"""
Email Service - Send notifications and alerts
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
from config import Config

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications"""
    
    def __init__(self):
        self.smtp_server = Config.SMTP_SERVER if hasattr(Config, 'SMTP_SERVER') else "smtp.gmail.com"
        self.smtp_port = Config.SMTP_PORT if hasattr(Config, 'SMTP_PORT') else 587
        self.smtp_username = Config.SMTP_USERNAME if hasattr(Config, 'SMTP_USERNAME') else None
        self.smtp_password = Config.SMTP_PASSWORD if hasattr(Config, 'SMTP_PASSWORD') else None
        self.from_email = Config.FROM_EMAIL if hasattr(Config, 'FROM_EMAIL') else "prometheus@example.com"
        self.enabled = bool(self.smtp_username and self.smtp_password)
        
        if not self.enabled:
            logger.warning("Email service disabled: SMTP credentials not configured")
    
    def send_email(self, to_email: str, subject: str, body: str, html: bool = False) -> bool:
        """
        Send an email
        
        Args:
            to_email: Recipient email
            subject: Email subject
            body: Email body
            html: Whether body is HTML
        
        Returns:
            Success status
        """
        if not self.enabled:
            logger.warning("Email sending disabled")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Attach body
            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent to {to_email}: {subject}")
            return True
        
        except Exception as e:
            logger.error(f"Email send error: {e}")
            return False
    
    def send_funding_alert(self, user_email: str, startup_data: Dict) -> bool:
        """
        Send funding alert email
        
        Args:
            user_email: Recipient email
            startup_data: Startup information dict
        """
        subject = f"🚀 Funding Alert: {startup_data.get('company', 'Unknown')} raised {startup_data.get('amount', 'Unknown')}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #4CAF50;">New Funding Alert!</h2>
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;">
                <p><strong>Company:</strong> {startup_data.get('company', 'Unknown')}</p>
                <p><strong>Amount:</strong> {startup_data.get('amount', 'Unknown')}</p>
                <p><strong>Sector:</strong> {startup_data.get('sector', 'Unknown')}</p>
                <p><strong>Location:</strong> {startup_data.get('city', 'Unknown')}, {startup_data.get('state', 'Unknown')}</p>
                {f"<p><strong>Investors:</strong> {startup_data.get('investors', 'Not disclosed')}</p>" if startup_data.get('investors') else ''}
                <p><strong>Date:</strong> {startup_data.get('date', 'Unknown')}</p>
            </div>
            <p style="margin-top: 20px; color: #666;">
                This is an automated alert from Prometheus RAG System.
            </p>
        </body>
        </html>
        """
        
        return self.send_email(user_email, subject, html_body, html=True)
    
    def send_weekly_report(self, user_email: str, stats: Dict) -> bool:
        """
        Send weekly analytics report
        
        Args:
            user_email: Recipient email
            stats: User statistics dict
        """
        subject = "📊 Your Weekly Prometheus Report"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #2196F3;">Your Weekly Activity Report</h2>
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;">
                <p><strong>Total Queries:</strong> {stats.get('total_queries', 0)}</p>
                <p><strong>Average Response Time:</strong> {stats.get('avg_response_time', 0)}s</p>
                <p><strong>Cached Queries:</strong> {stats.get('cached_queries', 0)} ({stats.get('cache_hit_rate', 0)}%)</p>
                <p><strong>Preferred Language:</strong> {stats.get('preferred_language', 'en')}</p>
            </div>
            <p style="margin-top: 20px;">
                Keep exploring startup funding data with Prometheus!
            </p>
        </body>
        </html>
        """
        
        return self.send_email(user_email, subject, html_body, html=True)
    
    def send_welcome_email(self, user_email: str, username: str) -> bool:
        """
        Send welcome email to new users
        
        Args:
            user_email: User email
            username: Username
        """
        subject = "Welcome to Prometheus RAG System! 🎉"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #4CAF50;">Welcome to Prometheus, {username}!</h2>
            <p>Thank you for joining Prometheus RAG System - your multilingual startup funding intelligence platform.</p>
            
            <h3>What you can do:</h3>
            <ul>
                <li>Query 23,000+ Indian startup funding records</li>
                <li>Get insights in 8 Indian languages</li>
                <li>Voice search with Whisper AI</li>
                <li>Track funding trends and patterns</li>
            </ul>
            
            <p style="margin-top: 20px;">
                Start exploring now and discover the startup ecosystem!
            </p>
            
            <p style="color: #666; font-size: 12px; margin-top: 30px;">
                Need help? Reply to this email or visit our documentation.
            </p>
        </body>
        </html>
        """
        
        return self.send_email(user_email, subject, html_body, html=True)
    
    def send_batch_emails(self, recipients: List[str], subject: str, body: str, html: bool = False) -> int:
        """
        Send emails to multiple recipients
        
        Returns:
            Number of successfully sent emails
        """
        success_count = 0
        for email in recipients:
            if self.send_email(email, subject, body, html):
                success_count += 1
        
        logger.info(f"Sent {success_count}/{len(recipients)} emails successfully")
        return success_count


# Global email service instance
email_service = EmailService()
