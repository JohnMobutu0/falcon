from django.db import models
from django.utils import timezone
from django.conf import settings

class AutomobileType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class AutomobileStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g., "Good", "Needs Repair"
    description = models.TextField(blank=True)
    color = models.CharField(max_length=20, default='secondary')  # for Bootstrap badge

    def __str__(self):
        return self.name

class Automobile(models.Model):
    type = models.ForeignKey(AutomobileType, on_delete=models.PROTECT)
    status = models.ForeignKey(AutomobileStatus, on_delete=models.PROTECT)
    license_plate = models.CharField(max_length=20, unique=True)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField()
    color = models.CharField(max_length=30, blank=True)
    notes = models.TextField(blank=True)
    created_by_user_id = models.IntegerField()  # from JWT
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.license_plate} - {self.make} {self.model}"
    
        # In Automobile model
    @property
    def is_borrowed(self):
        return self.borrow_records.filter(returned_at__isnull=True).exists()

    @property
    def current_borrow_record(self):
        return self.borrow_records.filter(returned_at__isnull=True).first()



class BorrowRecord(models.Model):
    automobile = models.ForeignKey(Automobile, on_delete=models.CASCADE, related_name='borrow_records')
    borrower_name = models.CharField(max_length=100)
    borrowed_by = models.CharField(max_length=150, null=True)  # staff who performed the borrow action
    borrowed_at = models.DateTimeField(auto_now_add=True)
    returned_at = models.DateTimeField(null=True, blank=True)
    condition_returned = models.ForeignKey(AutomobileStatus, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    notes = models.TextField(blank=True)
        # ... existing fields ...
    due_date = models.DateField(null=True, blank=True, help_text="Expected return date")
     # ... existing fields ...

    @property
    def is_overdue(self):
        if self.returned_at or not self.due_date:
            return False
        return self.due_date < timezone.now().date()

    def __str__(self):
        return f"{self.automobile} borrowed by {self.borrower_name} on {self.borrowed_at}"
    



class BorrowDeadlineChange(models.Model):
    CHANGE_TYPES = [
        ('set', 'Set'),
        ('update', 'Update'),
        ('clear', 'Clear'),
    ]
    borrow_record = models.ForeignKey(BorrowRecord, on_delete=models.CASCADE, related_name='deadline_changes')
    changed_by_user_name = models.CharField(max_length=150, null=True)
    old_due_date = models.DateField(null=True, blank=True)
    new_due_date = models.DateField(null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    change_type = models.CharField(max_length=10, choices=CHANGE_TYPES)
    notes = models.TextField(blank=True, help_text="Reason for change if any")

    class Meta:
        ordering = ['-changed_at']
    

