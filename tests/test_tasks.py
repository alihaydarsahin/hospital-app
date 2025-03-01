import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from app.tasks import (
    send_appointment_reminder,
    process_appointment_cancellation,
    generate_daily_report,
    cleanup_expired_tokens
)
from app.models.appointment import Appointment
from app.models.user import User

@pytest.fixture
def mock_send_email():
    with patch('app.tasks.send_email') as mock:
        yield mock

@pytest.fixture
def mock_send_sms():
    with patch('app.tasks.send_sms') as mock:
        yield mock

def test_appointment_reminder(test_appointment, mock_send_email, mock_send_sms):
    """Test appointment reminder task"""
    # Set appointment for tomorrow
    test_appointment.date = datetime.now().date() + timedelta(days=1)
    test_appointment.status = 'confirmed'
    
    # Run reminder task
    send_appointment_reminder()
    
    # Verify email was sent
    mock_send_email.assert_called_once()
    assert 'appointment reminder' in mock_send_email.call_args[0][0].lower()
    
    # Verify SMS was sent
    mock_send_sms.assert_called_once()
    assert 'reminder' in mock_send_sms.call_args[0][1].lower()

def test_appointment_cancellation(test_appointment, mock_send_email):
    """Test appointment cancellation task"""
    # Process cancellation
    process_appointment_cancellation(test_appointment.id)
    
    # Verify cancellation emails were sent
    assert mock_send_email.call_count == 2  # One for patient, one for doctor
    
    # Verify appointment status
    appointment = Appointment.query.get(test_appointment.id)
    assert appointment.status == 'cancelled'

def test_daily_report(test_appointment, mock_send_email):
    """Test daily report generation"""
    # Create some test appointments with different statuses
    test_appointment.status = 'completed'
    
    # Generate report
    generate_daily_report()
    
    # Verify report email was sent
    mock_send_email.assert_called_once()
    email_subject = mock_send_email.call_args[0][0]
    assert 'daily report' in email_subject.lower()
    
    # Verify report content
    email_body = mock_send_email.call_args[0][1]
    assert 'completed appointments' in email_body.lower()
    assert str(datetime.now().date()) in email_body

def test_cleanup_expired_tokens(test_user):
    """Test cleanup of expired password reset tokens"""
    # Create expired token
    test_user.reset_password_token = 'test_token'
    test_user.reset_password_token_expiry = datetime.now() - timedelta(days=2)
    
    # Run cleanup
    cleanup_expired_tokens()
    
    # Verify token was cleared
    user = User.query.get(test_user.id)
    assert user.reset_password_token is None
    assert user.reset_password_token_expiry is None

@patch('app.tasks.celery')
def test_periodic_task_scheduling(mock_celery):
    """Test periodic task scheduling"""
    from app.tasks import setup_periodic_tasks
    
    # Call setup function
    setup_periodic_tasks(mock_celery)
    
    # Verify tasks were scheduled
    assert mock_celery.add_periodic_task.call_count >= 3
    
    # Verify specific tasks
    scheduled_tasks = [call[0][1].name for call in mock_celery.add_periodic_task.call_args_list]
    assert 'send_appointment_reminder' in scheduled_tasks
    assert 'generate_daily_report' in scheduled_tasks
    assert 'cleanup_expired_tokens' in scheduled_tasks

def test_reminder_no_duplicate(test_appointment, mock_send_email):
    """Test that reminders aren't sent multiple times"""
    # Set appointment for tomorrow
    test_appointment.date = datetime.now().date() + timedelta(days=1)
    test_appointment.status = 'confirmed'
    test_appointment.reminder_sent = True
    
    # Run reminder task
    send_appointment_reminder()
    
    # Verify no email was sent
    mock_send_email.assert_not_called()

def test_report_error_handling(mock_send_email):
    """Test error handling in report generation"""
    # Simulate database error
    with patch('app.models.appointment.Appointment.query') as mock_query:
        mock_query.filter.side_effect = Exception('Database error')
        
        # Generate report should not raise exception
        generate_daily_report()
        
        # Verify error email was sent
        mock_send_email.assert_called_once()
        assert 'error' in mock_send_email.call_args[0][0].lower() 