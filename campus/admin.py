from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

@admin.register(User)
class CampusUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("College profile", {"fields": ("role", "phone")}),)
    list_display = ("username", "email", "first_name", "last_name", "role", "is_active")
    list_filter = ("role", "is_active")

for model in [Department, Course, Faculty, Student, Subject, Attendance, Examination, Result, Fee, FeePayment, TimetableEntry, Notice, StudyMaterial]:
    admin.site.register(model)
admin.site.site_header = "Smart Campus Administration"
admin.site.site_title = "Smart Campus"
admin.site.index_title = "College operations"
