from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q

from . import models

@login_required(login_url='login')
def index(request):
    my_groups = models.Group.objects.filter(members=request.user)
    requests = models.JoinRequest.objects.filter(
        group__admin=request.user,
        accepted=False, 
        is_active=True)
    context = {
        'my_groups': my_groups, 
        'requests': requests,
               }
    return render(request, 'index.html', context)



@login_required(login_url='login')
def group_list(request):
    groups = models.Group.objects.filter(admin=request.user)
    return render(request, 'group_list.html', {'groups': groups})

@login_required(login_url='login')
def create_group(request):
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        group = models.Group.objects.create(name=group_name, admin=request.user)
        group.members.add(request.user)
        return redirect('group_list')
    return render(request, 'create_group.html')

@login_required(login_url='login')
def search_group(request):
    if request.method == 'POST':
        q = request.POST.get('q')
        groups = models.Group.objects.filter(name__icontains=q)
        return render(request, 'group_list.html', {'groups': groups})
    return redirect('group_list')
    

@login_required(login_url='login')
def send_join_request(request, code):
    group = get_object_or_404(models.Group, code=code)
    models.JoinRequest.objects.create(user=request.user, group=group)
    return redirect('group_list')

@login_required(login_url='login')
def accept_join_request(request, code):
    group = models.JoinRequest.objects.get(code=code).group
    if request.user.is_authenticated and request.user == group.admin:
        join_request = get_object_or_404(models.JoinRequest, code=code)
        join_request.accepted = True
        join_request.is_active = False
        join_request.save()
        group.members.add(join_request.user)
        return redirect('group_list')
    else:
        return render(request, 'error/join_request.html')

@login_required(login_url='login')
def leave_group(request, code):
    group = get_object_or_404(models.Group, code=code)
    group.members.remove(request.user)
    return redirect('group_list')


@login_required(login_url='login')
def delete_join_request(request, code):
    join_request = models.JoinRequest.objects.get(code=code)
    if request.user.is_authenticated and request.user == join_request.group.admin:
        join_request.is_active = False
        join_request.save()
        return redirect('index')

@login_required(login_url='login')
def send_message(request, code):
    group = get_object_or_404(models.Group, code=code)
    if request.user not in group.members.all():
        messages.error(request, 'You are not a member of this group.')
        return redirect('group_list')
    
    if request.method == 'POST':
        content = request.POST.get('content')
        models.Message.objects.create(group=group, sender=request.user, content=content)
    return redirect('group_messages', code=code)


@login_required(login_url='login')
def group_messages(request, code):
    group = get_object_or_404(models.Group, code=code)
    messages = models.Message.objects.filter(group=group)
    return render(request, 'group_messages.html', {'group': group, 'messages': messages})


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return redirect('register')

        user = User.objects.create_user(username=username, password=password)
        user.save()
        messages.success(request, f'Account created for {username}! You can now log in.')
        return redirect('login')

    return render(request, 'register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('group_list')
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('login')

    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('login')