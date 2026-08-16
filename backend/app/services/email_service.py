import structlog
import smtplib
from email.message import EmailMessage
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

from app.core.config import settings
from app.core.exceptions import ValidationError

logger = structlog.get_logger(__name__)

class BaseEmailProvider(ABC):
    @abstractmethod
    async def send_email(self, recipient: str, subject: str, body: str) -> Dict[str, Any]:
        pass

class MockEmailProvider(BaseEmailProvider):
    async def send_email(self, recipient: str, subject: str, body: str) -> Dict[str, Any]:
        logger.info("mock_email_sent", recipient=recipient, subject=subject, body_length=len(body))
        
        return {
            "status": "success",
            "provider": "mock",
            "message": "Mock email successfully executed (no real email was sent)",
            "details": {
                "recipient": recipient,
                "subject": subject,
                "mode": "mock",
            }
        }

class SMTPEmailProvider(BaseEmailProvider):
    async def send_email(self, recipient: str, subject: str, body: str) -> Dict[str, Any]:
        if not all([settings.SMTP_HOST, settings.SMTP_PORT, settings.SMTP_USERNAME, settings.SMTP_PASSWORD, settings.SMTP_FROM]):
            raise ValueError("SMTP configuration is incomplete.")
            
        try:
            msg = EmailMessage()
            msg.set_content(body)
            msg['Subject'] = subject
            msg['From'] = settings.SMTP_FROM
            msg['To'] = recipient

            # Standard synchronous smtplib (for hackathon purposes, normally use aiosmtplib)
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(msg)
                
            return {
                "status": "success",
                "provider": "smtp",
                "message": "Email sent successfully",
            }
        except Exception as e:
            logger.error("smtp_send_failed", error=str(e))
            raise

def get_email_provider() -> BaseEmailProvider:
    if settings.EMAIL_MODE.lower() == "smtp":
        return SMTPEmailProvider()
    return MockEmailProvider()

async def send_email_action(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validates the payload and sends an email via the configured provider."""
    recipient = payload.get("recipient")
    subject = payload.get("subject")
    body = payload.get("body")
    
    if not recipient or "@" not in recipient:
        raise ValidationError("Valid 'recipient' is required.")
    if not subject:
        raise ValidationError("'subject' is required.")
    if not body:
        raise ValidationError("'body' is required.")
        
    provider = get_email_provider()
    return await provider.send_email(recipient, subject, body)
