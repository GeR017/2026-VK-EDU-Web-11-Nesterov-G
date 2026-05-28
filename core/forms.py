from django import forms
from django.contrib.auth.models import User
from django.db.models import Model
from django.forms import ModelForm

from .models import Profile


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


    def clean_username(self):
        cleaned_data = super().clean()
        if self.cleaned_data.get('username')[0] == 'b':
            raise forms.ValidationError('Error')
        return  self.cleaned_data.get('username')

class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirmation = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data['password'] != cleaned_data['password_confirmation']:
            raise forms.ValidationError('Passwords do not match')
    def save(self, commit=True):
        user = super().save(commit=commit)
        user.set_password(self.cleaned_data['password'])
        user.save()

        Profile.objects.create(user=user)

        return user

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username','email')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar',)

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')

        if not avatar:
            return avatar

        #Возможность добавить кастомный метод проверки на плохой контент
        is_inappropriate = False

        if is_inappropriate:
            raise forms.ValidationError(
                "Изображение не прошло модерацию."
            )

        return avatar


