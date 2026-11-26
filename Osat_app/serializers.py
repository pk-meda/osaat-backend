import ast
import json

from django.contrib.auth.models import User
from rest_framework import serializers

from .models import (
    Comprehensive,
    CurrentMedicalTreatment,
    Diagnosis,
    Dispensing,
    FamilyHistory,
    Firstscreening,
    InitialEyeTest,
    OtherMedicalIssueResponse,
    Participant,
    PatientComplaint,
    RefractionExamination,
    RefractionSpectacle,
    RetestEyeTest,
    SecondScreening,
    SpectacleHistory,
    SurgeryTreatmentHistory,
    VisualAcuityMeasurement,
    school,
    ComprehensiveEyeTest,
)


class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True)  # Custom field for full name
    mobile_number = serializers.CharField(
        max_length=15, required=True
    )  # Add mobile number field

    class Meta:
        model = User
        fields = ["id", "name", "email", "mobile_number", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email address is already in use.")
        return value

    def validate_mobile_number(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This mobile number is already in use.")
        return value

    def create(self, validated_data):
        name = validated_data.pop("name")
        first_name, last_name = name.split(" ", 1) if " " in name else (name, "")

        user = User.objects.create(
            username=validated_data[
                "mobile_number"
            ],  # Storing mobile number as username
            email=validated_data["email"],
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


# class SchoolSerializer(serializers.ModelSerializer):
#     country = serializers.StringRelatedField()
#     province = serializers.StringRelatedField()
#     class Meta:
#         model = School
#         fields = [
#             "id", "name", "country", "province", "number_of_children",
#             "address", "contact_person", "contact_details", "referral_clinic"
#         ]


class schoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = school
        fields = "__all__"


class FirstScreeningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Firstscreening
        fields = "__all__"
        # read_only_fields = ['reference_number', 'created_at']


class SecondscreeningSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecondScreening
        fields = "__all__"


class ComprehensiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comprehensive
        fields = "__all__"


class InitialEyeTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = InitialEyeTest
        fields = "__all__"


class RetestEyeTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RetestEyeTest
        fields = "__all__"


class DispensingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispensing
        fields = "__all__"

    def validate_participant_number(self, value):
        if not value:
            raise serializers.ValidationError("Participant number is required.")
        return value


class RefractionExaminationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefractionExamination
        fields = "__all__"


# class DiagnosisSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Diagnosis
#         fields = "__all__"


class DiagnosisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diagnosis
        fields = "__all__"

    def validate_management_plan(self, value):
        """
        Ensure management_plan is always valid JSON (list or dict).
        Convert if the frontend sends it as a string.
        """
        if isinstance(value, str):
            try:
                # Try literal_eval for "['A', 'B']" case
                parsed = ast.literal_eval(value)
                if isinstance(parsed, (list, dict)):
                    return parsed
            except Exception:
                pass
            try:
                # Try JSON parse for '["A","B"]'
                parsed = json.loads(value)
                if isinstance(parsed, (list, dict)):
                    return parsed
            except Exception:
                pass
            # fallback
            return [value]
        elif isinstance(value, (list, dict)):
            return value
        return [str(value)]


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = "__all__"
        read_only_fields = ["created_by"]


class SpectacleHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SpectacleHistory
        fields = "__all__"


class SurgeryTreatmentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SurgeryTreatmentHistory
        fields = "__all__"


class OtherMedicalIssueResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherMedicalIssueResponse
        fields = ["reference_number", "medical_issue", "other_medical_issues"]


class FamilyHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyHistory
        fields = "__all__"


class CurrentMedicalSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrentMedicalTreatment
        fields = "__all__"


class VisualacuitySerializer(serializers.ModelSerializer):
    class Meta:
        model = VisualAcuityMeasurement
        fields = "__all__"


class RefractionSpectacleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefractionSpectacle
        fields = "__all__"


# class PatientComplaintSerializer(serializers.ModelSerializer):
#     selected_complaint = serializers.ListField(
#         child=serializers.ChoiceField(choices=PatientComplaint.COMPLAINT_CHOICES),
#         required=False
#     )

#     class Meta:
#         model = PatientComplaint
#         fields = ['id', 'selected_complaint']

#     def validate_selected_complaint(self, value):
#         """
#         Ensure the complaints are valid based on the choices.
#         """
#         for complaint in value:
#             if complaint not in dict(PatientComplaint.COMPLAINT_CHOICES).keys():
#                 raise serializers.ValidationError(f"Invalid complaint: {complaint}")
#         return value

#     def create(self, validated_data):
#         """
#         Create a PatientComplaint instance from the validated data.
#         """
#         complaints = validated_data.get('selected_complaint', [])
#         patient_complaint = PatientComplaint()
#         patient_complaint.set_complaints(complaints)
#         patient_complaint.save()
#         return patient_complaint


# class PatientComplaintSerializer(serializers.ModelSerializer):
#     selected_complaint = serializers.ListField(child=serializers.CharField())

#     class Meta:
#         model = PatientComplaint
#         fields = "__all__"



class ComplaintItemSerializer(serializers.Serializer):
    category = serializers.ChoiceField(choices=PatientComplaint.CATEGORY_CHOICES)
    label = serializers.CharField(max_length=100)
    eye_side = serializers.ChoiceField(choices=PatientComplaint.EYE_SIDE_CHOICES)
    onset = serializers.ChoiceField(choices=PatientComplaint.ONSET_CHOICES)
    duration = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    reporter = serializers.ChoiceField(choices=PatientComplaint.REPORTER_CHOICES)


class OtherComplaintSerializer(serializers.Serializer):
    selected = serializers.BooleanField(default=True)
    description = serializers.CharField(max_length=255)
    eye_side = serializers.ChoiceField(choices=PatientComplaint.EYE_SIDE_CHOICES)
    onset = serializers.ChoiceField(choices=PatientComplaint.ONSET_CHOICES)
    duration = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    reporter = serializers.ChoiceField(choices=PatientComplaint.REPORTER_CHOICES)


class PatientComplaintSerializer(serializers.ModelSerializer):
    complaints_data = ComplaintItemSerializer(many=True, required=False, default=list)
    other_complaint = OtherComplaintSerializer(required=False, allow_null=True)
    selected_complaint = serializers.ListField(
        child=serializers.CharField(), required=False, read_only=True
    )

    class Meta:
        model = PatientComplaint
        fields = "__all__"
        extra_kwargs = {
            "created_by": {"read_only": True},
            "reference_number": {"validators": []},  # Handled via upsert in view
        }

    def validate(self, attrs):
        no_concerns = attrs.get(
            "no_concerns",
            getattr(self.instance, "no_concerns", False),
        )
        complaints_data = attrs.get(
            "complaints_data",
            getattr(self.instance, "complaints_data", []),
        )
        other_complaint = attrs.get(
            "other_complaint",
            getattr(self.instance, "other_complaint", None),
        )

        has_other = bool(other_complaint and other_complaint.get("selected"))

        if no_concerns:
            attrs["complaints_data"] = []
            attrs["other_complaint"] = None
        elif not complaints_data and not has_other:
            raise serializers.ValidationError(
                'Select at least one complaint/observation or check "No concerns".'
            )

        return attrs

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["selected_complaint"] = (
            instance.selected_complaint.split(",") if instance.selected_complaint else []
        )
        return representation


class ComprehensiveEyeTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComprehensiveEyeTest
        fields = '__all__'
