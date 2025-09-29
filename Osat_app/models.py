import random
import string
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.timezone import now
from multiselectfield import MultiSelectField

User = get_user_model()


# for store the  passord reset token
class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.token}"


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Province(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name="provinces"
    )

    class Meta:
        unique_together = ("name", "country")

    def __str__(self):
        return f"{self.name}, {self.country.name}"


class school(models.Model):
    school_name = models.CharField(max_length=225, unique=True, null=True)
    contact_details = models.CharField(max_length=225, null=True)
    address = models.CharField(max_length=225, null=True)
    province = models.CharField(max_length=225, null=True)
    country = models.CharField(max_length=225, null=True)

    def __str__(self):
        return self.school_name or ""


class Participant(models.Model):
    reference_number = models.CharField(max_length=20, unique=True)

    first_screening = models.BooleanField(default=False)
    second_screening = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="participants",
        null=True,
        blank=True,
    )
    comprehensive_eye_exam = models.BooleanField(default=False)
    measure_visual_acuity = models.BooleanField(default=False)
    diagnosis_management = models.BooleanField(default=False)
    dispensing = models.BooleanField(default=False)

    spectacle_wearing_history = models.BooleanField(default=False)
    family_history = models.BooleanField(default=False)
    surgery_treatment_history = models.BooleanField(default=False)
    current_medical_treatment = models.BooleanField(default=False)
    refraction_spectacle_presentation = models.BooleanField(default=False)
    other_medical_issues = models.BooleanField(default=False)
    refraction_and_examination = models.BooleanField(default=False)

    surgery_history = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return f"{self.reference_number} - {self.name}"


# class Firstscreening(models.Model):  # Class name should be PascalCase
#     reference_number = models.CharField(max_length=20, unique=True, blank=True)  # Moved here
#     grade = models.CharField(max_length=10, null=True, blank=True)
#     gender = models.CharField(
#         max_length=10,
#         choices=[('male', 'Male'), ('female', 'Female')],
#         null=True,
#         blank=True
#     )
#     age = models.IntegerField(null=True, blank=True)  # Ensures non-negative age
#     wears_spectacles = models.CharField(
#         max_length=100,
#         choices=[
#             ('Has spectacles and is currently wearing them', 'Has spectacles and is currently wearing them'),
#             ('Has spectacles but not wearing them', 'Has spectacles but not wearing them'),
#             ('Does not wear spectacles', 'Does not wear spectacles'),
#             ('Has spectacles but not wearing however has them in their possession', 'Has spectacles but not wearing however has them in their possession '),
#             ('Has spectacles but not wearing and not in their possession', 'Has spectacles but not wearing and not in their possession '),
#             ('Has previously worn spectacles but no longer has spectacles', 'Has previously worn spectacles but no longer has spectacles '),
#             ('Has never worn spectacles before', 'Has never worn spectacles before ')
#         ],
#         null=True,
#         blank=True
#     )
#     created_at = models.DateTimeField(default=now)
#     first_screening = models.BooleanField(default=True)

#     def save(self, *args, **kwargs):
#         """Generate a unique reference number if it doesn't exist."""
#         if not self.reference_number:
#             self.reference_number = f"FS{uuid.uuid4().hex[:6].upper()}"  # 'FS' for First Screening
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.reference_number} - {self.grade or 'Unknown'} - {self.gender or 'Unknown'} - {self.age or 'N/A'}"


# class Firstscreening(models.Model):
#     grade = models.CharField(max_length=10, null=True, blank=True)
#     gender = models.CharField(
#         max_length=10,
#         choices=[('male', 'Male'), ('female', 'Female')],
#         null=True,
#         blank=True
#     )
#     age = models.IntegerField(null=True, blank=True)
#     wears_spectacles = models.CharField(
#         max_length=100,
#         choices=[
#             ('Has spectacles and is currently wearing them', 'Has spectacles and is currently wearing them'),
#             ('Has spectacles but not wearing them', 'Has spectacles but not wearing them'),
#             ('Does not wear spectacles', 'Does not wear spectacles'),
#             ('Has spectacles but not wearing however has them in their possession', 'Has spectacles but not wearing however has them in their possession'),
#             ('Has spectacles but not wearing and not in their possession', 'Has spectacles but not wearing and not in their possession'),
#             ('Has previously worn spectacles but no longer has spectacles', 'Has previously worn spectacles but no longer has spectacles'),
#             ('Has never worn spectacles before', 'Has never worn spectacles before')
#         ],
#         null=True,
#         blank=True
#     )
#     created_at = models.DateTimeField(default=now)
#     first_screening = models.BooleanField(default=True)
#     first_screening_passed = models.BooleanField(default=False)
#     school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)

#     def __str__(self):
#         return f"First Screening - {self.grade or 'Unknown'} - {self.gender or 'Unknown'} - {self.age or 'N/A'}"


class Firstscreening(models.Model):
    grade = models.CharField(max_length=10, null=True, blank=True)

    gender = models.CharField(
        max_length=10,
        choices=[("male", "Male"), ("female", "Female")],
        null=True,
        blank=True,
    )

    age = models.IntegerField(null=True, blank=True)

    wears_spectacles = models.CharField(
        max_length=100,
        choices=[
            (
                "Has spectacles and is currently wearing them",
                "Has spectacles and is currently wearing them",
            ),
            (
                "Has spectacles but not wearing them",
                "Has spectacles but not wearing them",
            ),
            ("Does not wear spectacles", "Does not wear spectacles"),
            (
                "Has spectacles but not wearing however has them in their possession",
                "Has spectacles but not wearing however has them in their possession",
            ),
            (
                "Has spectacles but not wearing and not in their possession",
                "Has spectacles but not wearing and not in their possession",
            ),
            (
                "Has previously worn spectacles but no longer has spectacles",
                "Has previously worn spectacles but no longer has spectacles",
            ),
            ("Has never worn spectacles before", "Has never worn spectacles before"),
        ],
        null=True,
        blank=True,
    )

    reference_number = models.CharField(
        max_length=100, unique=True, null=True, blank=True
    )
    # first_screening_passed = models.BooleanField(default=False)
    # school = models.ForeignKey('School', on_delete=models.CASCADE, null=True, blank=True)
    school = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(default=now)
    # name = models.CharField(max_length=255, null=True)
    # country = models.ForeignKey('Country', on_delete=models.CASCADE, null=True, blank=True)
    # province = models.ForeignKey('Province', on_delete=models.CASCADE, null=True)
    # country = models.CharField(max_length=255, null=True, blank=True)
    # province = models.CharField(max_length=255, null=True, blank=True)
    # address = models.TextField(null=True, blank=True)
    # contact_person = models.CharField(max_length=255, null=True, blank=True)
    # contact_details = models.CharField(max_length=100, null=True, blank=True)
    referral_clinic = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = f"SS-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"First Screening - {self.grade or 'Unknown'} - {self.gender or 'Unknown'} - {self.age or 'N/A'}"


class Comprehensive(models.Model):
    # reference_number = models.CharField(max_length=20)
    status = models.CharField(
        max_length=10,
        null=True,
        blank=True,  # Allows blank values
        choices=[("Yes", "Yes"), ("No", "No"), ("Not Known", "Not Known")],
    )

    def __str__(self):
        return self.status or "Unknown"


# class SecondScreening(models.Model):
#     reference_number = models.CharField(max_length=20)   # Required & Indexed
#     name = models.CharField(max_length=100, blank=True, default="")
#     surname = models.CharField(max_length=100, blank=True, default="")
#     contact_name = models.CharField(max_length=100, blank=True, default="")
#     relationship = models.CharField(max_length=100, blank=True, default="")
#     contact_number = models.CharField(max_length=15, blank=True, default="")  # Supports international numbers
#     second_screening = models.BooleanField(default=False)

#     def __str__(self):
#         return f"{self.name} {self.surname}".strip() or "Unnamed Participant"

# def generate_participant_number(prefix):
#     number = ''.join(random.choices(string.digits, k=random.choice([5, 6])))
#     return f"{prefix.upper()}{number}"

# class SecondScreening(models.Model):
#     reference_number = models.CharField(max_length=20,null=True)
#     participant_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
#     name = models.CharField(max_length=100, blank=True, default="")
#     surname = models.CharField(max_length=100, blank=True, default="")
#     contact_name = models.CharField(max_length=100, blank=True, default="")
#     relationship = models.CharField(max_length=100, blank=True, default="")
#     contact_number = models.CharField(max_length=15, blank=True, default="")  # Supports international numbers
#     second_screening = models.BooleanField(default=False)

#     def save(self, *args, **kwargs):
#         if not self.participant_number:
#             prefix = self.reference_number[:4]  # Use part of reference_number or define your own logic
#             new_id = generate_participant_number(prefix)

#             # Ensure uniqueness
#             while SecondScreening.objects.filter(participant_number=new_id).exists():
#                 new_id = generate_participant_number(prefix)

#             self.participant_number = new_id

#         super().save(*args, **kwargs)


class SecondScreening(models.Model):
    reference_number = models.CharField(
        max_length=100, unique=True, blank=True, null=True
    )
    # contact_name = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    relationship = models.CharField(max_length=50)
    contact_first_name = models.CharField(max_length=100, null=True, blank=True)
    contact_surname = models.CharField(max_length=100, null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="second_screenings",
        null=True,
        blank=True,
    )
    # refCount = models.IntegerField(null=True, blank=True)
    # refPrefix = models.CharField(max_length=50, null=True, blank=True)
    # file = models.FileField(upload_to='eye_tests/', null=True, blank=True)
    # second_screening = models.BooleanField(default=False, null=True, blank=True)
    school = models.CharField(max_length=255, null=True, blank=True)
    # school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)

    # def save(self, *args, **kwargs):
    #     if not self.reference_number:
    #         self.reference_number = f"SS-{uuid.uuid4().hex[:8].upper()}"  # Example: SS-3FA7C9D1
    #     super().save(*args, **kwargs)


class Dispensing(models.Model):
    reference_number = models.CharField(max_length=20)
    frame_choice = models.CharField(max_length=50, null=True, blank=True)
    # glasses_ordered = models.BooleanField(default=False)
    # glasses_ready = models.BooleanField(default=False)
    # glasses_received = models.BooleanField(default=False)
    # glasses_dispensed = models.BooleanField(default=False)
    # notification_sent = models.BooleanField(default=False)
    # age = models.IntegerField(blank=True)  # Default age to avoid migration issues
    lenses_type = models.CharField(max_length=50, null=True, blank=True)
    pd_distance = models.CharField(max_length=10, null=True, blank=True)
    pd_near = models.CharField(max_length=10, null=True, blank=True)
    frame_distance = models.CharField(max_length=10, null=True, blank=True)
    frame_near = models.CharField(max_length=10, null=True, blank=True)
    frame_bifocal = models.CharField(max_length=10, null=True, blank=True)
    fitting_height_re = models.CharField(max_length=10, null=True, blank=True)
    fitting_height_le = models.CharField(max_length=10, null=True, blank=True)
    comments = models.CharField(max_length=255, null=True, blank=True)
    provision_date = models.DateTimeField(auto_now_add=True)
    provision_status = models.CharField(max_length=50, null=True, blank=True)
    dispensing = models.BooleanField(default=True)

    def __str__(self):
        return f"Dispensing Record: {self.reference_number}"


class InitialEyeTest(models.Model):
    TEST_RESULTS = [("pass", "Pass"), ("fail", "Fail")]

    reference_number = models.CharField(max_length=50, unique=True)
    test_type = models.CharField(max_length=50, default="Snellen E Chart")
    left_eye_score = models.FloatField()
    right_eye_score = models.FloatField()
    test_result = models.CharField(max_length=10, choices=TEST_RESULTS)

    def __str__(self):
        return f"{self.reference_number} - {self.test_result}"


class RetestEyeTest(models.Model):
    TEST_RESULTS = [("pass", "Pass"), ("fail", "Fail")]

    reference_number = models.CharField(max_length=50, unique=True)
    test_type = models.CharField(max_length=50, default="Snellen E Chart")
    test_result = models.CharField(max_length=10, choices=TEST_RESULTS)

    def __str__(self):
        return f"{self.reference_number} - {self.test_result}"


class ComprehensiveEyeTest(models.Model):
    TEST_RESULTS = [("pass", "Pass"), ("fail", "Fail")]

    reference_number = models.CharField(max_length=50, unique=True)
    left_eye_score = models.FloatField()
    right_eye_score = models.FloatField()
    additional_ocular_complaints = models.BooleanField(default=False)
    test_result = models.CharField(max_length=10, choices=TEST_RESULTS)

    def __str__(self):
        return f"{self.reference_number} - {self.test_result}"


class RefractionExamination(models.Model):
    reference_number = models.CharField(max_length=50, unique=True)
    chief_complaint = models.CharField(
        max_length=255,
        choices=[
            ("NO_COMPLAINTS", "No Complaints"),
            ("ITCHING", "Itching of eye/s"),
            ("HEADACHE", "Headaches"),
            ("WATERING", "Watering of eye/s"),
            ("REDNESS", "Redness of eye/s"),
            ("BLURRING", "Blurring of vision"),
            ("PAIN", "Pain in eye/s"),
            ("DISCHARGE", "Discharge from eye/s"),
            ("EYE_STRAIN", "Eye strain"),
            ("SWELLING", "Swelling of eye/s"),
            ("IRRITATION", "Irritation of eye/s"),
            ("INJURY", "Injury to eye/s"),
            ("FOREIGN_BODY", "Foreign body in eye/s"),
            ("PHOTOPHOBIA", "Photophobia"),
            ("DIPLOPIA", "Diplopia"),
            ("POLYOPIA", "Polyopia"),
            ("DROOPING_LID", "Drooping of lid/s"),
            ("SQUINT", "Squint"),
            ("SQUEEZING_EYE", "Squeezing eye"),
            ("ABNORMAL_HEAD_POSTURE", "Abnormal head posture"),
            ("FLOATERS", "Floaters/black spots"),
            ("FLASHES", "Flashes of light"),
        ],
    )

    eye = models.CharField(
        max_length=10,
        choices=[
            ("LEFT EYE", "Left Eye"),
            ("RIGHT EYE", "Right Eye"),
            ("BOTH EYES", "Both Eyes"),
        ],
    )

    duration = models.IntegerField()
    additional_ocular_complaint = models.BooleanField(default=False)
    ocular_alignment_remarks = models.TextField(blank=True, null=True)
    refraction_and_examination = models.BooleanField(default=True)

    def __str__(self):
        return f"Refraction Examination - {self.reference_number}"


class Diagnosis(models.Model):
    reference_number = models.CharField(max_length=50, unique=True)
    # follow_up_required = models.BooleanField(default=False)
    # follow_up_date = models.DateField(null=True, blank=True)
    # diagnosis = models.CharField(max_length=255, null=True, blank=True)
    refractive_error_type = models.CharField(max_length=100, null=True, blank=True)
    affected_eye = models.CharField(max_length=100, null=True, blank=True)
    ocular_condition = models.CharField(max_length=100, null=True, blank=True)
    management_plan = models.CharField(max_length=100, null=True, blank=True)
    diagnosis_management = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.reference_number}"


class SpectacleHistory(models.Model):
    reference_number = models.CharField(max_length=50, primary_key=True)

    wears_spectacles = models.BooleanField(null=True, blank=True)
    wearing_duration = models.CharField(max_length=20, null=True, blank=True)

    has_glasses = models.BooleanField(null=True, blank=True)

    lens_condition = models.CharField(
        max_length=20,
        choices=[
            ("good", "Good"),
            ("scratched", "Scratched"),
            ("dirty", "Dirty"),
            ("broken", "Broken"),
        ],
        null=True,
        blank=True,
    )

    lens_material = models.CharField(
        max_length=10,
        choices=[("glass", "Glass"), ("plastic", "Plastic")],
        null=True,
        blank=True,
    )

    lens_coating = models.CharField(
        max_length=20,
        choices=[
            ("hard coat", "Hard Coat"),
            ("arc", "ARC"),
            ("blue coat", "Blue Coat"),
        ],
        null=True,
        blank=True,
    )

    lens_type = models.CharField(
        max_length=20,
        choices=[
            ("single vision", "Single Vision"),
            ("bifocal", "Bifocal"),
            ("multifocal", "Multifocal"),
            ("lenticular", "Lenticular"),
        ],
        null=True,
        blank=True,
    )

    refractive_index = models.FloatField(
        null=True,
        blank=True,
        choices=[(1.5, "1.5"), (1.56, "1.56"), (1.67, "1.67"), (1.71, "1.71")],
    )

    frame_condition = models.CharField(max_length=20, null=True, blank=True)
    frame_fit = models.BooleanField(null=True, blank=True)
    frame_bent = models.BooleanField(null=True, blank=True)
    frame_broken = models.BooleanField(null=True, blank=True)
    frame_good_condition = models.BooleanField(null=True, blank=True)

    glasses_change_duration = models.CharField(max_length=20, null=True, blank=True)

    glasses_source = models.CharField(
        max_length=50,
        choices=[
            ("eye hospital", "Eye Hospital"),
            ("vision center", "Vision Center"),
            ("optical store", "Optical Store"),
            ("eye camp", "Eye Camp"),
            ("school eye health event", "School Eye Health Event"),
            ("dont know", "Don't Know"),
            ("other", "Other"),
        ],
        null=True,
        blank=True,
    )

    chose_own_frame = models.BooleanField(null=True, blank=True)  # Yes/No

    satisfaction_level = models.CharField(
        max_length=20,
        choices=[
            ("very happy", "Very Happy"),
            ("happy", "Happy"),
            ("ok", "OK"),
            ("unhappy", "Unhappy"),
            ("very unhappy", "Very Unhappy"),
        ],
        null=True,
        blank=True,
    )

    spectacle_wearing_history = models.BooleanField(default=True)

    def __str__(self):
        return f"Record {self.reference_number}"


class SurgeryTreatmentHistory(models.Model):
    EYE_CHOICES = [("Right", "Right Eye"), ("Left", "Left Eye"), ("Both", "Both")]

    SURGERY_CHOICES = [
        ("TRAUMA", "Trauma"),
        ("CATARACT", "Cataract"),
        ("SQUINT", "Squint"),
        ("LID", "Lid"),
        ("OTHER", "Other"),
        ("NONE", "None"),
    ]

    reference_number = models.CharField(max_length=50, primary_key=True)
    surgery_done = models.BooleanField(default=False)

    treated_eye = models.CharField(max_length=10, choices=EYE_CHOICES, default="Both")
    surgery_type = models.CharField(max_length=50, blank=True, null=True)
    other_surgery_details = models.CharField(max_length=100, blank=True, null=True)

    # Fields to match the required format
    left_eye_trauma = models.BooleanField(default=False)
    left_eye_cataract = models.BooleanField(default=False)
    left_eye_squint = models.BooleanField(default=False)
    left_eye_lid = models.BooleanField(default=False)
    left_eye_other = models.BooleanField(default=False)
    left_eye_none = models.BooleanField(default=False)

    right_eye_trauma = models.BooleanField(default=False)
    right_eye_cataract = models.BooleanField(default=False)
    right_eye_squint = models.BooleanField(default=False)
    right_eye_lid = models.BooleanField(default=False)
    right_eye_other = models.BooleanField(default=False)
    right_eye_none = models.BooleanField(default=False)
    surgery_treatment_history = models.BooleanField(default=True)

    def __str__(self):
        return (
            f"Record {self.reference_number} - {self.treated_eye} - {self.surgery_type}"
        )


# class MedicalIssueResponse(models.Model):
#     reference_number = models.CharField(max_length=50)
#     name = models.CharField(max_length=100)
#     age = models.IntegerField()
#     grade = models.CharField(max_length=20)
#     school = models.CharField(max_length=255)
#     medical_issue = models.CharField(
#         max_length=10,
#         choices=[("Yes", "Yes"), ("No", "No"), ("Not Known", "Not Known")]
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
#     other_medical_issues = models.BooleanField(default=True)


#     def __str__(self):
#         return f"{self.reference_number} - {self.medical_issue}"


class OtherMedicalIssueResponse(models.Model):
    reference_number = models.CharField(max_length=50)
    medical_issue = models.CharField(
        max_length=10,
        choices=[("Yes", "Yes"), ("No", "No"), ("Not Known", "Not Known")],
    )
    # medical_issue = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    other_medical_issues = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.reference_number} - {self.medical_issue}"


class FamilyHistory(models.Model):
    reference_number = models.CharField(max_length=50, unique=True)

    # Boolean fields for each family history condition
    Hypertension = models.BooleanField(default=False)
    Diabetes = models.BooleanField(default=False)
    Cataract = models.BooleanField(default=False)
    Glaucoma = models.BooleanField(default=False)
    Other_glasses = models.BooleanField(
        default=False
    )  # Renamed to match "OtherGlasses"
    Other = models.BooleanField(default=False)
    none = models.BooleanField(default=False)

    relationshipwithchild = models.CharField(
        max_length=50,
        choices=[
            ("Grandfather", "Grandfather"),
            ("Grandmother", "Grandmother"),
            ("Father", "Father"),
            ("Mother", "Mother"),
            ("Sister", "Sister"),
            ("Brother", "Brother"),
        ],
    )

    search_term = models.CharField(
        max_length=100, blank=True, null=True
    )  # Fixed "SerachTerm" typo
    family_history = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.reference_number} - Family History"


class CurrentMedicalTreatment(models.Model):
    reference_number = models.CharField(max_length=50, unique=True)
    medical_treatment = models.CharField(
        max_length=10,
        choices=[("Yes", "Yes"), ("No", "No"), ("Not Known", "Not Known")],
    )
    medicine = models.CharField(max_length=50)

    treatment_eye = models.CharField(
        max_length=50,
        choices=[
            ("Right_eye", "Right_eye"),
            ("Left_eye", "Left_eye"),
            ("Both", "Both"),
            ("Systemic", "Systemic"),
        ],
    )

    medicine_type = models.CharField(
        max_length=50,
        choices=[
            ("Eye drop", "Eye drop"),
            ("Eye ointment", "Eye ointment"),
            ("Injection", "Injection"),
            ("capsule", "capsule"),
            ("tablet", "tablet"),
            ("Syrup", "Syrup"),
            ("spray", "spray"),
        ],
    )

    times_per_day = models.IntegerField(
        choices=[
            (1, "one time a day"),
            (2, "twice a day"),
            (3, "three times a day"),
            (4, "four times a day"),
            (5, "five times a day"),
        ]
    )

    # prescribed_date = models.DateField()
    prescribed_date = models.CharField(max_length=50, null=True, blank=True)
    current_medical_treatment = models.BooleanField(default=True)

    def __str__(self):
        return f"f{self.reference_number} - {self.medical_treatment} - {self.treatment_eye} - {self.medicine}"


# Define choices for Visual Acuity fields
VISUAL_ACUITY_DISTANCE_CHOICES = [
    ("6/4", "6/4"),
    ("6/5", "6/5"),
    ("6/6", "6/6"),
    ("6/6P", "6/6P"),
    ("6/7.5", "6/7.5"),
    ("6/7.5P", "6/7.5P"),
    ("6/9", "6/9"),
    ("6/9P", "6/9P"),
    ("6/12", "6/12"),
    ("6/12P", "6/12P"),
    ("6/18", "6/18"),
    ("6/18P", "6/18P"),
    ("6/24", "6/24"),
    ("6/24P", "6/24P"),
    ("6/36", "6/36"),
    ("6/36P", "6/36P"),
    ("6/60", "6/60"),
    ("5/60", "5/60"),
    ("4/60", "4/60"),
    ("3/60", "3/60"),
    ("2/60", "2/60"),
    ("1/60", "1/60"),
    ("FC 1/2 M", "FC 1/2 M"),
    ("FCCF", "FCCF"),
    ("HM(+)", "HM(+)"),
    ("PL+ PR ACCURATE", "PL+ PR ACCURATE"),
    ("PL + PR INACCURATE", "PL + PR INACCURATE"),
    ("FIXING AND FOLLOWING LIGHT", "FIXING AND FOLLOWING LIGHT"),
    ("NPL", "NPL"),
    ("DEFERRED", "DEFERRED"),
]

VISUAL_ACUITY_NEAR_CHOICES = [
    ("N6", "N6"),
    ("N8", "N8"),
    ("N10", "N10"),
    ("N12", "N12"),
    ("N14", "N14"),
    ("N18", "N18"),
    ("N24", "N24"),
    ("N36", "N36"),
    ("N60", "N60"),
    ("LESS THEN N60", "LESS THEN N60"),
]


class VisualAcuityMeasurement(models.Model):
    reference_number = models.CharField(max_length=100, unique=True)
    unaided_distance_va_re = models.CharField(
        max_length=50, choices=VISUAL_ACUITY_DISTANCE_CHOICES, blank=True, null=True
    )
    unaided_distance_va_le = models.CharField(
        max_length=50, choices=VISUAL_ACUITY_DISTANCE_CHOICES, blank=True, null=True
    )
    unaided_near_va_re = models.CharField(
        max_length=50, choices=VISUAL_ACUITY_NEAR_CHOICES, blank=True, null=True
    )
    unaided_near_va_le = models.CharField(
        max_length=50, choices=VISUAL_ACUITY_NEAR_CHOICES, blank=True, null=True
    )
    aided_distance_va_re = models.CharField(
        max_length=50, choices=VISUAL_ACUITY_DISTANCE_CHOICES, blank=True, null=True
    )
    aided_distance_va_le = models.CharField(
        max_length=50, choices=VISUAL_ACUITY_DISTANCE_CHOICES, blank=True, null=True
    )
    aided_near_va_re = models.CharField(
        max_length=50, choices=VISUAL_ACUITY_NEAR_CHOICES, blank=True, null=True
    )
    aided_near_va_le = models.CharField(
        max_length=50, choices=VISUAL_ACUITY_NEAR_CHOICES, blank=True, null=True
    )
    ph_distance_va_re = models.CharField(
        max_length=50, choices=VISUAL_ACUITY_DISTANCE_CHOICES, blank=True, null=True
    )
    pd_distance_va_le = models.CharField(
        max_length=50, choices=VISUAL_ACUITY_DISTANCE_CHOICES, blank=True, null=True
    )
    measure_visual_acuity = models.BooleanField(default=True)

    def __str__(self):
        return f"Reference: {self.reference_number}"


# Define choices for SPH (Spherical) values
SPH_CHOICES = [
    ("0.00", "0.00"),
    ("+0.25", "+0.25"),
    ("+0.50", "+0.50"),
    ("+0.75", "+0.75"),
    ("+1.00", "+1.00"),
    ("+1.25", "+1.25"),
    ("+1.50", "+1.50"),
    ("+1.75", "+1.75"),
    ("+2.00", "+2.00"),
    ("+2.25", "+2.25"),
    ("+2.50", "+2.50"),
    ("+2.75", "+2.75"),
    ("+3.00", "+3.00"),
    ("+3.25", "+3.25"),
    ("+3.50", "+3.50"),
    ("+3.75", "+3.75"),
    ("+4.00", "+4.00"),
    ("+4.25", "+4.25"),
    ("+4.50", "+4.50"),
    ("+4.75", "+4.75"),
    ("+5.00", "+5.00"),
    ("+5.25", "+5.25"),
    ("+5.50", "+5.50"),
    ("+5.75", "+5.75"),
    ("+6.00", "+6.00"),
    ("+6.50", "+6.50"),
    ("+7.00", "+7.00"),
    ("+7.50", "+7.50"),
    ("+8.00", "+8.00"),
    ("+8.50", "+8.50"),
    ("+9.00", "+9.00"),
    ("+9.50", "+9.50"),
    ("+10.00", "+10.00"),
    ("+10.50", "+10.50"),
    ("+11.00", "+11.00"),
    ("+11.50", "+11.50"),
    ("+12.00", "+12.00"),
    ("+12.50", "+12.50"),
    ("+13.00", "+13.00"),
    ("+13.50", "+13.50"),
    ("+14.00", "+14.00"),
    ("+14.50", "+14.50"),
    ("+15.00", "+15.00"),
    ("+15.50", "+15.50"),
    ("+16.00", "+16.00"),
    ("+16.50", "+16.50"),
    ("+17.00", "+17.00"),
    ("+17.50", "+17.50"),
    ("+18.00", "+18.00"),
    ("+18.50", "+18.50"),
    ("+19.00", "+19.00"),
    ("+19.50", "+19.50"),
    ("+20.00", "+20.00"),
    ("-0.25", "-0.25"),
    ("-0.50", "-0.50"),
    ("-0.75", "-0.75"),
    ("-1.00", "-1.00"),
    ("-1.25", "-1.25"),
    ("-1.50", "-1.50"),
    ("-1.75", "-1.75"),
    ("-2.00", "-2.00"),
    ("-2.25", "-2.25"),
    ("-2.50", "-2.50"),
    ("-2.75", "-2.75"),
    ("-3.00", "-3.00"),
    ("-3.25", "-3.25"),
    ("-3.50", "-3.50"),
    ("-3.75", "-3.75"),
    ("-4.00", "-4.00"),
    ("-4.25", "-4.25"),
    ("-4.50", "-4.50"),
    ("-4.75", "-4.75"),
    ("-5.00", "-5.00"),
    ("-5.25", "-5.25"),
    ("-5.50", "-5.50"),
    ("-5.75", "-5.75"),
    ("-6.00", "-6.00"),
    ("-6.50", "-6.50"),
    ("-7.00", "-7.00"),
    ("-7.50", "-7.50"),
    ("-8.00", "-8.00"),
    ("-8.50", "-8.50"),
    ("-9.00", "-9.00"),
    ("-9.50", "-9.50"),
    ("-10.00", "-10.00"),
    ("-10.50", "-10.50"),
    ("-11.00", "-11.00"),
    ("-11.50", "-11.50"),
    ("-12.00", "-12.00"),
    ("-12.50", "-12.50"),
    ("-13.00", "-13.00"),
    ("-13.50", "-13.50"),
    ("-14.00", "-14.00"),
    ("-14.50", "-14.50"),
    ("-15.00", "-15.00"),
    ("-15.50", "-15.50"),
    ("-16.00", "-16.00"),
    ("-16.50", "-16.50"),
    ("-17.00", "-17.00"),
    ("-17.50", "-17.50"),
    ("-18.00", "-18.00"),
    ("-18.50", "-18.50"),
    ("-19.00", "-19.00"),
    ("-19.50", "-19.50"),
    ("-20.00", "-20.00"),
]

# Define choices for CYL (Cylindrical) values
CYL_CHOICES = [
    ("0.00", "0.00"),
    ("+0.25", "+0.25"),
    ("+0.50", "+0.50"),
    ("+0.75", "+0.75"),
    ("+1.00", "+1.00"),
    ("+1.25", "+1.25"),
    ("+1.50", "+1.50"),
    ("+1.75", "+1.75"),
    ("+2.00", "+2.00"),
    ("+2.25", "+2.25"),
    ("+2.50", "+2.50"),
    ("+2.75", "+2.75"),
    ("+3.00", "+3.00"),
    ("+3.25", "+3.25"),
    ("+3.50", "+3.50"),
    ("+3.75", "+3.75"),
    ("+4.00", "+4.00"),
    ("+4.25", "+4.25"),
    ("+4.50", "+4.50"),
    ("+4.75", "+4.75"),
    ("+5.00", "+5.00"),
    ("+5.25", "+5.25"),
    ("+5.50", "+5.50"),
    ("+5.75", "+5.75"),
    ("+6.00", "+6.00"),
    ("-0.25", "-0.25"),
    ("-0.50", "-0.50"),
    ("-0.75", "-0.75"),
    ("-1.00", "-1.00"),
    ("-1.25", "-1.25"),
    ("-1.50", "-1.50"),
    ("-1.75", "-1.75"),
    ("-2.00", "-2.00"),
    ("-2.25", "-2.25"),
    ("-2.50", "-2.50"),
    ("-2.75", "-2.75"),
    ("-3.00", "-3.00"),
    ("-3.25", "-3.25"),
    ("-3.50", "-3.50"),
    ("-3.75", "-3.75"),
    ("-4.00", "-4.00"),
    ("-4.25", "-4.25"),
    ("-4.50", "-4.50"),
    ("-4.75", "-4.75"),
    ("-5.00", "-5.00"),
    ("-5.25", "-5.25"),
    ("-5.50", "-5.50"),
    ("-5.75", "-5.75"),
    ("-6.00", "-6.00"),
]

# Define choices for AXIS values
AXIS_CHOICES = [(str(i), str(i)) for i in range(0, 181, 5)]  # 0 to 180 in steps of 5

# Define choices for ADD (Addition) values
ADD_CHOICES = [
    ("+1.00", "+1.00"),
    ("+1.25", "+1.25"),
    ("+1.50", "+1.50"),
    ("+1.75", "+1.75"),
    ("+2.00", "+2.00"),
    ("+2.25", "+2.25"),
    ("+2.50", "+2.50"),
    ("+2.75", "+2.75"),
    ("+3.00", "+3.00"),
    ("+3.25", "+3.25"),
    ("+3.50", "+3.50"),
    ("+3.75", "+3.75"),
    ("+4.00", "+4.00"),
]


class RefractionSpectacle(models.Model):
    reference_number = models.CharField(max_length=100, unique=True)
    spherical_prescription_re = models.CharField(
        max_length=50, choices=SPH_CHOICES, blank=True, null=True
    )
    cylindrical_prescription_re = models.CharField(
        max_length=50, choices=CYL_CHOICES, blank=True, null=True
    )
    axis_cylinder_re = models.CharField(
        max_length=50, choices=AXIS_CHOICES, blank=True, null=True
    )
    spherical_prescription_le = models.CharField(
        max_length=50, choices=SPH_CHOICES, blank=True, null=True
    )
    cylindrical_prescription_le = models.CharField(
        max_length=50, choices=CYL_CHOICES, blank=True, null=True
    )
    axis_cylinder_le = models.CharField(
        max_length=50, choices=AXIS_CHOICES, blank=True, null=True
    )
    refraction_spectacle_presentation = models.BooleanField(default=True)

    def __str__(self):
        return f"Reference: {self.reference_number}"


class PatientComplaint(models.Model):
    COMPLAINT_CHOICES = [
        ("NO COMPLAINTS/observations", "NO COMPLAINTS/observations"),
        ("BLURRING", "BLURRING"),
        ("HEADACHE", "HEADACHE"),
        ("WATERING", "WATERING"),
        ("REDNESS", "REDNESS"),
        ("BURNING SENSATION", "BURNING SENSATION"),
        ("ITCHING", "ITCHING"),
        ("SQUEEZING", "SQUEEZING"),
        ("PAIN", "PAIN"),
        ("REPEATED EYE SWELLING", "REPEATED EYE SWELLING"),
        ("SQUINTING", "SQUINTING"),
        ("DROOPING OF THE LID", "DROOPING OF THE LID"),
        ("ABNORMAL EYE MOVEMENT", "ABNORMAL EYE MOVEMENT"),
        ("NIGHT BLINDNESS", "NIGHT BLINDNESS"),
    ]

    selected_complaint = models.TextField(null=True, blank=True)
    effected_eye = models.CharField(max_length=50, null=True, blank=True)
    reference_number = models.CharField(max_length=100, unique=True, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="complaints",
        null=True,
        blank=True,
    )

    def set_complaints(self, complaints):
        """
        Sets the complaints as a comma-separated string.
        """
        self.selected_complaint = ",".join(complaints)

    def get_complaints(self):
        """
        Returns a list of complaints from the comma-separated string.
        """
        return self.selected_complaint.split(",") if self.selected_complaint else []

    def __str__(self):
        return f"Complaints: {self.selected_complaint}"
