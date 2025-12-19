from django.contrib import admin

from .models import *
# Register your models here.

@admin.register(EventFormStatus_Phase01)
class EventFormStatusAdmin_Phase01(admin.ModelAdmin):
    list_display = ['is_published', 'updated_at']

@admin.register(EventFormStatus_Phase02)
class EventFormStatusAdmin_Phase02(admin.ModelAdmin):
    list_display = ['is_published', 'updated_at']

@admin.register(Form_Participant_Phase_1)
class Form_Participant_Phase01_Admin(admin.ModelAdmin):
    list_display = ['id', 'name', 'university', 'email', 'membership_type', 'is_nsu_student', 'created_at']

@admin.register(Form_Participant_Phase_2)
class Form_Participant_Phase01_Admin(admin.ModelAdmin):
    list_display = ['id', 'name', 'institution', 'email', 'membership_type', 'created_at']

admin.site.register(Form_Participant_Unique_Code_Phase_2)