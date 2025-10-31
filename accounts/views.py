from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required


# handle default login 
@login_required
def login_redirect_view(request):
    user = request.user
    if user.is_staff:
        return redirect('moderator_dashboard')
    else:
        return redirect('home')

# only load moderator dashboard if the user is staff
@login_required
def moderator_dashboard(request):
    user = request.user
    if user.is_staff:
        return render(request, 'moderator_dashboard.html')
    

# each user gets a custom url and profile page
@login_required
def user_profile(request, username):
    return render(request, 'profile.html', {'user': request.user})
