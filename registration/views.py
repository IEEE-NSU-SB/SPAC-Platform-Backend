import csv
import json
import pandas as pd
from io import BytesIO
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from access_ctrl.decorators import permission_required
from access_ctrl.utils import Site_Permissions
from system_administration.utils import log_exception
from emails.views import send_participant_phase02_email, send_registration_email_phase01, send_registration_email_phase02
from django.db.models import Count
from django.db.models.functions import Trim

from .models import *

def _get_publish_status_phase01() -> bool:
    status = EventFormStatus_Phase01.objects.order_by('-updated_at').first()
    return bool(status and status.is_published)

def _get_publish_status_phase02() -> bool:
    status = EventFormStatus_Phase02.objects.order_by('-updated_at').first()
    return bool(status and status.is_published)

def landing(request):

    if not request.user.is_authenticated:
        return redirect('registration:registration_form_phase01')
    
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('registration:reg_landing')
    
    if request.user.is_authenticated:
        if not Site_Permissions.user_has_permission(request.user, 'reg_form_control'):
            return redirect('core:dashboard')
        elif not Site_Permissions.user_has_permission(request.user, 'view_qr_dashboard'):
            return redirect('registration:reg_landing')
        else:
            return redirect('core:dashboard')
    else:
        return redirect('registration:registration_form_phase01')
    

@login_required
@permission_required('reg_form_control')
def reg_landing(request):
    return render(request, 'landingpage.html')

def registration_form_phase01(request):
    """Display the registration form for general users. Hidden if not published."""
    # If staff/superuser hits the user URL, send them to the admin view

    if request.user.is_authenticated and request.user.is_staff:
        return redirect('registration:registration_admin_phase01')
    
    if request.user.is_authenticated:
        if not Site_Permissions.user_has_permission(request.user, 'reg_form_control'):
            return redirect('core:dashboard')
        elif not Site_Permissions.user_has_permission(request.user, 'view_qr_dashboard'):
            return redirect('registration:registration_admin_phase01')
        else:
            return redirect('core:dashboard')

    registration_count = Form_Participant_Phase_1.objects.count()
    registration_closed = registration_count >= 10000
    context = {
        'is_staff_view': False,
        'is_published': _get_publish_status_phase01(),
        'registration_closed': registration_closed,
    }
    return render(request, 'form.html', context)

def registration_form_phase02(request):
    """Display the registration form for general users. Hidden if not published."""
    # If staff/superuser hits the user URL, send them to the admin view

    if request.user.is_authenticated and request.user.is_staff:
        return redirect('registration:registration_admin_phase02')
    
    if request.user.is_authenticated:
        if not Site_Permissions.user_has_permission(request.user, 'reg_form_control'):
            return redirect('core:dashboard')
        elif not Site_Permissions.user_has_permission(request.user, 'view_qr_dashboard'):
            return redirect('registration:registration_admin_phase02')
        else:
            return redirect('core:dashboard')
    
    unique_code = request.GET.get('token')
    if unique_code:
        if not Form_Participant_Unique_Code_Phase_2.objects.filter(unique_code=unique_code).exists():
            return render(request, 'check_token.html', {})
    else:
        return render(request, 'check_token.html', {})

    registration_count = Form_Participant_Phase_2.objects.count()
    registration_closed = registration_count >= 10000
    universities = University.objects.all()

    context = {
        'is_staff_view': False,
        'is_published': _get_publish_status_phase02(),
        'registration_closed': registration_closed,
        'universities':universities,
        'unique_code':unique_code,
    }
    return render(request, 'phase2form.html',context)

@login_required
@permission_required('reg_form_control')
def registration_admin_phase01(request):
    """Staff-only admin view to manage and preview the form regardless of publish state."""

    registration_count = Form_Participant_Phase_1.objects.count()

    permisions = {
        'reg_form_control':Site_Permissions.user_has_permission(request.user, 'reg_form_control'),
        'view_reg_responses_list':Site_Permissions.user_has_permission(request.user, 'view_reg_responses_list'),
        'view_finance_info':Site_Permissions.user_has_permission(request.user, 'view_finance_info'),
        'view_qr_dashboard':Site_Permissions.user_has_permission(request.user, 'view_qr_dashboard'),
    }

    context = {
        'is_staff_view': True,
        'is_published': _get_publish_status_phase01(),
        'registration_count':registration_count,
        'has_perm': permisions
    }
    return render(request, 'form.html', context)

@login_required
@permission_required('reg_form_control')
def registration_admin_phase02(request):
    """Staff-only admin view to manage and preview the form regardless of publish state."""

    registration_count = Form_Participant_Phase_2.objects.count()
    universities = University.objects.all()

    permisions = {
        'reg_form_control':Site_Permissions.user_has_permission(request.user, 'reg_form_control'),
        'view_reg_responses_list':Site_Permissions.user_has_permission(request.user, 'view_reg_responses_list'),
        'view_finance_info':Site_Permissions.user_has_permission(request.user, 'view_finance_info'),
        'view_qr_dashboard':Site_Permissions.user_has_permission(request.user, 'view_qr_dashboard'),
    }

    context = {
        'is_staff_view': True,
        'is_published': _get_publish_status_phase02(),
        'registration_count':registration_count,
        'has_perm': permisions,
        'universities':universities,
    }
    return render(request, 'phase2form.html', context)

@login_required
@require_POST
def toggle_publish_phase01(request):
    """Toggle EventFormStatus.is_published and return current status."""
    status = EventFormStatus_Phase01.objects.order_by('-updated_at').first()
    if not status:
        status = EventFormStatus_Phase01.objects.create(is_published=True)
    else:
        status.is_published = not status.is_published
        status.save(update_fields=['is_published'])
    return JsonResponse({'success': True, 'is_published': status.is_published})

@login_required
@require_POST
def toggle_publish_phase02(request):
    """Toggle EventFormStatus.is_published and return current status."""
    status = EventFormStatus_Phase02.objects.order_by('-updated_at').first()
    if not status:
        status = EventFormStatus_Phase02.objects.create(is_published=True)
    else:
        status.is_published = not status.is_published
        status.save(update_fields=['is_published'])
    return JsonResponse({'success': True, 'is_published': status.is_published})

def submit_form_phase01(request):
    """Handle form submission and save participant data"""
    try:
        if request.method == 'POST':
            
            status = EventFormStatus_Phase01.objects.order_by('-updated_at').first()

            # if not Site_Permissions.user_has_permission(request.user, 'reg_form_control'):
            if not Site_Permissions.user_has_permission(request.user, 'reg_form_control') and status.is_published == False:
                return JsonResponse({
                'success': False,
                'message': 'Form has been turned off'
                })

            # Get form data
            #Step 1
            name = request.POST.get('name')
            email = request.POST.get('email')
            contact_number = request.POST.get('contact_number')
            is_nsu_student = request.POST.get('is_student_bool')
            department = ''
            if is_nsu_student == 'True':
                university = 'North South University'
                university_id = request.POST.get('nsu_id','')
                department = request.POST.get('department','')
            else:
                university = request.POST.get('uni_name', '')
                university_id = request.POST.get('uni_id','')
                department = request.POST.get('major','')

            membership_type = request.POST.get('membership_type')
            if membership_type == 'member':
                ieee_id = request.POST.get('ieee_id')
            else:
                ieee_id = 'N/A'
            ambassador_code = request.POST.get('ambassador_code', '')

            # Step 2
            # Collect questionnaire answers
            answers = {
                'question1': request.POST.get('question1', ''),
                'question2': request.POST.get('question2', ''),
                'question3': request.POST.get('question3', ''),
            }
            comments = request.POST.get('comments')

            # Create and save participant
            participant = Form_Participant_Phase_1.objects.create(
                name=name,
                email=email,
                contact_number=contact_number,
                membership_type=membership_type,
                ieee_id=ieee_id,
                university=university,
                department=department,
                university_id=university_id,
                answers=answers,
                is_nsu_student=is_nsu_student,
                ambassador_code=ambassador_code,
                comments=comments,
            )

            send_registration_email_phase01(request, participant.name, participant.email)
            
            # Return success response
            return JsonResponse({
                'success': True,
                'message': 'Registration successful! Your participant ID is: ' + str(participant.id),
                'participant_id': participant.id
            })
                        
        else:
            # If not POST request, return error
            return JsonResponse({
                'success': False,
                'message': 'Invalid request method'
            })
    except Exception as e:
        # Return error response
        log_exception(e, request)
        return JsonResponse({
            'success': False,
            'message': 'Registration failed'
        })
    

def submit_form_phase02(request):
    """Handle form submission and save participant data"""
    try:
        if request.method == 'POST':
            
            status = EventFormStatus_Phase02.objects.order_by('-updated_at').first()

            # if not Site_Permissions.user_has_permission(request.user, 'reg_form_control'):
            if not Site_Permissions.user_has_permission(request.user, 'reg_form_control') and status.is_published == False:
                return JsonResponse({
                'success': False,
                'message': 'Form has been turned off'
                })
            
            unique_code = request.POST.get('token')

            if unique_code:
                if not Form_Participant_Unique_Code_Phase_2.objects.filter(unique_code=unique_code).exists():
                    return JsonResponse({
                    'success': False,
                    'message': 'Incorrect token'
                    })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Token was not provided'
                    })

            # Get form data
            #Step 1
            name = request.POST.get('name')
            email = request.POST.get('email')
            contact_number = request.POST.get('contact_number')
            institution = request.POST.get('institution_name', '')
            # university_id = request.POST.get('uni_id','')

            membership_type = request.POST.get('membership_grade')
            if membership_type == 'student':
                ieee_id = request.POST.get('student_membership_id')
            elif membership_type == 'professional':
                ieee_id = request.POST.get('professional_membership_id')
            else:
                ieee_id = 'N/A'
            
            tshirt_size = request.POST.get('tshirt_size')

            # Step 2
            payment_method = 'Bkash'
            transaction_id = request.POST.get('transaction_id')
            comments = request.POST.get('comments')

            # Create and save participant
            participant = Form_Participant_Phase_2.objects.create(
                name=name,
                email=email,
                contact_number=contact_number,
                institution=institution,
                membership_type=membership_type,
                ieee_id=ieee_id,
                tshirt_size=tshirt_size,
                payment_method=payment_method,
                transaction_id=transaction_id,
                comments=comments,
            )

            send_registration_email_phase02(request, participant.name, participant.email)
            
            # Return success response
            return JsonResponse({
                'success': True,
                'message': 'Registration successful! Your participant ID is: ' + str(participant.id),
                'participant_id': participant.id
            })
                        
        else:
            # If not POST request, return error
            return JsonResponse({
                'success': False,
                'message': 'Invalid request method'
            })
    except Exception as e:
        # Return error response
        log_exception(e, request)
        return JsonResponse({
            'success': False,
            'message': 'Registration failed'
        })
    
@login_required
@permission_required('reg_form_control')
def download_excel(request):
    participants = Form_Participant_Phase_1.objects.all()
    
    # Prepare data for Sheet 1: Basic Information (without questionnaire answers)
    basic_data = []
    for participant in participants:
        basic_row = {
            'ID': participant.id,
            'Name': participant.name,
            'Email': participant.email,
            'Contact Number': participant.contact_number,
            'Is NSU Student': 'Yes' if participant.is_nsu_student else 'No',
            'Membership Type': participant.membership_type,
            'IEEE ID': participant.ieee_id,
            'University': participant.university,
            'University ID': participant.university_id,
            'Department': participant.department,
            'Comments': participant.comments,
            'Created At': participant.created_at.astimezone().strftime('%Y-%m-%d %H:%M:%S'),
        }
        basic_data.append(basic_row)
    
    # Prepare data for Sheet 2: Questionnaire Answers
    questionnaire_data = []
    for participant in participants:
        answers = participant.answers or {}
        questionnaire_row = {
            'ID': participant.id,
            'Name': participant.name,
            'Email': participant.email,
            'Contact': participant.contact_number,
            'Q1': answers.get('question1', ''),
            'Q2': answers.get('question2', ''),
            'Q3': answers.get('question3', ''),
        }
        questionnaire_data.append(questionnaire_row)

    # Prepare data for Sheet 3: Ambassasdor Codes
    ambassador_data = []
    for participant in participants:
        basic_row = {
            'ID': participant.id,
            'Name': participant.name,
            'Email': participant.email,
            'Membership Type': participant.membership_type,
            'University': participant.university,
            'Ambassador Code': participant.ambassador_code,
        }
        ambassador_data.append(basic_row)
    
    # Create Excel file with two sheets
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Sheet 1: Basic Information
        if basic_data:
            df_basic = pd.DataFrame(basic_data)
            df_basic.to_excel(writer, index=False, sheet_name='Basic Information')
        else:
            # Create empty sheet if no data
            empty_df = pd.DataFrame({'Message': ['No participants registered']})
            empty_df.to_excel(writer, index=False, sheet_name='Basic Information')
        
        # Sheet 2: Questionnaire Answers
        if questionnaire_data:
            df_questionnaire = pd.DataFrame(questionnaire_data)
            df_questionnaire.to_excel(writer, index=False, sheet_name='Questionnaire Answers')
        else:
            # Create empty sheet if no data
            empty_df = pd.DataFrame({'Message': ['No participants registered']})
            empty_df.to_excel(writer, index=False, sheet_name='Questionnaire Answers')
        
        # Sheet 3: Ambassador Codes
        if ambassador_data:
            df_ambassador = pd.DataFrame(ambassador_data)
            df_ambassador.to_excel(writer, index=False, sheet_name='Ambassador Codes')
        else:
            # Create empty sheet if no data
            empty_df = pd.DataFrame({'Message': ['No participants registered']})
            empty_df.to_excel(writer, index=False, sheet_name='Ambassador Codes')
    
    output.seek(0)
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="participants_data.xlsx"'
    return response

@login_required
@permission_required('view_reg_responses_list')
def response_table2(request):

    # ieee_member = 350
    # non_ieee_member = 450


    permissions = {
        'view_finance_info':Site_Permissions.user_has_permission(request.user, 'view_finance_info')
    }

    participants = Form_Participant_Phase_2.objects.all().order_by('created_at')
    total_registrations = Form_Participant_Phase_2.objects.count()

    # Query grouped stats
    stats = (
        Form_Participant_Phase_2.objects
        .values("membership_type")
        .annotate(total=Count("id"))
    )

    # Build summary dictionary
    summary = {}

    for entry in stats:
        membership = entry["membership_type"]
        summary[membership] = entry.get("total", 0)
    
    # summary['ieee_member_total'] = summary.get('member', 0) * ieee_member
    # summary['non_ieee_member_total'] = summary.get('non_ieee', 0) * non_ieee_member

    # total_amount = (summary['ieee_member_total']
    #                 +summary['non_ieee_member_total'])
    # total_amount = f"BDT {total_amount:,}"

    # summary['ieee_member_total'] = f"{summary['ieee_member_total']:,}"
    # summary['non_ieee_member_total'] = f"{summary['non_ieee_member_total']:,}"

    
    university_data = (
        Form_Participant_Phase_2.objects
        .exclude(institution__isnull=True)
        .exclude(institution='')
        .annotate(institution_sanitized=Trim('institution'))
        .values('institution_sanitized')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    # # Payment method counts
    # payment_counts = (
    #     Form_Participant_Phase_1.objects
    #     .values('payment_method')
    #     .annotate(total=Count('id'))
    # )
    # # Convert into dict like {"Bkash": 10, "Nagad": 15}
    # payment_summary = {entry['payment_method']: entry['total'] for entry in payment_counts}

    context = {
        'participants': participants,
        'registration_stats': summary,
        'university_data': university_data,
        # 'payment_summary': payment_summary,
        # 'total_amount': total_amount,
        'total_registrations':total_registrations,
        'has_perm':permissions
    }
    return render(request, 'phase2_response_table.html', context)

@login_required
@permission_required('view_reg_responses_list')
def response_table(request):

    permissions = {
        'view_finance_info':Site_Permissions.user_has_permission(request.user, 'view_finance_info')
    }

    participants = Form_Participant_Phase_1.objects.all().order_by('created_at')
    total_registrations = Form_Participant_Phase_1.objects.count()

    # Query grouped stats
    stats = (
        Form_Participant_Phase_1.objects
        .values("membership_type")
        .annotate(total=Count("id"))
    )

    # Build summary dictionary
    summary = {}

    for entry in stats:
        membership = entry["membership_type"]
        summary[membership] = entry.get("total", 0)
    
    university_data = (
        Form_Participant_Phase_1.objects
        .exclude(university__isnull=True)
        .exclude(university='')
        .annotate(university_sanitized=Trim('university'))
        .values('university_sanitized')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    context = {
        'participants': participants,
        'registration_stats': summary,
        'university_data': university_data,
        'total_registrations':total_registrations,
        'has_perm':permissions
    }
    return render(request, 'response_table.html', context)

@login_required
@permission_required('view_reg_response')
def view_response(request, id):
    partipant=Form_Participant_Phase_1.objects.get(id=id)
    context = {
        'participant': partipant
    }
    return render(request, 'participant_response.html', context)

from django.db.models import Case, When, Value, BooleanField

@login_required
@permission_required('reg_form_control')
def save_selected_phase01(request):

    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            selected_ids = data.get('selected_ids')

            Form_Participant_Phase_1.objects.update(
                is_selected=Case(
                    When(id__in=selected_ids, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                )
            )
            return JsonResponse({'message':'Participants selection updated successfully!', 'status':'success'})
        else:
            return JsonResponse({'message':'Invalid request header', 'status':'error'})
    except:
        return JsonResponse({'message':'Error!', 'status':'error'})
    
@login_required
def send_phase02_email(request):
    try:
        if request.method == 'POST':
            form_participants = Form_Participant_Phase_1.objects.filter(is_selected=True)
            
            send_participant_phase02_email(request, form_participants)
            
            return JsonResponse({'message':'Successfully emailed to all participants!', 'status':'success'})
        else:
            return JsonResponse({'message':'Invalid request header', 'status':'error'})
    except:
        return JsonResponse({'message':'Error!', 'status':'error'})
    
@login_required
@permission_required('view_reg_response')   
def view_response2(request, id):
    partipant=Form_Participant_Phase_2.objects.get(id=id)
    context = {
        'participant': partipant
    }
    return render(request, 'phase2_participant_response.html', context)