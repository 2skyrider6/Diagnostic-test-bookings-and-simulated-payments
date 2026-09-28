import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.core.config import settings

class EmailService:
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER if hasattr(settings, 'SMTP_SERVER') else "localhost"
        self.smtp_port = settings.SMTP_PORT if hasattr(settings, 'SMTP_PORT') else 587
        self.sender_email = settings.SENDER_EMAIL if hasattr(settings, 'SENDER_EMAIL') else "noreply@diagnosticbooking.com"
        self.sender_password = settings.SENDER_PASSWORD if hasattr(settings, 'SENDER_PASSWORD') else ""
    
    async def send_booking_confirmation(self, user_email: str, user_name: str, booking_details: dict):
        """Send booking confirmation email"""
        subject = "Booking Confirmation - Diagnostic Test Booking Service"
        
        body = f"""
        Hello {user_name},
        
        Your diagnostic test booking has been confirmed!
        
        Booking Details:
        - Test: {booking_details.get('test_name', 'N/A')}
        - Centre: {booking_details.get('centre_name', 'N/A')}
        - Appointment: {booking_details.get('appointment_datetime', 'N/A')}
        - Amount: ${booking_details.get('amount', '0.00')}
        - Booking ID: {booking_details.get('booking_id', 'N/A')}
        
        Please arrive 15 minutes before your appointment time.
        
        Thank you for using our service!
        
        Best regards,
        Diagnostic Booking Service Team
        """
        
        return await self._send_email(user_email, subject, body)
    
    async def send_booking_reminder(self, user_email: str, user_name: str, booking_details: dict):
        """Send booking reminder email"""
        subject = "Reminder: Your Diagnostic Test Appointment Tomorrow"
        
        body = f"""
        Hello {user_name},
        
        This is a reminder that you have a diagnostic test appointment tomorrow:
        
        Appointment Details:
        - Test: {booking_details.get('test_name', 'N/A')}
        - Centre: {booking_details.get('centre_name', 'N/A')}
        - Appointment: {booking_details.get('appointment_datetime', 'N/A')}
        - Booking ID: {booking_details.get('booking_id', 'N/A')}
        
        Please arrive 15 minutes before your appointment time.
        
        If you need to reschedule or cancel, please contact us at least 2 hours in advance.
        
        Best regards,
        Diagnostic Booking Service Team
        """
        
        return await self._send_email(user_email, subject, body)
    
    async def _send_email(self, recipient_email: str, subject: str, body: str) -> bool:
        """Send email via SMTP"""
        try:
            # Create message
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = recipient_email
            message["Subject"] = subject
            
            # Add body to email
            message.attach(MIMEText(body, "plain"))
            
            # Create secure connection and send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                text = message.as_string()
                server.sendmail(self.sender_email, recipient_email, text)
            
            return True
        except Exception as e:
            # In a real application, you would log this error
            print(f"Failed to send email: {e}")
            return False

# Create singleton instance
email_service = EmailService()