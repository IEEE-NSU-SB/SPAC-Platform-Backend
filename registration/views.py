import csv
import pandas as pd
from io import BytesIO
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from access_ctrl.decorators import permission_required
from access_ctrl.utils import Site_Permissions
from system_administration.utils import log_exception
from emails.views import send_registration_email
from django.db.models import Count
from django.db.models.functions import Trim

from .models import EventFormStatus, Form_Participant

def _get_publish_status() -> bool:
    status = EventFormStatus.objects.order_by('-updated_at').first()
    return bool(status and status.is_published)

def registration_form(request):
    """Display the registration form for general users. Hidden if not published."""
    # If staff/superuser hits the user URL, send them to the admin view
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('registration:registration_admin')

    registration_count = Form_Participant.objects.count()
    registration_closed = registration_count >= 10000
    context = {
        'is_staff_view': False,
        'is_published': _get_publish_status(),
        'registration_closed': registration_closed,
    }
    return render(request, 'form.html', context)

@login_required
@permission_required('reg_form_control')
def registration_admin(request):
    """Staff-only admin view to manage and preview the form regardless of publish state."""

    registration_count = Form_Participant.objects.count()

    permisions = {
        'reg_form_control':Site_Permissions.user_has_permission(request.user, 'reg_form_control'),
        'view_reg_responses_list':Site_Permissions.user_has_permission(request.user, 'view_reg_responses_list'),
        'view_finance_info':Site_Permissions.user_has_permission(request.user, 'view_finance_info'),
        'view_qr_dashboard':Site_Permissions.user_has_permission(request.user, 'view_qr_dashboard'),
    }

    context = {
        'is_staff_view': True,
        'is_published': _get_publish_status(),
        'registration_count':registration_count,
        'has_perm': permisions
    }
    return render(request, 'form.html', context)

def registration_redirect(request):
    if request.user.is_authenticated:
        return redirect('registration:registration_admin')
    else:
        return redirect('registration:registration_form')

@login_required
@require_POST
def toggle_publish(request):
    """Toggle EventFormStatus.is_published and return current status."""
    status = EventFormStatus.objects.order_by('-updated_at').first()
    if not status:
        status = EventFormStatus.objects.create(is_published=True)
    else:
        status.is_published = not status.is_published
        status.save(update_fields=['is_published'])
    return JsonResponse({'success': True, 'is_published': status.is_published})

def submit_form(request):
    """Handle form submission and save participant data"""
    try:
        if request.method == 'POST':
            
            status = EventFormStatus.objects.order_by('-updated_at').first()
            #TEMPORARY
            # if not Site_Permissions.user_has_permission(request.user, 'reg_form_control') and status.is_published == False:
            if not Site_Permissions.user_has_permission(request.user, 'reg_form_control'):
                return JsonResponse({
                'success': False,
                'message': 'Registration failed'
                })

            # Get form data
            #Step 1
            name = request.POST.get('name')
            email = request.POST.get('email')
            contact_number = request.POST.get('contact_number')
            is_nsu_student = request.POST.get('is_student_bool')
            nsu_email = None
            major = ''
            department = ''
            if is_nsu_student == 'True':
                university = 'North South University'
                university_id = request.POST.get('nsu_id','')
                nsu_email = request.POST.get('nsu_email', None)
                department = request.POST.get('department','')
                current_year = request.POST.get('current_year', '')
            else:
                university = request.POST.get('uni_name', '')
                university_id = request.POST.get('uni_id','')
                current_year = request.POST.get('other_current_year', '')
                major = request.POST.get('major', '')

            membership_type = request.POST.get('membership_type')
            ieee_id = request.POST.get('ieee_id')

            # Step 2
            # Collect questionnaire answers
            answers = {
                'question1': request.POST.get('question1', ''),
                'question2': request.POST.get('question2', ''),
            }
            ambassador_code = request.POST.get('ambassador_code', '')
            participant_type = request.POST.get('participant_type', '')

            # Step 3
            registering_for_team = request.POST.get('registering_for_team', '')
            team_member_count = request.POST.get('team_mem_count', '')
            mem_name_1 = request.POST.get('mem_name_1', '')
            mem_uni_name_1 = request.POST.get('mem_uni_name_1', '')
            mem_uni_id_1 = request.POST.get('mem_uni_id_1', '')
            mem_name_2 = request.POST.get('mem_name_2', '')
            mem_uni_name_2 = request.POST.get('mem_uni_name_2', '')
            mem_uni_id_2 = request.POST.get('mem_uni_id_2', '')

            # Step 4
            payment_method = request.POST.get('payment_method')
            transaction_id = request.POST.get('transaction_id')

            # Create and save participant
            participant = Form_Participant.objects.create(
                name=name,
                email=email,
                contact_number=contact_number,
                membership_type=membership_type,
                ieee_id=ieee_id,
                nsu_email=nsu_email,
                university=university,
                department=department,
                university_id=university_id,
                payment_method=payment_method,
                transaction_id=transaction_id,
                answers=answers,
                current_year=current_year,
                is_nsu_student = is_nsu_student,
                ambassador_code=ambassador_code,
                participant_type=participant_type,
                major=major,
                registering_for_team=registering_for_team,
                team_member_count=team_member_count,
                team_mem_1_name=mem_name_1,
                team_mem_1_university=mem_uni_name_1,
                team_mem_1_university_id=mem_uni_id_1,
                team_mem_2_name=mem_name_2,
                team_mem_2_university=mem_uni_name_2,
                team_mem_2_university_id=mem_uni_id_2,
            )

            # send_registration_email(participant.name, participant.email)
            
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
    participants = Form_Participant.objects.all()
    
    # Prepare data for Sheet 1: Basic Information (without questionnaire answers)
    basic_data = []
    for participant in participants:
        basic_row = {
            'ID': participant.id,
            'Name': participant.name,
            'Email': participant.email,
            'Contact Number': participant.contact_number,
            'Is Student': 'Yes' if participant.is_student else 'No',
            'Membership Type': participant.membership_type,
            'IEEE ID': participant.ieee_id,
            'Profession':participant.profession,
            'Affiliation':participant.affiliation,
            'Designation':participant.designation,
            'University': participant.university,
            'Department': participant.department,
            'University ID': participant.university_id,
            'Payment Method': participant.payment_method,
            'Transaction ID': participant.transaction_id,
            'T-shirt Size': participant.tshirt_size,
            'Comments': participant.comments,
            'Created At': participant.created_at.strftime('%Y-%m-%d %H:%M:%S'),
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
            'Q4': answers.get('question4', ''),
        }
        questionnaire_data.append(questionnaire_row)
    
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
    
    output.seek(0)
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="participants_data.xlsx"'
    return response

@login_required
@permission_required('view_reg_responses_list')
def response_table(request):

    student_member_amount = 410
    student_non_member_amount = 510
    not_student_member_amount = 810
    not_student_non_member_amount = 910

    permissions = {
        'view_finance_info':Site_Permissions.user_has_permission(request.user, 'view_finance_info')
    }

    participants = Form_Participant.objects.all().order_by('created_at')

    # Query grouped stats
    stats = (
        Form_Participant.objects
        .values("is_nsu_student", "membership_type")
        .annotate(total=Count("id"))
    )

    # Build summary dictionary
    summary = {}

    for entry in stats:
        is_student = "student" if entry["is_nsu_student"] else "not_student"
        membership = entry["membership_type"]

        key = f"{is_student}_{membership}"
        summary[key] = entry.get("total", 0)
    
    summary['student_member_amount_total'] = summary.get('student_member', 0) * student_member_amount
    summary['student_non_ieee_amount_total'] = summary.get('student_non_ieee', 0) * student_non_member_amount
    summary['not_student_member_amount_total'] = summary.get('not_student_member', 0) * not_student_member_amount
    summary['not_student_non_ieee_amount_total'] = summary.get('not_student_non_ieee', 0) * not_student_non_member_amount

    total_amount = (summary['student_member_amount_total']
                    +summary['student_non_ieee_amount_total'] 
                    +summary['not_student_member_amount_total']
                    +summary['not_student_non_ieee_amount_total'])
    total_amount = f"BDT {total_amount:,}"

    summary['student_member_amount_total'] = f"{summary['student_member_amount_total']:,}"
    summary['student_non_ieee_amount_total'] = f"{summary['student_non_ieee_amount_total']:,}"
    summary['not_student_member_amount_total'] = f"{summary['not_student_member_amount_total']:,}"
    summary['not_student_non_ieee_amount_total'] = f"{summary['not_student_non_ieee_amount_total']:,}"

    
    university_data = (
        Form_Participant.objects
        .exclude(university__isnull=True)
        .exclude(university='')
        .annotate(university_sanitized=Trim('university'))
        .values('university_sanitized')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    # Payment method counts
    payment_counts = (
        Form_Participant.objects
        .values('payment_method')
        .annotate(total=Count('id'))
    )
    # Convert into dict like {"Bkash": 10, "Nagad": 15}
    payment_summary = {entry['payment_method']: entry['total'] for entry in payment_counts}

    context = {
        'participants': participants,
        'registration_stats': summary,
        'university_data': university_data,
        'payment_summary': payment_summary,
        'total_amount': total_amount,
        'has_perm':permissions
    }
    return render(request, 'response_table.html', context)

@login_required
@permission_required('view_reg_response')
def view_response(request, id):
    partipant=Form_Participant.objects.get(id=id)
    context = {
        'participant': partipant
    }
    return render(request, 'form_response.html', context)