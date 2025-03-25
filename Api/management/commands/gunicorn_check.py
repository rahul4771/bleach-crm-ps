import subprocess
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = "Monitor Gunicorn and send an email if it stops"

    def handle(self, *args, **kwargs):
        ALERT_EMAILS = [
            "jishin.cheruvattil@slots.com.kw",
            "mahenth.vasudev@slots.com.kw"
        ]

        if not self.is_gunicorn_running():
            self.send_alert(ALERT_EMAILS)

    def is_gunicorn_running(self):
        """Check if Gunicorn is running."""
        try:
            subprocess.check_output(["pgrep", "-f", "gunicorn"], text=True)
            return True  # Gunicorn is running
        except subprocess.CalledProcessError:
            return False  # Gunicorn is not running

    def send_alert(self, recipients):
        """Send an email alert when Gunicorn stops."""
        send_mail(
            subject="Gunicorn Stopped!",
            message="Alert: Gunicorn has stopped on your server! Please check immediately.",
            from_email='notification@bleach-kw.com',
            recipient_list=recipients,
            fail_silently=False,
        )
