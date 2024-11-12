from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/',views.login_view, name='login'),
    path('register/', views.register_view, name='register'),  
    path('create-ticket/', views.create_ticket, name='create_ticket'), 
    path('add-activity/', views.add_activity, name='add_activity'),  
    path('ticket-history/', views.ticket_history_view,name='ticket_history'),

    path('ticket-history/<int:ticket_id>/add-activity/', views.add_activity, name='add_activity'), 
    path('ticket-history/<int:ticket_id>/update-status/', views.update_ticket_status, name='update_ticket_status'), 
]
