from flask import current_app
from flask_mail import Message
from app import mail, celery
import requests
from datetime import datetime

def send_email(to, subject, template):
    """Send email function"""
    try:
        msg = Message(
            subject,
            recipients=[to],
            html=template,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending email: {str(e)}")
        return False

@celery.task
def send_sms(phone_number, message):
    """Send SMS function"""
    try:
        # SMS API configuration
        api_key = current_app.config['SMS_API_KEY']
        sender_id = current_app.config['SMS_SENDER_ID']
        
        # API request
        response = requests.post(
            'https://api.sms-provider.com/send',
            json={
                'api_key': api_key,
                'sender_id': sender_id,
                'phone': phone_number,
                'message': message
            },
            timeout=5
        )
        
        if response.status_code == 200:
            current_app.logger.info(f"SMS sent successfully to: {phone_number}")
            return True
        else:
            current_app.logger.error(f"SMS sending error: {response.text}")
            return False
            
    except Exception as e:
        current_app.logger.error(f"SMS sending error: {str(e)}")
        return False

def send_welcome_email(user):
    """Send welcome email to newly registered user"""
    template = f"""
    <h1>Welcome to Hospital Management System</h1>
    <p>Dear {user.full_name},</p>
    <p>Thank you for registering with our hospital management system. 
    We're excited to have you as a member of our community.</p>
    <p>You can now log in to your account and start using our services.</p>
    <p>Best regards,<br>Hospital Management Team</p>
    """
    return send_email(
        to=user.email,
        subject="Welcome to Hospital Management System",
        template=template
    )

def send_appointment_notification(appointment, is_confirmation=False, is_cancellation=False):
    """Randevu ile ilgili bildirimleri gönderir"""
    # Email bildirimi
    if is_confirmation:
        subject = "Randevu Onaylandı"
        template = f"""
        <h2>Randevunuz Onaylandı</h2>
        <p>Sayın {appointment.patient.get_full_name()},</p>
        <p>{appointment.date.strftime('%d.%m.%Y')} tarihinde saat {appointment.time.strftime('%H:%M')}'deki 
        randevunuz Dr. {appointment.doctor.get_full_name()} tarafından onaylanmıştır.</p>
        <p>Randevu detayları için sisteme giriş yapabilirsiniz.</p>
        """
    elif is_cancellation:
        subject = "Randevu İptali"
        template = f"""
        <h2>Randevunuz İptal Edildi</h2>
        <p>Sayın {appointment.patient.get_full_name()},</p>
        <p>{appointment.date.strftime('%d.%m.%Y')} tarihinde saat {appointment.time.strftime('%H:%M')}'deki 
        randevunuz iptal edilmiştir.</p>
        <p>Yeni bir randevu almak için sisteme giriş yapabilirsiniz.</p>
        """
    else:
        subject = "Yeni Randevu Oluşturuldu"
        template = f"""
        <h2>Randevunuz Oluşturuldu</h2>
        <p>Sayın {appointment.patient.get_full_name()},</p>
        <p>{appointment.date.strftime('%d.%m.%Y')} tarihinde saat {appointment.time.strftime('%H:%M')} için 
        Dr. {appointment.doctor.get_full_name()} ile randevunuz oluşturulmuştur.</p>
        <p>Randevu detayları için sisteme giriş yapabilirsiniz.</p>
        """
    
    send_email(to=appointment.patient.email, subject=subject, template=template)
    
    # SMS bildirimi
    if appointment.patient.phone:
        message = f"Randevunuz {'onaylandı' if is_confirmation else 'iptal edildi' if is_cancellation else 'oluşturuldu'}. "
        message += f"Tarih: {appointment.date.strftime('%d.%m.%Y')}, Saat: {appointment.time.strftime('%H:%M')}"
        send_sms.delay(appointment.patient.phone, message)

def send_password_reset_email(user, token):
    """Şifre sıfırlama emaili gönderir"""
    subject = "Şifre Sıfırlama - Hastane Randevu Sistemi"
    reset_url = f"{current_app.config['BASE_URL']}/reset-password/{token}"
    template = f"""
    <h2>Şifre Sıfırlama</h2>
    <p>Sayın {user.get_full_name()},</p>
    <p>Şifrenizi sıfırlamak için aşağıdaki bağlantıya tıklayın:</p>
    <p><a href="{reset_url}">{reset_url}</a></p>
    <p>Bu bağlantı 1 saat süreyle geçerlidir.</p>
    <p>Eğer şifre sıfırlama talebinde bulunmadıysanız, bu emaili dikkate almayın.</p>
    <br>
    <p>Saygılarımızla,</p>
    <p>Hastane Randevu Sistemi Ekibi</p>
    """
    return send_email(to=user.email, subject=subject, template=template)

def send_appointment_reminder():
    """24 saat içindeki randevular için hatırlatma gönderir"""
    from app.models.appointment import Appointment
    
    tomorrow = datetime.now().date()
    appointments = Appointment.query.filter_by(
        date=tomorrow,
        status='confirmed'
    ).all()
    
    for appointment in appointments:
        # Email bildirimi
        subject = "Randevu Hatırlatması"
        template = f"""
        <h2>Randevu Hatırlatması</h2>
        <p>Sayın {appointment.patient.get_full_name()},</p>
        <p>Yarın ({appointment.date.strftime('%d.%m.%Y')}) saat {appointment.time.strftime('%H:%M')}'de 
        Dr. {appointment.doctor.get_full_name()} ile randevunuz bulunmaktadır.</p>
        <p>Randevunuza zamanında gelmenizi rica ederiz.</p>
        """
        send_email(to=appointment.patient.email, subject=subject, template=template)
        
        # SMS bildirimi
        if appointment.patient.phone:
            message = f"Hatırlatma: Yarın saat {appointment.time.strftime('%H:%M')}'de "
            message += f"Dr. {appointment.doctor.get_full_name()} ile randevunuz bulunmaktadır."
            send_sms.delay(appointment.patient.phone, message) 