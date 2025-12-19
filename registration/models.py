from django.db import models

class EventFormStatus(models.Model):
    """Control publish/unpublish of the registration form"""
    is_published = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Event Form Status"

    def __str__(self):
        return "Published" if self.is_published else "Unpublished"
    
class University(models.Model):

    name = models.CharField(max_length=200, blank=False, null=False)

    class Meta:
        verbose_name = 'University'

    def __str__(self):
        return self.name
    
class Form_Participant_Phase_1(models.Model):

    MEMBERSHIP_CHOICES = [
        ('non_ieee', 'Non IEEE Member'),
        ('member', 'IEEE Member')
    ]

    # Step 1
    name = models.CharField(max_length=200, null=False, blank=False)
    email = models.EmailField(unique=False, null=False, blank=False)
    contact_number = models.CharField(max_length=20, null=False, blank=False)
    membership_type = models.CharField(max_length=10, choices=MEMBERSHIP_CHOICES, null=False, blank=False, default='non_ieee')
    is_nsu_student = models.BooleanField(null=False, blank=False, default=False)
    ieee_id = models.CharField(max_length=50, blank=True, null=True)
    university = models.CharField(max_length=200, null=True, blank=True, default='')
    department = models.CharField(max_length=200, null=True, blank=True,default='')
    university_id = models.CharField(max_length=50, null=True, blank=True,default='')
    ambassador_code = models.CharField(max_length=15, blank=True, null=True, default='')

    # Step 2
    # Store all questionnaire answers in JSON
    answers = models.JSONField(default=dict)
    comments = models.TextField(null=True, blank=True, default='')

    is_selected = models.BooleanField(null=False, blank=False, default=False)
    is_phase_2_email_sent = models.BooleanField(null=False, blank=False, default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Participant Form (Phase 1)'

    def __str__(self):
        return f"{self.name} - {self.email}"
    
class Form_Participant_Unique_Code_Phase_2(models.Model):

    participant = models.ForeignKey(Form_Participant_Phase_1, null=False, blank=False, on_delete=models.CASCADE)
    unique_code = models.CharField(null=False, blank=False, max_length=50, unique=True)
    is_active = models.BooleanField(null=False, blank=False, default=False)

    class Meta:
        verbose_name = 'Unique Code for Phase 2'

    def __str__(self):
        return self.participant.name
    
# class Form_Participant_Phase_2(models.Model):

#     MEMBERSHIP_CHOICES = [
#         ("student_member", "IEEE Student Member"),
#         ("member", "IEEE Member"),
#         ("non_ieee", "Non-IEEE Member"),
#     ]

#     PAYMENT_CHOICES = [
#         ("Bkash","Bkash"),
#         ("Nagad","Nagad"),
#         ("Not Set","Not Set"),
#     ]

#     SIZE_CHOICES = [("S","S"),("M","M"),("L","L"),("XL","XL"),("2XL","2XL"),("3XL","3XL"),("4XL","4XL")]

#     # Step 1
#     name = models.CharField(max_length=200, null=False, blank=False)
#     email = models.EmailField(unique=False, null=False, blank=False)
#     contact_number = models.CharField(max_length=20, null=False, blank=False)
#     institution = models.CharField(max_length=200, null=True, blank=True, default='')

#     # Step 2
#     membership_type = models.CharField(max_length=20, choices=MEMBERSHIP_CHOICES)

#     # Step 3 & 4
#     ieee_id = models.CharField(max_length=50, blank=True, null=True, default='')

#     # Step 5
#     payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default="Not Set")
#     transaction_id = models.CharField(max_length=100, null=True, blank=True, default='')

#     # Step 6
#     tshirt_size = models.CharField(max_length=5, choices=SIZE_CHOICES, null=True, blank=True)
#     comments = models.TextField(null=True, blank=True, default='')

#     class Meta:
#         verbose_name = 'Participant Form (Phase 2)'

#     def __str__(self):
#         return f"{self.name} - {self.email}"