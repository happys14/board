import json
from http.client import responses
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.tokens import default_token_generator
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout
from django.contrib.auth.views import PasswordResetView
from django.views.generic import (ListView, DetailView,
                                  CreateView, UpdateView, DeleteView, TemplateView)
from .forms import SignUpForm, AdsForm, ResponseForm
from .models import *

class AdsList(ListView):
    """Главная страница"""
    model = Ads
    ordering = '-date'
    template_name = 'main_paige.html'
    context_object_name = 'ads'     # Обращение к списку объектов в html-шаблоне
    paginate_by = 15

    def get_queryset(self):
        """Фильтрация по категориям"""
        queryset = super().get_queryset()
        category_id = self.request.GET.get('category')

        if category_id:
            queryset = queryset.filter(category__id=category_id)

        return queryset

    def get_context_data(self, **kwargs):
        """Добавление категорий в контекст для фильтрации"""
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()

        return context


class AdsDetail(DetailView):
    """Конкретное объявление"""
    model = Ads
    template_name = 'ads_detail.html'
    context_object_name = 'ad'

    def get_context_data(self, **kwargs):
        """Добавляем проверку на возможность редактирования"""
        context = super().get_context_data(**kwargs)
        context['can_edit'] = self.request.user.is_authenticated and self.object.can_edit(self.request.user)
        return context


from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, UpdateView
from .models import Ads
from .forms import AdsForm

class AdsCreate(LoginRequiredMixin, CreateView):
    """Создание объявления (авторизованный пользователь)"""
    model = Ads
    form_class = AdsForm
    template_name = 'ads_form.html'
    success_url = reverse_lazy('ads_list')

    def form_valid(self, form):
        """Автоматически добавляем автора"""
        form.instance.author = self.request.user
        return super().form_valid(form)

class AdsUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование автором только своего объявления"""
    model = Ads
    form_class = AdsForm  # Используем новую форму с множественным выбором категорий
    template_name = 'ads_form.html'

    def get_success_url(self):
        """Возвращает после на обновленное объявление"""
        return self.object.get_absolute_url()

    def test_func(self):
        """Проверка, является ли пользователь автором объявления"""
        ad = self.get_object()
        return self.request.user == ad.author


class AdsDelete(DeleteView, LoginRequiredMixin, UserPassesTestMixin):
    """Удаление автором ТОЛЬКО СВОЕГО объявление"""
    model = Ads
    template_name = 'ads_delete.html'
    success_url = reverse_lazy('ads_list')

    def is_creator(self):
        """Проверка авторства"""
        ad = self.get_object()
        return self.request.user == ad.author.author


# Далее: процесс регистрации с логикой верификации почты через код

import random
verification_codes = {}

def generate_verification_code():
    """Генерация 6-значного кода"""
    return str(random.randint(100000, 999999))


def signup(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]

            # Проверка, не зарегистрирован ли уже пользователь с таким email
            if User.objects.filter(email=email).exists():
                return render(request, 'registration/signup.html',
                              {'form': form, 'error': 'Пользователь с таким email уже существует'})

            # Генерация и отправка кода подтверждения
            verification_code = generate_verification_code()
            verification_codes[email] = {
                'code': verification_code,
                'data': form.cleaned_data  # Сохраняем введенные данные, но НЕ создаем пользователя
            }

            send_mail(
                subject='Код подтверждения email',
                message=f'Ваш код подтверждения: {verification_code}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email]
            )

            return render(request, 'registration/email_sent.html', {'email': email})
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})


def confirm_email(request):
    """Подтверждение email через одноразовый код и создание пользователя"""
    if request.method == 'POST':
        email = request.POST.get('email')
        code = request.POST.get('code')

        if email in verification_codes and verification_codes[email]['code'] == code:
            form_data = verification_codes[email]['data']

            # Создание пользователя
            user = User.objects.create_user(
                 # Используем email в качестве username
                email=email,
                password=form_data["password1"]
            )
            user.is_active = True  # Активируем аккаунт
            user.save()

            # Создание профиля с никнеймом
            Profile.objects.create(user=user, nickname=form_data["nickname"])

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            # Удаляем код после успешного подтверждения
            del verification_codes[email]

            return redirect('profile')
        else:
            return render(request, 'registration/email_sent.html', {'email': email, 'error': 'Неверный код'})

    return redirect('signup')


from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView
from django.shortcuts import render, redirect

@login_required
def profile(request):
    """Редактирование личного кабинета"""
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        profile.bio = request.POST.get('bio')

        # Обновление аватара, если загружен новый
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']

        profile.save()
        return redirect('profile')

    return render(request, 'registration/profile.html', {'profile': profile})


@login_required
def delete_account(request):
    """Удаление аккаунта пользователя"""
    user = request.user  # Получаем текущего пользователя

    if request.method == "POST":
        user.delete()  # Удаляем пользователя
        logout(request)  # Разлогиниваем после удаления
        return redirect('signup')  # Перенаправляем на страницу регистрации

    return render(request, 'registration/delete_account.html')


class UserProfileView(DetailView):
    """Страница профиля пользователя с его биографией и объявлениями"""
    model = User
    template_name = 'user_profile.html'
    context_object_name = 'profile_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = Profile.objects.get(user=self.object)  # Добавляем профиль
        context['ads'] = Ads.objects.filter(author=self.object).order_by('-date')  # Объявления пользователя
        return context


# Блок новостей

def news_list(request):
    news = News.objects.all().order_by('-date')
    pinned_news = news.filter(id=4)
    other_news = news.exclude(id=4)  # Все остальные

    paginator = Paginator(news, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'news_list.html', {
        'pinned_news': pinned_news.first(),  # Передаем 1 новость
        'page_obj': page_obj
    })


def news_detail(request, news_id):
    news_item = get_object_or_404(News, id=news_id)
    return render(request, 'news_detail.html',
                  {'news_item': news_item})


class CustomPasswordResetView(PasswordResetView):
    """Кастомная форма для сброса пароля"""
    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('password_reset_done')  # Оставаться на той же странице


class CustomSuccessView(TemplateView):
    """Статичная страничка - сообщение об отправленной на почту ссылке"""
    template_name = 'registration/msg.html'


# Функционал для создания отклика

@login_required
def create_response(request, ad_id):
    ad = get_object_or_404(Ads, id=ad_id)

    if request.method == 'POST':
        form = ResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.ad = ad
            response.user = request.user
            response.save()

            return redirect(ad.get_absolute_url())
    else:
        form = ResponseForm()

    return render(request, 'create_response.html',
                  {'form': form, 'ad': ad})


@login_required
def view_responses(request):
    # Фильтруем объявления текущего пользователя
    ads = Ads.objects.filter(author=request.user)

    # Если пользователь выбрал конкретное объявление, фильтруем отклики
    selected_ad_id = request.GET.get('ad_id')
    responses = Response.objects.filter(ad__author=request.user).order_by('-date_created')
    if selected_ad_id:
        responses = responses.filter(ad_id=selected_ad_id)

    return render(request, 'view_responses.html', {
        'ads': ads,
        'responses': responses,
        'selected_ad_id': int(selected_ad_id) if selected_ad_id else None
    })

@login_required
def accept_response(request, response_id):
    # Принятие отклика
    response = get_object_or_404(Response, id=response_id, ad__author=request.user)
    response.is_accepted = True
    response.save()

    # Отправка уведомления пользователю
    response.user.email_user(
        subject=f'Ваш отклик на "{response.ad.title}" принят!',
        message=f"Автор объявления: {response.ad.author.email}. Можете начать общение.",
        from_email=settings.DEFAULT_FROM_EMAIL
    )

    # Проверка на AJAX-запрос
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'accepted', 'response_id': response.id})

    return redirect('view_responses')

@login_required
def reject_response(request, response_id):
    # Получаем отклик, который нужно отклонить
    response = get_object_or_404(Response, id=response_id, ad__author=request.user)

    # Удаляем отклик
    response.delete()

    return redirect('view_responses')


from django.utils.timezone import activate

def set_timezone(request):
    """Сохранение временной зоны сессии"""
    if request.method == 'POST':
        data = json.loads(request.body)
        timezone = data.get('timezone', 'UTC')
        request.session['django_timezone'] = timezone
        activate(timezone)

        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'Invalid request'},
                        status=400)



