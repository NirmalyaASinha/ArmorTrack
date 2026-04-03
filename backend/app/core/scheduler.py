from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from app.core.database import sql1_db
from app.core.config import settings

scheduler = BackgroundScheduler()


def check_maintenance_due():
    """Daily check for assets due for maintenance"""
    try:
        print(f"[{datetime.utcnow()}] Running maintenance check...")
        
        assets = sql1_db.get_client().table("assets").select("*").execute()
        
        for asset in assets.data:
            last_serviced = asset.get("last_serviced_at")
            interval_days = asset.get("service_interval_days", 90)
            
            if last_serviced:
                last_serviced_dt = datetime.fromisoformat(last_serviced.replace('Z', '+00:00'))
                next_service = last_serviced_dt + timedelta(days=interval_days)
                days_until_due = (next_service - datetime.utcnow()).days
                
                if days_until_due <= settings.MAINTENANCE_WARNING_DAYS:
                    # Create alert
                    severity = "CRITICAL" if days_until_due < 0 else "WARNING"
                    alert = {
                        "type": "MAINTENANCE_DUE",
                        "severity": severity,
                        "message": f"Asset {asset['asset_name']} ({asset['id']}) {'OVERDUE' if days_until_due < 0 else 'due soon'} for maintenance",
                        "asset_id": asset["id"],
                        "timestamp": datetime.utcnow().isoformat(),
                        "dismissed": False
                    }
                    sql1_db.get_client().table("alerts").insert(alert).execute()
                    print(f"  Alert created for asset: {asset['id']}")
        
        print(f"[{datetime.utcnow()}] Maintenance check completed")
    
    except Exception as e:
        print(f"Maintenance check failed: {str(e)}")


def check_active_alerts():
    """Periodic check for active alerts"""
    try:
        # Get active IN_TRANSIT batches
        batches = sql1_db.get_client().table("batches") \
            .select("id") \
            .eq("status", "IN_TRANSIT") \
            .execute()
        
        for batch in batches.data:
            # Check for GPS signal loss
            latest_gps = sql1_db.get_client().table("gps_tracking") \
                .select("timestamp") \
                .eq("batch_id", batch["id"]) \
                .order("timestamp", desc=True) \
                .limit(1) \
                .execute()
            
            if latest_gps.data:
                last_update = datetime.fromisoformat(latest_gps.data[0]["timestamp"])
                time_since_update = (datetime.utcnow() - last_update).total_seconds() / 60
                
                if time_since_update > settings.GPS_SIGNAL_LOSS_MINUTES:
                    # Check if alert already exists
                    existing_alert = sql1_db.get_client().table("alerts") \
                        .select("id") \
                        .eq("batch_id", batch["id"]) \
                        .eq("type", "GPS_SIGNAL_LOSS") \
                        .eq("dismissed", False) \
                        .execute()
                    
                    if not existing_alert.data:
                        alert = {
                            "type": "GPS_SIGNAL_LOSS",
                            "severity": "ALERT",
                            "message": f"GPS signal lost for batch {batch['id']} for over {settings.GPS_SIGNAL_LOSS_MINUTES} minutes",
                            "batch_id": batch["id"],
                            "timestamp": datetime.utcnow().isoformat(),
                            "dismissed": False
                        }
                        sql1_db.get_client().table("alerts").insert(alert).execute()
                        print(f"  GPS signal loss alert for batch: {batch['id']}")
        
    except Exception as e:
        print(f"Alert check failed: {str(e)}")


def start_scheduler():
    """Start the background scheduler"""
    print("Initializing scheduler...")
    
    # Daily maintenance check at midnight
    scheduler.add_job(
        check_maintenance_due,
        CronTrigger(hour=0, minute=0),
        id='maintenance_check',
        replace_existing=True
    )
    
    # Check alerts every 5 minutes
    scheduler.add_job(
        check_active_alerts,
        'interval',
        minutes=5,
        id='alert_check',
        replace_existing=True
    )
    
    scheduler.start()
    print("Scheduler started successfully")
    
    return scheduler


def stop_scheduler():
    """Stop the background scheduler"""
    print("Stopping scheduler...")
    scheduler.shutdown()
    print("Scheduler stopped")
