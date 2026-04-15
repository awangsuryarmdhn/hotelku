"""
Accounts Views — Login, Logout, Profile management.
"""
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View

from .forms import LoginForm


class LoginView(View):
    """Handle staff login."""

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:index')
        form = LoginForm()
        return render(request, 'accounts/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', '/')
                return redirect(next_url)
            else:
                form.add_error(None, 'Username atau password salah. Silakan coba lagi.')
        return render(request, 'accounts/login.html', {'form': form})


class LogoutView(View):
    """Handle staff logout."""

    def post(self, request):
        logout(request)
        return redirect('accounts:login')

    def get(self, request):
        logout(request)
        return redirect('accounts:login')


class ProfileView(LoginRequiredMixin, View):
    """View and edit current user profile."""

    def get(self, request):
        return render(request, 'accounts/profile.html')
