from django.shortcuts import render, redirect
from django.contrib import messages
import bcrypt
from .models import *
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

def index(request):
    return render(request, 'myapp/index.html')

def register(request):
    if request.method == 'POST':

        # Validations for registering
        has_errors = False

        if len(request.POST['first_name']) < 2:
            has_errors = True
            messages.error(request, 'First name must be at least 2 characters long.')

        if len(request.POST['last_name']) < 2:
            has_errors = True
            messages.error(request, 'Last name must be at least 2 characters long.')

        if not EMAIL_REGEX.match(request.POST['email']):
            has_errors = True
            messages.error(request, 'Invalid email address.')
        
        if len(request.POST['password']) < 8:
            has_errors = True
            messages.error(request, 'Password must be at least 8 characters long.')

        if not request.POST['password'] == request.POST['password_confirm']:
            has_errors = True
            messages.error(request, 'Password and Password Confirmation do not match.')
        
        if User.objects.filter(email=request.POST['email']).exists():
            has_errors = True
            messages.error(request, 'Email already exists. Please proceed to login.')
        
        if has_errors:
            return redirect('/')

    # Password hash for Django 2.0 version
    hash1 = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt())
    pwhash = hash1.decode("utf-8")

    # Create new user
    user = User.objects.create(
        first_name=request.POST['first_name'],
        last_name=request.POST['last_name'],
        email=request.POST['email'],
        password=pwhash
    )

    messages.success(request, 'Thanks for registering. Please proceed to login.')
    return redirect('/')

def login(request):
    if request.method == 'POST':

        # Check if email already exists in DB
        try:
            user = User.objects.get(email=request.POST['email'])
        except Exception as e:
            # Exception error will print in terminal as "User matching query does not exist."
            print(e)
            messages.error(request, 'Email does not exist. Please register.')
            return redirect('/')

        # Check if password hash matches saved password hash in DB
        valid_pass = bcrypt.checkpw(request.POST['password'].encode(), user.password.encode())

        # If passwords match, save user session in user ID and redirect to Dashboard page
        if valid_pass:
            request.session['user_id'] = user.id
            print('Logged in.')
            return redirect('/dashboard')
        
        else:
            messages.error(request, 'Email and password do not match. Please try again.')
            return redirect('/')


def logout(request):
    request.session.clear()
    return redirect('/')

def dashboard(request):
    user = User.objects.get(id=request.session['user_id'])

    my_jobs = Job.objects.filter(poster=user)
    other_jobs = Job.objects.exclude(poster=user)
    my_work = user.added_work.all()

    context = {
        'user': user,
        'my_jobs': my_jobs,
        'other_jobs': other_jobs,
        'my_work': my_work,
    }
    return render(request, 'myapp/dashboard.html', context)

def create(request):
    user = User.objects.get(id=request.session['user_id'])

    context = {
        'user': user,
    }
    return render(request, 'myapp/create.html', context)

def createProcess(request):
    if request.method == "POST":

        # Validations for creating a new task
        has_errors = False

        if len(request.POST['title']) < 4:
            has_errors = True
            messages.error(request, 'Title must be at least 3 characters long.')

        if len(request.POST['description']) < 11:
            has_errors = True
            messages.error(request, 'Description must be at least 10 characters long.')

        if len(request.POST['location']) < 1:
            has_errors = True
            messages.error(request, 'Please enter a location.')
            
        if has_errors:
            return render(request, 'myapp/create.html')

        # Create new task
        else:
            user = User.objects.get(id=request.session['user_id'])

            newTask = Job.objects.create(
                title=request.POST['title'],
                description=request.POST['description'],
                location=request.POST['location'],
                poster=user
            )
            print(newTask)
            return redirect('/dashboard')

    return redirect('/dashboard')

def view(request, job_id):
    context = {
        'job': Job.objects.get(id=job_id),
    }
    return render(request, 'myapp/view.html', context)

def update(request, job_id):
    user = User.objects.get(id=request.session['user_id'])

    context = {
        'job': Job.objects.get(id=job_id)
    }

    return render(request, 'myapp/update.html', context)

def updateProcess(request, job_id):
    if request.method == "POST":
        user = User.objects.get(id=request.session['user_id'])

        context = {
            'user': user,
        }

        # Prepopulate form from DB
        request.session['title'] = request.POST['title']
        request.session['description'] = request.POST['description']
        request.session['location'] = request.POST['location']

        # Validations for updating the task
        has_errors = False

        if len(request.POST['title']) < 4:
            has_errors = True
            messages.error(request, 'Title must be at least 3 characters long.')

        if len(request.POST['description']) < 11:
            has_errors = True
            messages.error(request, 'Description must be at least 10 characters long.')

        if len(request.POST['location']) < 1:
            has_errors = True
            messages.error(request, 'Please enter a location.')
            
        if has_errors:
            return render(request, 'myapp/update.html', context)

        # Save changes to updates
        else:
            task = Job.objects.get(id=job_id)
            task.title = request.POST['title']
            task.description = request.POST['description']
            task.location = request.POST['location']
            task.save()
            messages.success(request, 'Successfully updated.')
            return redirect('/update/' + str(job_id), context)

    return redirect('/dashboard', context)

def delete(request, job_id):
    context = {
        'job': Job.objects.get(id=job_id)
    }
    return render(request, 'myapp/delete.html', context)

def confirm(request, job_id):
    task = Job.objects.get(id=job_id)
    task.delete()
    print('Successfully deleted.')
    return redirect('/dashboard')

def work(request, job_id):
    user = User.objects.get(id=request.session['user_id'])
    task = Job.objects.get(id=job_id)

    # work = n:m field
    task.work.add(user)

    # added_work = n:m related name
    my_work = user.added_work.all()

    context = {
        'my_work': my_work,
    }
   
    print("Added work.")
    return redirect('/dashboard', context)

def done(request, job_id):
    user = User.objects.get(id=request.session['user_id'])
    task = Job.objects.get(id=job_id)

    task.work.remove(user)

    my_work = user.added_work.all()

    context = {
        'my_work': my_work,
    }

    print("Removed work.")
    return redirect('/dashboard', context)