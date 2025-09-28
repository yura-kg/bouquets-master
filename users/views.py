from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.conf import settings
from django.utils import timezone
from .models import CustomUser
from .forms import CustomUserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate until email confirmation
            user.confirmation_token = get_random_string(50)
            user.confirmation_sent_at = timezone.now()
            user.save()
            
            # Send confirmation email
            confirmation_url = request.build_absolute_uri(
                f'/confirm-email/{user.confirmation_token}/'
            )
            send_mail(
                'Подтверждение email - БукетМастер',
                f'Для подтверждения email перейдите по ссылке: {confirmation_url}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            messages.success(
                request, 
                'Регистрация успешна! Проверьте вашу почту для подтверждения email.'
            )
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def confirm_email(request, token):
    try:
        user = CustomUser.objects.get(confirmation_token=token)
        user.is_confirmed = True
        user.is_active = True
        user.confirmation_token = None
        user.save()
        messages.success(request, 'Email успешно подтвержден! Теперь вы можете войти.')
    except CustomUser.DoesNotExist:
        messages.error(request, 'Неверная ссылка подтверждения.')
    return redirect('login')

def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None and user.is_confirmed:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Неверные данные или email не подтвержден.')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def dashboard(request):
    return render(request, 'users/dashboard.html')
