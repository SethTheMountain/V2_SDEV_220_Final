from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Employee
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
import pytz
import json

def main(request):
    if request.method == 'POST':
        messages.error(request, "Admin login not implemented yet.")
        return redirect('main')
    return render(request, 'employees/main.html', {'timezone_set': request.session.get('timezone_set', False)})

def register(request):
    if request.method == 'POST':
        try:
            employee = Employee(
                first_name=request.POST['first_name'],
                last_name=request.POST['last_name'],
                employee_id=request.POST['employee_id'],
                address=request.POST['address'],
                phone_number=request.POST['phone_number'],
                department=request.POST['department'],
                position=request.POST['position'],
                hours_per_week=float(request.POST['hours_per_week']),
                hourly_salary=float(request.POST['hourly_salary'])
            )
            employee.full_clean()
            employee.save()
            messages.success(request, "Employee registered successfully!")
            return redirect('confirmation')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    return render(request, 'employees/register.html')

def confirmation(request):
    return render(request, 'employees/confirmation.html')

def custom_admin(request):
    employees = Employee.objects.all()
    return render(request, 'employees/admin.html', {'employees': employees})

@require_POST
def update_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    try:
        employee.first_name = request.POST['first_name']
        employee.last_name = request.POST['last_name']
        employee.employee_id = request.POST['employee_id']
        employee.address = request.POST['address']
        employee.phone_number = request.POST['phone_number']
        employee.department = request.POST['department']
        employee.position = request.POST['position']
        employee.hours_per_week = float(request.POST['hours_per_week'])
        employee.hourly_salary = float(request.POST['hourly_salary'])
        employee.full_clean()
        employee.save()
        messages.success(request, "Employee updated successfully!")
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
    return redirect('custom_admin')

@require_POST
def delete_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    employee.delete()
    messages.success(request, "Employee deleted successfully!")
    return redirect('custom_admin')

@require_POST
def set_timezone(request):
    try:
        data = json.loads(request.body)
        timezone = data.get('timezone')
        if timezone in pytz.all_timezones:
            request.session['timezone'] = timezone
            request.session['timezone_set'] = True
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'message': 'Invalid timezone'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

def new_admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('new_admin_dashboard')
        else:
            messages.error(request, "Invalid credentials or you are not an admin.")
    return render(request, 'employees/new_admin_login.html')

def new_admin_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('main')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def new_admin_dashboard(request):
    employees = Employee.objects.all()
    query = request.GET.get('search', '')
    if query:
        employees = employees.filter(first_name__icontains=query) | employees.filter(last_name__icontains=query) | employees.filter(employee_id__icontains=query)
    return render(request, 'employees/new_admin_dashboard.html', {'employees': employees, 'query': query})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def new_edit_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if request.method == 'POST':
        try:
            employee.first_name = request.POST['first_name']
            employee.last_name = request.POST['last_name']
            employee.employee_id = request.POST['employee_id']
            employee.address = request.POST['address']
            employee.phone_number = request.POST['phone_number']
            employee.department = request.POST['department']
            employee.position = request.POST['position']
            employee.hours_per_week = float(request.POST['hours_per_week'])
            employee.hourly_salary = float(request.POST['hourly_salary'])
            employee.full_clean()
            employee.save()
            messages.success(request, "Employee updated successfully!")
            return redirect('new_admin_dashboard')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    return render(request, 'employees/new_edit_employee.html', {'employee': employee})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def new_delete_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    if request.method == 'POST':
        employee.delete()
        messages.success(request, "Employee deleted successfully!")
        return redirect('new_admin_dashboard')
    return render(request, 'employees/new_confirm_delete.html', {'employee': employee})