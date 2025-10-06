from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test

@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    return render(request, 'administrator/dashboard.html')