from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Employee
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
import pytz
import json
import logging

logger = logging.getLogger(__name__)

def main(request):
    if request.method == 'POST':
        messages.error(request, "Admin login not implemented here. Use /new-admin-login/.")
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
            logger.info("Registered employee: %s (ID: %s)", employee.employee_id, employee.id)
            return redirect('confirmation')
        except IntegrityError as e:
            messages.error(request, "Error: Employee ID already exists.")
            logger.error("Registration failed: %s", str(e))
        except ValueError as e:
            messages.error(request, f"Invalid input: {str(e)}")
            logger.error("Registration failed: %s", str(e))
        except Exception as e:
            messages.error(request, f"Unexpected error: {str(e)}")
            logger.error("Registration failed: %s", str(e))
    return render(request, 'employees/register.html')

def confirmation(request):
    return render(request, 'employees/confirmation.html')

def custom_admin(request):
    employees = Employee.objects.filter(id__isnull=False, id__gt=0)
    logger.debug("Custom admin employees: %s", [emp.id for emp in employees])
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
        logger.info("Updated employee: %s (ID: %s)", employee.employee_id, employee.id)
    except IntegrityError as e:
        messages.error(request, "Error: Employee ID already exists.")
        logger.error("Update failed: %s", str(e))
    except ValueError as e:
        messages.error(request, f"Invalid input: {str(e)}")
        logger.error("Update failed: %s", str(e))
    except Exception as e:
        messages.error(request, f"Unexpected error: {str(e)}")
        logger.error("Update failed: %s", str(e))
    return redirect('custom_admin')

@require_POST
def delete_employee(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    try:
        employee.delete()
        messages.success(request, "Employee deleted successfully!")
        logger.info("Deleted employee: %s (ID: %s)", employee.employee_id, employee_id)
    except Exception as e:
        messages.error(request, f"Error deleting employee: {str(e)}")
        logger.error("Delete failed: %s", str(e))
    return redirect('custom_admin')

@require_POST
def set_timezone(request):
    try:
        data = json.loads(request.body)
        timezone = data.get('timezone')
        if timezone in pytz.all_timezones:
            request.session['timezone'] = timezone
            request.session['timezone_set'] = True
            logger.info("Set timezone: %s", timezone)
            return JsonResponse({'status': 'success'})
        logger.warning("Invalid timezone: %s", timezone)
        return JsonResponse({'status': 'error', 'message': 'Invalid timezone'})
    except Exception as e:
        logger.error("Timezone setting failed: %s", str(e))
        return JsonResponse({'status': 'error', 'message': str(e)})

def new_admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            logger.info("Admin login: %s", username)
            return redirect('new_admin_dashboard')
        else:
            messages.error(request, "Invalid credentials or you are not an admin.")
            logger.warning("Failed admin login attempt: %s", username)
    return render(request, 'employees/new_admin_login.html')

def new_admin_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    logger.info("Admin logout")
    return redirect('main')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def new_admin_dashboard(request):
    employees = Employee.objects.filter(id__isnull=False, id__gt=0)
    query = request.GET.get('search', '')
    if query:
        employees = employees.filter(
            first_name__icontains=query
        ) | employees.filter(
            last_name__icontains=query
        ) | employees.filter(
            employee_id__icontains=query
        )
    valid_employees = [emp for emp in employees if emp.id and isinstance(emp.id, int) and emp.id > 0]
    if len(valid_employees) < employees.count():
        logger.error("Invalid employees filtered out: %s", [
            emp.__dict__ for emp in employees if not (emp.id and isinstance(emp.id, int) and emp.id > 0)
        ])
    logger.debug("Dashboard employees: %s", [(emp.id, emp.employee_id, emp.first_name) for emp in valid_employees])
    if not valid_employees:
        logger.warning("No valid employees found for query: %s", query)
    return render(request, 'employees/new_admin_dashboard.html', {
        'employees': valid_employees,
        'query': query
    })

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
            logger.info("Edited employee: %s (ID: %s)", employee.employee_id, employee.id)
            return redirect('new_admin_dashboard')
        except IntegrityError as e:
            messages.error(request, "Error: Employee ID already exists.")
            logger.error("Edit failed: %s", str(e))
        except ValueError as e:
            messages.error(request, f"Invalid input: {str(e)}")
            logger.error("Edit failed: %s", str(e))
        except Exception as e:
            messages.error(request, f"Unexpected error: {str(e)}")
            logger.error("Edit failed: %s", str(e))
    return render(request, 'employees/new_edit_employee.html', {'employee': employee})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def new_delete_employee(request, employee_id):
    try:
        employee = get_object_or_404(Employee, id=employee_id)
    except Exception as e:
        logger.error("Failed to retrieve employee with ID %s: %s", employee_id, str(e))
        messages.error(request, "Employee not found.")
        return redirect('new_admin_dashboard')

    if request.method == 'POST':
        try:
            employee.delete()
            messages.success(request, "Employee deleted successfully!")
            logger.info("Deleted employee: %s (ID: %s)", employee.employee_id, employee_id)
            return redirect('new_admin_dashboard')
        except Exception as e:
            logger.error("Delete failed for employee ID %s: %s", employee_id, str(e))
            messages.error(request, f"Error deleting employee: {str(e)}")
            return redirect('new_admin_dashboard')

    try:
        return render(request, 'employees/new_confirm_delete.html', {'employee': employee})
    except Exception as e:
        logger.error("Failed to render delete confirmation for employee ID %s: %s", employee_id, str(e))
        messages.error(request, "Error loading delete confirmation page.")
        return redirect('new_admin_dashboard')