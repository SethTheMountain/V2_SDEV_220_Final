from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('register/', views.register, name='register'),
    path('confirmation/', views.confirmation, name='confirmation'),
    path('custom_admin/', views.custom_admin, name='custom_admin'),
    path('update_employee/<int:employee_id>/', views.update_employee, name='update_employee'),
    path('delete_employee/<int:employee_id>/', views.delete_employee, name='delete_employee'),
    path('set_timezone/', views.set_timezone, name='set_timezone'),
    path('new-admin-login/', views.new_admin_login, name='new_admin_login'),
    path('new-admin-logout/', views.new_admin_logout, name='new_admin_logout'),
    path('new-admin-dashboard/', views.new_admin_dashboard, name='new_admin_dashboard'),
    path('new-edit-employee/<int:employee_id>/', views.new_edit_employee, name='new_edit_employee'),
    path('new-delete-employee/<int:employee_id>/', views.new_delete_employee, name='new_delete_employee'),
]