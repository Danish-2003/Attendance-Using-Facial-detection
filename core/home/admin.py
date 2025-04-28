from django.contrib import admin

# Register your models here.
from .models import Students,Attendance

@admin.register(Students)

class StudentAdmin(admin.ModelAdmin):
    list_display = ("id","name","roll_no","image")
@admin.register(Attendance)

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("id","student","date","time","status")
    list_filter = ("date","status")