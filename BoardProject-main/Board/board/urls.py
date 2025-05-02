from django.urls import path
from .views import *
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView, \
    PasswordResetCompleteView

urlpatterns = [
    path('', AdsList.as_view(), name='ads_list'),
    path('ads/<int:pk>/', AdsDetail.as_view(), name='ads_detail'),
    path('ads/create/', AdsCreate.as_view(), name='ads_create'),
    path('ads/<int:pk>/edit/', AdsUpdate.as_view(), name='ads_edit'),
    path('ads/<int:pk>/delete/', AdsDelete.as_view(), name='ads_delete'),

    # Регистрация, подтверждение
    path('signup/', signup, name='signup'),
    path('confirm/', confirm_email, name='confirm_email'),

    # Личный кабинет и публичный профиль пользователя
    path('profile/', profile, name='profile'),
    path('profile/<int:pk>/', UserProfileView.as_view(), name='user_profile'),

    # Блок новостей
    path('news/', news_list, name='news_list'),
    path('news/<int:news_id>/', news_detail, name='news_detail'),


    # Вход и выход, удаление аккаунта
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('delete_account/', delete_account, name='delete_account'),

    # Процесс восстановление пароля

    path(
        'password_reset/',
        CustomPasswordResetView.as_view(
            template_name='registration/password_reset_form.html',
            email_template_name='registration/password_reset_email.html',
            success_url=reverse_lazy('password_reset_done')
        ), name='password_reset'),
    path('msg/', TemplateView.as_view(template_name='registration/msg.html'), name='password_reset_done'),

    # Страница сброса пароля
    path('reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             success_url='/password_reset_complete/'
         ),
         name='password_reset_confirm'),

    # Страница успешного сброса
    path('password_reset_complete/',
         PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),

    # Функционал откликов
    path('ads/<int:ad_id>/response/', create_response, name='create_response'),
    path('responses/', view_responses, name='view_responses'),
    path('responses/accept/<int:response_id>/', accept_response, name='accept_response'),
    path('responses/reject/<int:response_id>/', reject_response, name='reject_response'),

    # Временная локализация
    path("set_timezone/", set_timezone, name="set_timezone"),
]


