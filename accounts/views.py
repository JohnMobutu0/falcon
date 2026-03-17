from django.shortcuts import redirect, render
from django.http import HttpResponse



def authent(request):
    """A view that only shows content if the user is authenticated via JWT."""
    if hasattr(request, 'user_id') and request.user_id:
        return redirect('index')
    else:
        return render(request, "accounts/unauthorized.html", status=401)