
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Profile, Category, Ads, Response
from django.core.exceptions import ValidationError


class SignUpForm(UserCreationForm):
    """Форма регистрации"""
    email = forms.EmailField(
        required=True,
        label="Email",
    )
    nickname = forms.CharField(
        max_length=50,
        required=True,
        label="Никнейм",
        help_text="Обязательное поле.\nВпоследствии вы не сможете его изменить.",
    )

    class Meta:
        model = User
        fields = ['email', 'nickname', 'password1', 'password2']

    def clean_nickname(self):
        """Проверка уникальности никнейма"""
        nickname = self.cleaned_data.get("nickname")

        if Profile.objects.filter(nickname=nickname).exists():
            raise ValidationError("Этот никнейм уже занят. Выберите другой.")

        return nickname

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Profile.objects.create(user=user, nickname=self.cleaned_data["nickname"])
        return user


class ProfileForm(forms.ModelForm):
    """Редактирование профиля в ЛК"""
    class Meta:
        model = Profile
        fields = ['bio']
        labels = {
            'bio': 'О себе',
        }


class AdsForm(forms.ModelForm):
    """Форма создания объявления"""

    # Если захочется выбрать несколько категорий
    # category = forms.ModelMultipleChoiceField(
    #     queryset=Category.objects.all(),
    #     widget=forms.CheckboxSelectMultiple,
    #     label="Категории"
    # )

    class Meta:
        model = Ads
        fields = ['title', 'category', 'content', 'video']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field in self.fields:
                self.fields[field].widget.attrs.update({'class': 'form-control', 'autocomplete': 'off'})

            self.fields['content'].widget.attrs.update({'class': 'form-control django_ckeditor_5'})


class ResponseForm(forms.ModelForm):
    """Форма для написания отклика"""
    class Meta:
        model = Response
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': 'Введите текст отклика...'}),
        }
        labels = {
            'text': 'Текст отклика',
        }