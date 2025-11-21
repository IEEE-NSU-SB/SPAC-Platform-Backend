from django.db import models

class EventFormStatus(models.Model):
    """Control publish/unpublish of the registration form"""
    is_published = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Event Form Status"

    def __str__(self):
        return "Published" if self.is_published else "Unpublished"


class Form_Participant(models.Model):
    MEMBERSHIP_CHOICES = [
        ("member", "IEEE Member"),
        ("non_ieee", "Non-IEEE Member"),
    ]
    JOIN_CHOICES = [
        ('participant', 'Participant'),
        ('participant_pstpre_contestant', 'Participant and Poster Presentation Contestant'),
        ('participant_pwrolmp_contestant', 'Participant and Power Olympiad Contestant'),
    ]
    TEAM_MEMBER_COUNT_CHOICES = [
        ('two', 'Two'),
        ('three', 'Three'),
    ]
    SIZE_CHOICES = [("S","S"),("M","M"),("L","L"),("XL","XL"),("2XL","2XL"),("3XL","3XL"),("4XL","4XL")]

    is_nsu_student = models.BooleanField(default=False)

    # Step 1
    name = models.CharField(max_length=200, null=False, blank=False)
    email = models.EmailField(unique=False, null=False, blank=False)
    nsu_email = models.EmailField(null=True, blank=True)
    contact_number = models.CharField(max_length=20, null=False, blank=False)
    university = models.CharField(max_length=200, null=True, blank=True, default='')
    university_id = models.CharField(max_length=50, null=True, blank=True,default='')
    department = models.CharField(max_length=200, null=True, blank=True,default='')
    major = models.CharField(max_length=50, null=True, blank=True, default='')
    membership_type = models.CharField(max_length=20, choices=MEMBERSHIP_CHOICES)
    ieee_id = models.CharField(max_length=50, blank=True, null=True)
    current_year = models.CharField(max_length=8, null=True, blank=True, default='')

    # Step 2
    # Store all questionnaire answers in JSON
    answers = models.JSONField(default=dict)
    ambassador_code = models.CharField(max_length=15, blank=True, null=True, default='')
    participant_type = models.JSONField(default=list)

    # Step 3
    registering_for_team = models.BooleanField(blank=False, null=False, default=False)
    team_member_count = models.CharField(max_length=5, choices=TEAM_MEMBER_COUNT_CHOICES, null=True, blank=True)
    team_mem_1_name = models.CharField(max_length=200, null=True, blank=True, default='')
    team_mem_1_university = models.CharField(max_length=200, null=True, blank=True, default='')
    team_mem_1_university_id = models.CharField(max_length=50, null=True, blank=True, default='')
    team_mem_2_name = models.CharField(max_length=200, null=True, blank=True, default='')
    team_mem_2_university = models.CharField(max_length=200, null=True, blank=True, default='')
    team_mem_2_university_id = models.CharField(max_length=50, null=True, blank=True, default='')

    # Step 4
    payment_method = models.CharField(max_length=20, choices=[("Bkash","Bkash")], default="Bkash")
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    comments = models.TextField(null=True, blank=True, default='')

    tshirt_size = models.CharField(max_length=5, choices=SIZE_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name="Form Participant"

    def __str__(self):
        return f"{self.name} - {self.email}"