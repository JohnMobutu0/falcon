from django.shortcuts import render
from django.http import HttpResponse
from fleet.models import Automobile, BorrowRecord
from accounts.decorators import jwt_required


@jwt_required
def index(request):
    
    context = {
        'user_id': request.user_id,
        'user_name': request.user_name,
        #'email': request.email,
        #'user_email': request.user_email,
        #'total_autos': Automobile.objects.count(),
        #'borrowed_count': BorrowRecord.objects.filter(returned_at__isnull=True).count(),
    }
    return render(request, 'dashboard/index.html', context)