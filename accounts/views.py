from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required


# handle default login 
@login_required
def login_redirect_view(request):
    user = request.user
    if user.is_staff:
        return redirect('moderator_dashboard')
    else:
        return redirect('user_dashboard')

# only load moderator dashboard if the user is staff
@login_required
def moderator_dashboard(request):
    user = request.user
    if user.is_staff:
        return render(request, 'moderator_dashboard.html')

# for loading regular user dashboard
@login_required
def user_dashboard(request):
    return render(request, 'user_dashboard.html')