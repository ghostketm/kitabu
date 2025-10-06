from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomUserLoginForm

def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('notes:note_list')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, f'Welcome {user.username}! Your account has been created.')
            return redirect('notes:note_list')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login(request):
    """Login view"""
    if request.method == 'POST':
        form = CustomUserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f'Welcome back {user.username}!')
            return redirect('notes:note_list')
    else:
        form = CustomUserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def profile(request):
    """User profile with premium status"""
    return render(request, 'accounts/profile.html', {
        'user': request.user,
        'note_count': request.user.notes.count(),
        'shared_note_count': request.user.shared_notes.count(),
    })