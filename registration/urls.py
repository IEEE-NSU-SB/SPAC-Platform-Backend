from django.urls import path

from .views import *

app_name='registration'
urlpatterns = [
    path('', landing, name='landing'),
    path('registration/landing/', reg_landing, name='reg_landing'),
    path('phase-1/', registration_form_phase01, name='registration_form_phase01'),
    path('phase-2/', registration_form_phase02, name='registration_form_phase02'),
    path('reg/', registration_redirect, name="registration_redirect"),
    path('registration/admin/', registration_admin, name='registration_admin'),
    path('registration/toggle-publish/', toggle_publish, name='toggle_publish'),
    path('registration/responses/', response_table, name='response_table'),
    path('registration/response/<int:id>/', view_response, name='view_response'),
    path('registration/submit-form/', submit_form, name='submit_form'),
    path('registration/download-excel/', download_excel, name='download_excel'),
    path('registration/save_selected_p01/', save_selected_phase01, name='save_selected_phase01'),
    path('registration/send_p02_email/', send_phase02_email, name='send_phase02_email')
]   