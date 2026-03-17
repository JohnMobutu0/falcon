# fleet/mixins.py
from django.http import HttpResponseForbidden

class UserIDRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user_id:
            return HttpResponseForbidden("Not authenticated")
        return super().dispatch(request, *args, **kwargs)