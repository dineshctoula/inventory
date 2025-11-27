from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dairyapp:index')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        
        if email and password:
            user = authenticate(request, username=email, password=password, email=email)

            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name() or user.email}!')
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('dairyapp:index')
            else:
                messages.error(request, 'Invalid email or password. Please try again.')
        else:
            messages.error(request, 'Please provide both email and password.')
    
    return render(request, 'accounts/login.html', {'title': 'Login'})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    response = redirect('accounts:login')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


