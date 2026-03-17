# fleet/views.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.utils import timezone
from .models import AutomobileType, AutomobileStatus, Automobile, BorrowRecord, BorrowDeadlineChange
from .mixins import UserIDRequiredMixin
from .forms import BorrowForm, ReturnForm
from django.views.generic import TemplateView
from django.db.models import Count, Q, OuterRef, Exists
from django.conf import settings
from accounts.decorators import jwt_required
from django.utils.decorators import method_decorator
from datetime import date, timedelta
from django.contrib.auth import get_user_model



# ----------------------------------------------------------------------
# AutomobileType CRUD
# ----------------------------------------------------------------------
#@method_decorator(jwt_required, name='dispatch')
class AutomobileTypeListView(UserIDRequiredMixin, ListView):
    model = AutomobileType
    template_name = 'fleet/type_list.html'
    context_object_name = 'types'

#@method_decorator(jwt_required, name='dispatch')
class AutomobileTypeCreateView(UserIDRequiredMixin, CreateView):
    model = AutomobileType
    fields = ['name', 'description']
    template_name = 'fleet/type_form.html'
    success_url = reverse_lazy('fleet:type_list')

#@method_decorator(jwt_required, name='dispatch')
class AutomobileTypeUpdateView(UserIDRequiredMixin, UpdateView):
    model = AutomobileType
    fields = ['name', 'description']
    template_name = 'fleet/type_form.html'
    success_url = reverse_lazy('fleet:type_list')

#@method_decorator(jwt_required, name='dispatch')
class AutomobileTypeDeleteView(UserIDRequiredMixin, DeleteView):
    model = AutomobileType
    template_name = 'fleet/type_confirm_delete.html'
    success_url = reverse_lazy('fleet:type_list')

# ----------------------------------------------------------------------
# AutomobileStatus CRUD
# ----------------------------------------------------------------------
#@method_decorator(jwt_required, name='dispatch')
class AutomobileStatusListView(UserIDRequiredMixin, ListView):
    model = AutomobileStatus
    template_name = 'fleet/status_list.html'
    context_object_name = 'statuses'

#@method_decorator(jwt_required, name='dispatch')
class AutomobileStatusCreateView(UserIDRequiredMixin, CreateView):
    model = AutomobileStatus
    fields = ['name', 'description', 'color']
    template_name = 'fleet/status_form.html'
    success_url = reverse_lazy('fleet:status_list')

#@method_decorator(jwt_required, name='dispatch')
class AutomobileStatusUpdateView(UserIDRequiredMixin, UpdateView):
    model = AutomobileStatus
    fields = ['name', 'description', 'color']
    template_name = 'fleet/status_form.html'
    success_url = reverse_lazy('fleet:status_list')

#@method_decorator(jwt_required, name='dispatch')
class AutomobileStatusDeleteView(UserIDRequiredMixin, DeleteView):
    model = AutomobileStatus
    template_name = 'fleet/status_confirm_delete.html'
    success_url = reverse_lazy('fleet:status_list')

# ----------------------------------------------------------------------
# Automobile CRUD
# ----------------------------------------------------------------------
#@method_decorator(jwt_required, name='dispatch')
class AutomobileListView(UserIDRequiredMixin, ListView):
    model = Automobile
    template_name = 'fleet/automobile_list.html'
    context_object_name = 'autos'

#@method_decorator(jwt_required, name='dispatch')
class AutomobileCreateView(UserIDRequiredMixin, CreateView):
    model = Automobile
    fields = ['type', 'status', 'license_plate', 'make', 'model', 'year', 'color', 'notes']
    template_name = 'fleet/automobile_form.html'
    success_url = reverse_lazy('fleet:automobile_list')

    def form_valid(self, form):
        form.instance.created_by_user_id = self.request.user_id
        return super().form_valid(form)

#@method_decorator(jwt_required, name='dispatch')
class AutomobileUpdateView(UserIDRequiredMixin, UpdateView):
    model = Automobile
    fields = ['type', 'status', 'license_plate', 'make', 'model', 'year', 'color', 'notes']
    template_name = 'fleet/automobile_form.html'
    success_url = reverse_lazy('fleet:automobile_list')

    # updated_at is auto_now, so no extra handling needed

#@method_decorator(jwt_required, name='dispatch')
class AutomobileDeleteView(UserIDRequiredMixin, DeleteView):
    model = Automobile
    template_name = 'fleet/automobile_confirm_delete.html'
    success_url = reverse_lazy('fleet:automobile_list')

# ----------------------------------------------------------------------
# BorrowRecord Views
# ----------------------------------------------------------------------
#@method_decorator(jwt_required, name='dispatch')
class BorrowRecordListView(UserIDRequiredMixin, ListView):
    model = BorrowRecord
    template_name = 'fleet/borrow_list.html'
    context_object_name = 'records'
    ordering = ['-borrowed_at']  # show newest first

    def get_queryset(self):
        return BorrowRecord.objects.select_related('automobile').order_by('-borrowed_at')

#@method_decorator(jwt_required, name='dispatch')
# fleet/views.py

class BorrowAutomobileView(UserIDRequiredMixin, View):
    def get(self, request, pk):
        auto = get_object_or_404(Automobile, pk=pk)
        if auto.is_borrowed:
            return redirect('fleet:automobile_list')
        form = BorrowForm()
        return render(request, 'fleet/borrow_form.html', {'form': form, 'auto': auto})

    def post(self, request, pk):
        auto = get_object_or_404(Automobile, pk=pk)
        
        
        if auto.is_borrowed:
            return redirect('fleet:automobile_list')
        form = BorrowForm(request.POST)
        if form.is_valid():
            record = BorrowRecord.objects.create(
                automobile=auto,
                borrower_name=form.cleaned_data['borrower_name'],
                borrowed_by=request.user_name,
                notes=form.cleaned_data['notes'],
                due_date=form.cleaned_data['due_date']
            )
            if record.due_date:
                BorrowDeadlineChange.objects.create(
                    borrow_record=record,
                    changed_by_user_name=request.user_name,
                    old_due_date=None,
                    new_due_date=record.due_date,
                    change_type='set',
                    notes="Initial due date set"
                )
            return redirect('fleet:automobile_list')
        return render(request, 'fleet/borrow_form.html', {'form': form, 'auto': auto})

#@method_decorator(jwt_required, name='dispatch')
class ReturnAutomobileView(UserIDRequiredMixin, View):

    def get(self, request, pk):
        record = get_object_or_404(BorrowRecord, pk=pk, returned_at__isnull=True)
        form = ReturnForm(initial={'notes': record.notes})
        return render(request, 'fleet/return_form.html', {
            'form': form,
            'record': record
        })

    def post(self, request, pk):
        record = get_object_or_404(BorrowRecord, pk=pk, returned_at__isnull=True)
        form = ReturnForm(request.POST)

        if form.is_valid():
            record.returned_at = timezone.now()

            notes = form.cleaned_data['notes']
            if notes:
                record.notes += f"\n[Returned on {timezone.now().date()}] {notes}"

            record.save()

            return redirect('fleet:automobile_list')

        return render(request, 'fleet/return_form.html', {
            'form': form,
            'record': record
        })
    

# ... your existing imports ...

#@method_decorator(jwt_required, name='dispatch')
class DashboardView(UserIDRequiredMixin, TemplateView):
    template_name = 'fleet/dashboard.html'
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Due soon (next 3 days)
        due_soon_threshold = timezone.now().date() + timedelta(days=3)
        due_soon = BorrowRecord.objects.filter(
            returned_at__isnull=True,
            due_date__isnull=False,
            due_date__gte=timezone.now().date(),
            due_date__lte=due_soon_threshold
        ).select_related('automobile').order_by('due_date')
        context['due_soon'] = due_soon


        context['now'] = timezone.now().date()

        today = timezone.now().date()
        due_soon_threshold = today + timedelta(days=3)
        context['today'] = today
        context['due_soon_threshold'] = due_soon_threshold







        # --- Counts by status ---
        status_counts = AutomobileStatus.objects.annotate(
            count=Count('automobile')
        ).values('name', 'count', 'color')
        context['status_counts'] = status_counts

        # Total automobiles
        context['total_autos'] = Automobile.objects.count()

        # --- Overdue borrows (borrowed > 7 days and not returned) ---

            # ... existing code ...

        # Overdue borrows based on due_date
        overdue_borrows = BorrowRecord.objects.filter(
            returned_at__isnull=True,
            due_date__isnull=False,
            due_date__lt=timezone.now().date()
        ).select_related('automobile').order_by('due_date')
        context['overdue_borrows'] = overdue_borrows

        # ... rest of context ...

#/////////////////////
        # You can set BORROW_LIMIT_DAYS in settings.py
        # limit_days = getattr(settings, 'BORROW_LIMIT_DAYS', 7)
        # overdue_threshold = timezone.now() - timedelta(days=limit_days)
        # overdue_borrows = BorrowRecord.objects.filter(
        #     returned_at__isnull=True,
        #     borrowed_at__lt=overdue_threshold
        # ).select_related('automobile').order_by('borrowed_at')
        # context['overdue_borrows'] = overdue_borrows
#/////////////////////

        # --- Never borrowed automobiles ---
        # Automobiles that have no borrow records
        never_borrowed = Automobile.objects.annotate(
            has_borrows=Exists(BorrowRecord.objects.filter(automobile=OuterRef('pk')))
        ).filter(has_borrows=False)
        context['never_borrowed'] = never_borrowed

        # --- Most borrowed (top 5) ---
        most_borrowed = Automobile.objects.annotate(
            borrow_count=Count('borrow_records')
        ).order_by('-borrow_count')[:5]
        context['most_borrowed'] = most_borrowed

        # --- Least borrowed (bottom 5, excluding zero) ---
        least_borrowed = Automobile.objects.annotate(
            borrow_count=Count('borrow_records')
        ).filter(borrow_count__gt=0).order_by('borrow_count')[:5]
        context['least_borrowed'] = least_borrowed

        # --- Recent borrow activity (last 5 returns or borrows?) ---
        # Let's show last 5 borrow records (including returned ones)
        recent_borrows = BorrowRecord.objects.select_related('automobile').order_by('-borrowed_at')[:5]
        context['recent_borrows'] = recent_borrows

        return context



# fleet/views.py

class UpdateDueDateView(UserIDRequiredMixin, View):
    def get(self, request, pk):
        record = get_object_or_404(BorrowRecord, pk=pk, returned_at__isnull=True)
        form = BorrowForm(initial={'due_date': record.due_date, 'borrower_name': record.borrower_name, 'notes': record.notes})
        return render(request, 'fleet/update_due_date.html', {'form': form, 'record': record})

    def post(self, request, pk):
        record = get_object_or_404(BorrowRecord, pk=pk, returned_at__isnull=True)
        form = BorrowForm(request.POST)
        if form.is_valid():
            old_due = record.due_date
            new_due = form.cleaned_data['due_date']
            if old_due != new_due:
                if new_due is None:
                    change_type = 'clear'
                elif old_due is None:
                    change_type = 'set'
                else:
                    change_type = 'update'
                BorrowDeadlineChange.objects.create(
                    borrow_record=record,
                    changed_by_user_id=request.user_id,
                    old_due_date=old_due,
                    new_due_date=new_due,
                    change_type=change_type,
                    notes="Due date updated via form"
                )
                record.due_date = new_due
                record.save()
            return redirect('fleet:automobile_list')
        return render(request, 'fleet/update_due_date.html', {'form': form, 'record': record})