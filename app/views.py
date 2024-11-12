from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import Ticket
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from .models import Ticket,Activity
from django.contrib.auth.models import User
from .utils import send_notification_email
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('create_ticket')
    return render(request, 'login.html')


@login_required
def create_ticket(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        priority = request.POST['priority']
        assigned_user_ids = request.POST.getlist('assigned_users')

        ticket = Ticket.objects.create(
            title=title,
            description=description,
            priority=priority,
            creator=request.user
        )
        
        
        for user_id in assigned_user_ids:
            user = User.objects.get(id=user_id)
            ticket.assigned_to.add(user)
            send_mail(
                'New Ticket Assignment',
                f"You have been assigned to ticket: {ticket.title}",
                'from@example.com',
                [user.email],
            )
        return redirect('create_ticket.html')
    
    users = User.objects.all()
    return render(request, 'create_ticket.html', {'users': users})
def ticket_history_view(request):
    tickets = Ticket.objects.all().prefetch_related('assigned_to')  
    ticket_data = []
    for ticket in tickets:
        assigned_users = ', '.join([user.username for user in ticket.assigned_to.all()])
        ticket_data.append({
            'sr_no': len(ticket_data) + 1,
            'title': ticket.title,
            'description': ticket.description,
            'priority': ticket.priority,
            'creator': ticket.creator.username,
            'assigned_to': assigned_users,
            'created_at': ticket.created_at,
        })

    return render(request, 'ticket_history.html', {'ticket_data': ticket_data})


@login_required
def add_activity(request, ticket_id):
    if request.method == 'POST':
        ticket = Ticket.objects.get(id=ticket_id)
        action = request.POST['action']
        activity = Activity.objects.create(ticket=ticket, user=request.user, action=action)
        
    
        recipients = list(ticket.assignees.all()) + [ticket.creator]
        
        for recipient in recipients:
            subject = f"New activity on ticket {ticket.title}"
            message = render_to_string('emails/activity_update.html', {'ticket': ticket, 'activity': activity, 'user': recipient})
            send_notification_email(subject, 'emails/activity_update.html', {'ticket': ticket, 'activity': activity, 'user': recipient}, [recipient.email])

        return redirect('ticket_detail', ticket_id=ticket.id)

@login_required
def update_ticket_status(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    
    if  ticket.assigned_to.all():
        return HttpResponse("You  have permission to update this ticket's status.", status=403)
    
    if request.method == "POST":
        new_status = request.POST.get('status')
        if new_status in ["Open", "In Progress", "Resolved", "Closed"]:
            ticket.status = new_status
            ticket.save()
            return redirect('ticket_history') 
    
    return render(request, 'app/update_status.html', {'ticket': ticket})

def add_activity(request, ticket_id):
    try:
        ticket = Ticket.objects.get(id=ticket_id)
    except Ticket.DoesNotExist:
        return HttpResponse("Ticket not found", status=404)

    if request.method == "POST":

        return HttpResponse("Activity added successfully")  

    return render(request, 'add_activity.html', {'ticket': ticket})
