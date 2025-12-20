from django.urls import path

from .views import *

app_name='registration'
urlpatterns = [
    path('', landing, name='landing'),
    path('registration/landing/', reg_landing, name='reg_landing'),
    path('phase-1/', registration_form_phase01, name='registration_form_phase01'),
    path('phase-2/', registration_form_phase02, name='registration_form_phase02'),
    path('registration/admin/phase-1/', registration_admin_phase01, name='registration_admin_phase01'),
    path('registration/admin/phase-2/', registration_admin_phase02, name='registration_admin_phase02'),
    path('registration/admin/phase-1/toggle-publish/', toggle_publish_phase01, name='toggle_publish_phase01'),
    path('registration/admin/phase-2/toggle-publish/', toggle_publish_phase02, name='toggle_publish_phase02'),
    path('registration/admin/phase-1/responses/', response_table, name='response_table_phase01'),
    path('registration/admin/phase-2/responses/', response_table2, name='response_table_phase02'),
    path('registration/phase-1/submit-form/', submit_form_phase01, name='submit_form_phase01'),
    path('registration/phase-2/submit-form/', submit_form_phase02, name='submit_form_phase02'),

    path('registration/response/<int:id>/', view_response, name='view_response'),
    path('registration/response2/<int:id>/', view_response2, name='view_response2'),
    path('registration/download-excel/', download_excel, name='download_excel'),
    path('registration/save_selected_p01/', save_selected_phase01, name='save_selected_phase01'),
    path('registration/send_p02_email/', send_phase02_email, name='send_phase02_email')
]   