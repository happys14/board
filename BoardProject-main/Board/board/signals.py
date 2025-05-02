from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import News, User

@receiver(post_save, sender=News)
def send_news_email(sender, instance, created, **kwargs):
    """Отправляет email всем пользователям при создании новой новости"""
    if created:  # Проверяем, что новость только что создана

        users = User.objects.all()
        recipient_list = [user.email for user in users if user.email]

        subject = f'Свежая новость на Доске объявлений!'
        message = f'Приветствую!\n\nОпубликована новая новость: "{instance.title}".\n\n' \
                  f'Подробнее: {settings.SITE_URL}{instance.get_absolute_url()}'

        from_email = settings.DEFAULT_FROM_EMAIL
        send_mail(subject, message, from_email, recipient_list,
                  fail_silently=False)
