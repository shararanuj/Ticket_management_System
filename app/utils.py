from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags
from django.template.loader import render_to_string

def send_notification_email(subject, message, recipient_list):
    send_mail(
        subject,
        strip_tags(message),
        settings.EMAIL_HOST_USER,
        recipient_list,
        html_message=message,
    )
