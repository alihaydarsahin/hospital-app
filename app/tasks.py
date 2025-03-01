from app import celery, db
from app.models.appointment import Appointment
from app.utils.notifications import send_email, send_sms
from datetime import datetime, timedelta
from flask import current_app, render_template
from apscheduler.triggers.cron import CronTrigger

@celery.task
def send_appointment_reminder():
    """Send reminders for tomorrow's appointments"""
    tomorrow = datetime.now().date() + timedelta(days=1)
    appointments = Appointment.query.filter(
        Appointment.appointment_date == tomorrow,
        Appointment.status == 'confirmed'
    ).all()
    
    for appointment in appointments:
        # Email notification
        subject = "Appointment Reminder"
        template = render_template(
            'email/appointment_reminder.html',
            appointment=appointment
        )
        send_email(appointment.patient.email, subject, template)
        
        # SMS notification if phone number exists
        if appointment.patient.phone:
            message = (
                f"Reminder: You have an appointment tomorrow at "
                f"{appointment.appointment_time.strftime('%H:%M')} with "
                f"Dr. {appointment.doctor.user.full_name}"
            )
            send_sms.delay(appointment.patient.phone, message)

@celery.task
def process_appointment_cancellation(appointment_id):
    """Process appointment cancellation and notify relevant parties"""
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return
    
    # Email to patient
    subject = "Appointment Cancellation Confirmation"
    template = render_template(
        'email/appointment_cancelled.html',
        appointment=appointment
    )
    send_email(appointment.patient.email, subject, template)
    
    # Email to doctor
    subject = "Patient Appointment Cancellation"
    template = render_template(
        'email/doctor_appointment_cancelled.html',
        appointment=appointment
    )
    send_email(appointment.doctor.user.email, subject, template)

@celery.task
def generate_daily_report():
    """Generate daily appointment report"""
    today = datetime.now().date()
    appointments = Appointment.query.filter(
        Appointment.appointment_date == today
    ).all()
    
    # Generate report data
    report_data = {
        'total_appointments': len(appointments),
        'completed': sum(1 for a in appointments if a.status == 'completed'),
        'cancelled': sum(1 for a in appointments if a.status == 'cancelled'),
        'no_show': sum(1 for a in appointments if a.status == 'no_show'),
        'appointments': appointments
    }
    
    # Send report to admin
    subject = f"Daily Appointment Report - {today.strftime('%Y-%m-%d')}"
    template = render_template(
        'email/daily_report.html',
        data=report_data,
        date=today
    )
    send_email(current_app.config['ADMIN_EMAIL'], subject, template)

@celery.task
def cleanup_expired_tokens():
    """Clean up expired password reset tokens"""
    from app.models.user import User
    threshold = datetime.utcnow() - timedelta(days=1)
    
    User.query.filter(User.reset_password_token_expiry < threshold).update({
        'reset_password_token': None,
        'reset_password_token_expiry': None
    })
    
    db.session.commit()

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Setup periodic task schedule"""
    # Send appointment reminders daily at 10:00 AM
    sender.add_periodic_task(
        CronTrigger.from_crontab('0 10 * * *'),
        send_appointment_reminder.s(),
        name='daily-appointment-reminders'
    )
    
    # Generate daily report at 23:59
    sender.add_periodic_task(
        CronTrigger.from_crontab('59 23 * * *'),
        generate_daily_report.s(),
        name='daily-appointment-report'
    )
    
    # Clean up expired tokens daily at 00:00
    sender.add_periodic_task(
        CronTrigger.from_crontab('0 0 * * *'),
        cleanup_expired_tokens.s(),
        name='cleanup-expired-tokens'
    ) 