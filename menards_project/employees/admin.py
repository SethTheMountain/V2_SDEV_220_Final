from django.contrib import admin
from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'employee_id', 'department', 'position', 'created_at')
    list_filter = ('department', 'position')
    search_fields = ('first_name', 'last_name', 'employee_id')
    ordering = ('-created_at',)