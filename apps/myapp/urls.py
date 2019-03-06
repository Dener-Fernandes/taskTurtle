from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('register', views.register),
    path('login', views.login),
    path('logout', views.logout),
    path('dashboard', views.dashboard),
    path('create', views.create),
    path('createProcess', views.createProcess),
    path('view/<int:job_id>', views.view),
    path('update/<int:job_id>', views.update),
    path('updateProcess/<int:job_id>', views.updateProcess),
    path('delete/<int:job_id>', views.delete),
    path('delete/<int:job_id>/confirm', views.confirm),
    path('work/<int:job_id>', views.work),
    path('done/<int:job_id>', views.done),

]