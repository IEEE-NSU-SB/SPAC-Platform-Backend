from django.urls import path

from .views import *

app_name='registration'
urlpatterns = [
    #Main Landing
    path('', landing, name='landing'),
    #System Landing
    path('registration/landing/', reg_landing, name='reg_landing'),
    #Forms
    path('phase-1/', registration_form_phase01, name='registration_form_phase01'),
    path('phase-2/', registration_form_phase02, name='registration_form_phase02'),
    #Form Admins
    path('registration/admin/phase-1/', registration_admin_phase01, name='registration_admin_phase01'),
    path('registration/admin/phase-2/', registration_admin_phase02, name='registration_admin_phase02'),
    #Form Publish APIs
    path('registration/admin/phase-1/toggle-publish/', toggle_publish_phase01, name='toggle_publish_phase01'),
    path('registration/admin/phase-2/toggle-publish/', toggle_publish_phase02, name='toggle_publish_phase02'),
    #Form Responses
    path('registration/admin/phase-1/responses/', response_table, name='response_table_phase01'),
    path('registration/admin/phase-2/responses/', response_table2, name='response_table_phase02'),
    #Form Submit APIs
    path('registration/phase-1/submit-form/', submit_form_phase01, name='submit_form_phase01'),
    path('registration/phase-2/submit-form/', submit_form_phase02, name='submit_form_phase02'),
    #Form Response Details
    path('registration/admin/phase-1/response/<int:id>/', view_response, name='view_response'),
    path('registration/admin/phase-2/response/<int:id>/', view_response2, name='view_response2'),
    #Form Data Exports
    path('registration/admin/phase-1/download-excel/', download_excel_phase01, name='download_excel_phase01'),
    path('registration/admin/phase-2/download-excel/', download_excel_phase02, name='download_excel_phase02'),

    path('registration/admin/save_selected_p01/', save_selected_phase01, name='save_selected_phase01'),
    path('registration/admin/send_p02_email/', send_phase02_email, name='send_phase02_email'),
    path('registration/admin/save_selected_p02/', save_selected_phase02, name='save_selected_phase02'),

]   