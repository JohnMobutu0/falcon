from django.urls import path
from . import views


app_name = 'fleet'
urlpatterns = [
    # AutomobileType
    path('types/', views.AutomobileTypeListView.as_view(), name='type_list'),
    path('types/create/', views.AutomobileTypeCreateView.as_view(), name='type_create'),
    path('types/<int:pk>/edit/', views.AutomobileTypeUpdateView.as_view(), name='type_edit'),
    path('types/<int:pk>/delete/', views.AutomobileTypeDeleteView.as_view(), name='type_delete'),

    # AutomobileStatus (similar)
    path('statuses/', views.AutomobileStatusListView.as_view(), name='status_list'),
    path('statuses/create/', views.AutomobileStatusCreateView.as_view(), name='status_create'),
    path('statuses/<int:pk>/edit/', views.AutomobileStatusUpdateView.as_view(), name='status_edit'),
    path('statuses/<int:pk>/delete/', views.AutomobileStatusDeleteView.as_view(), name='status_delete'),

    # Automobile
    path('autos/', views.AutomobileListView.as_view(), name='automobile_list'),
    path('autos/create/', views.AutomobileCreateView.as_view(), name='automobile_create'),
    path('autos/<int:pk>/edit/', views.AutomobileUpdateView.as_view(), name='automobile_edit'),
    path('autos/<int:pk>/borrow/', views.BorrowAutomobileView.as_view(), name='borrow_auto'),
    path('borrow/<int:pk>/return/', views.ReturnAutomobileView.as_view(), name='return_auto'),

    # Borrow records list
    path('borrows/', views.BorrowRecordListView.as_view(), name='borrow_list'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    # ... other URLs ...
    path('borrow/<int:pk>/edit-due/', views.UpdateDueDateView.as_view(), name='edit_due_date'),

]