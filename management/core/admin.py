"""
Admin module for managing the core models of the Support System application.

This module registers the following models with the Django admin interface:
- User: Extends the default UserAdmin to include additional fields for role and profile picture.
- Customer: Provides admin functionality for managing customers, including filtering by payment status.
- Agent: Provides admin functionality for managing agents, including filtering by department and availability.
- Department: Allows management of departments with search functionality.
- Ticket: Enables management of support tickets with filtering by status and creation date.

Classes:
- UserAdmin: Custom admin for the User model with additional fields and filters.
- CustomerAdmin: Admin for the Customer model with display, filter, and search options.
- AgentAdmin: Admin for the Agent model with display, filter, and search options.
- DepartmentAdmin: Admin for the Department model with display and search options.
- TicketAdmin: Admin for the Ticket model with display, filter, and search options.

Written in 2025 by Dorna Raj Gyawali <dronarajgyawali@gmail.com>
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core.models import User, Customer, Agent, Department, Ticket

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Profile', {'fields': ('role', 'profile_picture')}),
    )
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'solved_issues', 'is_paid')
    list_filter = ('is_paid',)
    search_fields = ('user__username',)

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'current_customers', 'max_customers', 'is_available')
    list_filter = ('department', 'is_available')
    search_fields = ('user__username',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'customer', 'agent', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('ticket_id', 'customer__user__username', 'agent__user__username')
