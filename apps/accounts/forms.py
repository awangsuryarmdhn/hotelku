"""
Accounts Forms — Login and profile forms.
"""
from django import forms


class LoginForm(forms.Form):
    """Staff login form."""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Masukkan username Anda',
            'autofocus': True,
            'id': 'login-username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Masukkan password Anda',
            'id': 'login-password',
        })
    )
