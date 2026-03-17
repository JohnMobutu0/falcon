# myapp/decorators.py

from functools import wraps
from django.shortcuts import redirect, render

def jwt_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if hasattr(request, 'user_id') and request.user_id:
            return view_func(request, *args, **kwargs)
        else:
            # Redirect to Laravel login
            return redirect("https://www.baidu.com/")
    return wrapper