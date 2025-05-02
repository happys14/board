from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django_ckeditor_5.fields import CKEditor5Field


class Category(models.Model):
    category = models.CharField(max_length=30, unique=True,
                                verbose_name='Категория')

    def __str__(self):
        return self.category


class Ads(models.Model):
    """Модель объявления, текст и изображения через ckeditor"""
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Автор')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    category = models.ManyToManyField(Category, through='AdsCategory', verbose_name='Категория')
    title = models.CharField(max_length=150, verbose_name='Заголовок')
    content = CKEditor5Field(verbose_name='Содержание новости')
    video = models.FileField(upload_to='ads_videos/', blank=True, null=True, verbose_name='Видео')

    def __str__(self):
        return self.title

    def preview(self):
        return f"{self.content[:300]}..." if len(self.content) > 300 else self.content

    def get_absolute_url(self):
        return reverse('ads_detail', args=[str(self.id)])

    def can_edit(self, user):
        return self.author == user


class AdsCategory(models.Model):
    ads = models.ForeignKey(Ads, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class UserManager(BaseUserManager):
    """Менеджер пользователей для кастомной модели User"""
    def create_user(self, email, password=None, **extra_fields):
        """Создание обычного пользователя"""
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Создание стафа (на случай, если захочется расширить для него
         права доступа) и суперпользователя"""
        extra_fields.setdefault('is_staff', True)  # доступ в админку
        extra_fields.setdefault('is_superuser', True)  # полный доступ

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Кастомная модель пользователя, который одновременно является автором"""
    username = None  # Убираем стандартный username
    email = models.EmailField(unique=True)  # Email как основной логин
    is_staff = models.BooleanField(default=False)  # Доступ в админку
    is_superuser = models.BooleanField(default=False)  # Полный доступ

    objects = UserManager()  # Подключаем кастомный менеджер

    USERNAME_FIELD = 'email'  # Логинимся по email
    REQUIRED_FIELDS = []  # Django больше не требует username

    def __str__(self):
        return self.email


class Profile(models.Model):
    """Профиль пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Никнейм'
    )
    bio = models.TextField(blank=True, verbose_name='Биография')
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', verbose_name='Аватар')

    def __str__(self):
        return self.nickname


class News(models.Model):
    """Модель новостей, публикуемых ТОЛЬКО АДМИНОМ"""
    title = models.CharField(max_length=250, verbose_name='Заголовок')
    content = CKEditor5Field(verbose_name='Содержание новости', default='')
    date = models.DateTimeField(auto_now_add=True,
                                verbose_name='Дата публикации')

    class Meta:
        ordering = ['-date']
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('news_detail', args=[str(self.id)])


class Response(models.Model):
    """Модель откликов"""
    ad = models.ForeignKey(Ads, on_delete=models.CASCADE,
                           related_name='responses', verbose_name='Отклики')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             verbose_name='Пользователь')
    text = models.TextField(verbose_name='Текст отклика')
    date_created = models.DateTimeField(auto_now_add=True,
                                        verbose_name='Дата создания')
    is_accepted = models.BooleanField(default=False, verbose_name='Принят')

    class Meta:
        verbose_name = 'Отклик'
        verbose_name_plural = 'Отклики'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Отправка уведомления автору о новом отклике
        subject = f'Новый отклик на Доске объявлений'
        message = (f'На ваше объявление "{self.ad.title}".\n'
                   f'Содержание отклика: {self.text[:150]}\n'
                   '❗️Проверьте личный кабинет❗')
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [self.ad.author.email]

        send_mail(subject, message, from_email, recipient_list)
