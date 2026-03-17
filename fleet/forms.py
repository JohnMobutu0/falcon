# fleet/forms.py

from django import forms

class BorrowForm(forms.Form):
    borrower_name = forms.CharField(max_length=255)
    notes = forms.CharField(widget=forms.Textarea, required=False)
    due_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="Expected return date (optional)"
    )

class ReturnForm(forms.Form):
    notes = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label="Return Notes"
    )