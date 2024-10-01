from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

# view of Login
def login_view(request):
    return render(request, 'auth/login/login.html')

# Post function of loign
def login_post(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # Ensure both request and user are passed
            return JsonResponse({'success': True, 'message': 'Login Successful!'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid username or password!'})
    return JsonResponse({'success': False, 'message': 'Invalid request!'})

# view of registration
def register(request):
    return render(request, 'auth/register/register.html')

# post function of registration
def register_post(request):
    if request.method=='POST':
        username = request.POST.get('username')
        email=request.POST.get('email')
        password=request.POST.get('password')
        confirm_password=request.POST.get('confirm_password')
        
        
        if password == confirm_password:
            if not User.objects.filter(username=username).exists():
                if not User.objects.filter(email=email).exists():
                    user=User.objects.create_user(username=username,email=email,password=password)
                    user.save()
                        
                    return JsonResponse({'success':True, 'message':'Registration Successful!'})
                else:
                        return JsonResponse({'success':False, 'message':'Email already exists!'})
            else:
                return JsonResponse({'success':False, 'message':'Username already exists!'})
        else:
            return JsonResponse({'success':False, 'message':'Passwords do not match!'})
        
    return JsonResponse({'success':False, 'message':'Invalid request!'})


# dashboard



# logout
@login_required
def user_logout(request):
    try:
        logout(request)  # Logs out the user
        return redirect('user_auth:login')  # Redirect to login page after successful logout
    except Exception as e:
        # If there's an error during logout, return an error message
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
 
# user profile
@login_required
def profile(request):
    return render(request, 'auth/profile/profile.html')

@login_required
def profile_update(request):
    
    if request.method == 'POST':
        user=request.user
        
        first_name = request.POST.get('first_name')
        last_name= request.POST.get('last_name')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        user.first_name = first_name
        
        user.last_name = last_name
        
        if password and password== confirm_password:
            user.set_password()
            update_session_auth_hash(request, user)
            
        
        user.save()
        
        return redirect('user_auth:profile')
            
                            
                            
        