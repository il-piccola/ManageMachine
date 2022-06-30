from django import forms
from ManageMachine.models import *

class LoginForm(forms.Form) :
    user = forms.CharField(
        widget=forms.TextInput(attrs={'class':'login'}),
        label='ユーザIDまたはメールアドレス'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class':'login'}),
        label='パスワード'
    )
    def clean_user(self) :
        user = self.cleaned_data['user']
        iusers = User.objects.filter(userid=user)
        eusers = User.objects.filter(email=user)
        if (not (iusers|eusers).exists()) :
            raise forms.ValidationError('ユーザー名が間違っています。')
        return user
    def clean_password(self) :
        password = self.cleaned_data['password']
        if ('user' in self.cleaned_data) :
            user = self.cleaned_data['user']
            iusers = User.objects.filter(userid=user)
            eusers = User.objects.filter(email=user)
            if (not (iusers|eusers).filter(password=password).exists()) :
                raise forms.ValidationError('パスワードが間違っています。')
        return password
