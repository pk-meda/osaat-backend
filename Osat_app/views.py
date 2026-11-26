import os
import random
import re
import string
import uuid
from datetime import timedelta
from uuid import uuid4
import csv
import io
import openpyxl
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.serializers import serialize
from django.db.models import Q
from django.db import transaction
from django.http import JsonResponse
from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import (  # send the reset link to the user
    urlsafe_base64_decode,
    urlsafe_base64_encode,
)
from rest_framework import generics, status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes  # <--- ADD THIS LINE
from rest_framework.response import Response
from rest_framework.views import APIView


from .models import (
    Comprehensive,
    ComprehensiveEyeTest,
    Country,
    CurrentMedicalTreatment,
    Diagnosis,
    Dispensing,
    FamilyHistory,
    Firstscreening,
    OtherMedicalIssueResponse,
    Participant,
    PatientComplaint,
    Province,
    RefractionExamination,
    RefractionSpectacle,
    SecondScreening,
    SpectacleHistory,
    SurgeryTreatmentHistory,
    VisualAcuityMeasurement,
    school,
)
from .serializers import (
    ComprehensiveSerializer,
    ComprehensiveEyeTestSerializer,
    CurrentMedicalSerializer,
    DiagnosisSerializer,
    DispensingSerializer,
    FamilyHistorySerializer,
    FirstScreeningSerializer,
    InitialEyeTestSerializer,
    OtherMedicalIssueResponseSerializer,
    ParticipantSerializer,
    PatientComplaintSerializer,
    RefractionExaminationSerializer,
    RefractionSpectacleSerializer,
    RetestEyeTestSerializer,
    SecondscreeningSerializer,
    SpectacleHistorySerializer,
    SurgeryTreatmentHistorySerializer,
    UserSerializer,
    VisualacuitySerializer,
    schoolSerializer,
)

ACCESS_TOKEN_EXPIRES_IN = 15


##User_Registration API
class RegisterAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Generate a token for the registered user
            token, created = Token.objects.get_or_create(user=user)

            return Response(
                {
                    "body": [],
                    "message": "User registered successfully",
                    "error": False,
                    "token": token.key,  # Token included for immediate login
                },
                status=status.HTTP_201_CREATED,
            )

        error_messages = " | ".join(
            [
                f"{field}: {', '.join(errors)}"
                for field, errors in serializer.errors.items()
            ]
        )

        return Response(
            {
                "body": [],
                "message": f"Registration failed: {error_messages}",
                "error": True,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# # User_Login API
# class UserLoginView(APIView):
#     def post(self, request):
#         email = request.data.get("email")
#         password = request.data.get("password")

#         if not email or not password:
#             return Response(
#                 {
#                     "body": [],
#                     "message": "Email and password are required",
#                     "error": True,
#                 },
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             return Response(
#                 {"body": [], "message": "Invalid email or password", "error": True},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         user = authenticate(username=user.username, password=password)

#         if user:
#             token, created = Token.objects.get_or_create(user=user)
#             return Response(
#                 {
#                     "body": {"token": token.key},
#                     "message": "Login successful",
#                     "error": False,
#                 },
#                 status=status.HTTP_200_OK,
#             )

#         return Response(
#             {"body": [], "message": "Invalid email or password", "error": True},
#             status=status.HTTP_400_BAD_REQUEST,
#         )


class UserLoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {
                    "body": [],
                    "message": "Email and password are required",
                    "error": True,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {
                    "body": [],
                    "message": "Invalid email or password",
                    "error": True,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(username=user.username, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)

            user_data = {
                "id": user.id,
                "name": f"{user.first_name} {user.last_name}".strip(),
                "email": user.email,
                "mobile_number": user.username,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
            }

            return Response(
                {
                    "body": {
                        "token": token.key,
                        "user": user_data,
                    },
                    "message": "Login successful",
                    "error": False,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "body": [],
                "message": "Invalid email or password",
                "error": True,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

#supports PUT/PATCH updates for an existing Firstscreening instance.
@api_view(['PATCH', 'PUT'])
@permission_classes([AllowAny])
def update_first_screening(request, pk):
    try:
        screening = Firstscreening.objects.get(pk=pk)
    except Firstscreening.DoesNotExist:
        return Response({'error': True, 'message': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)

    # Pass partial=True to allow updating step 2 fields without re-validating read-only fields
    serializer = FirstScreeningSerializer(screening, data=request.data, partial=True)
    if serializer.is_valid():
        instance = serializer.save()
        return Response({
            'error': False,
            'message': 'Screening updated successfully.',
            'body': FirstScreeningSerializer(instance).data
        }, status=status.HTTP_200_OK)

    return Response({
        'error': True,
        'message': 'Validation failed.',
        'body': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

# User-Logout API
class UserLogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Delete the user's token to log them out
            request.user.auth_token.delete()
            return Response(
                {"body": [], "message": "Logout successful", "error": False},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"body": [], "message": "Something went wrong", "error": True},
                status=status.HTTP_400_BAD_REQUEST,
            )


# OTP-Send API
class SendOTPView(APIView):
    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response(
                {"body": [], "message": "Email is required", "error": True},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"body": [], "message": "User not found", "error": True},
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp = "".join(random.choices(string.digits, k=6))
        cache.set(f"otp_{email}", otp, timeout=300)

        send_mail(
            "Password Reset OTP",
            f"Your OTP is: {otp}. Valid for 5 minutes.",
            "noreply@example.com",
            [email],
            fail_silently=False,
        )

        return Response(
            {"body": [], "message": "OTP sent to your email", "error": False},
            status=status.HTTP_200_OK,
        )


# OTP-Verify API
class VerifyOTPView(APIView):
    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        if not email or not otp:
            return Response(
                {"body": [], "message": "Email and OTP are required", "error": True},
                status=status.HTTP_400_BAD_REQUEST,
            )

        stored_otp = cache.get(f"otp_{email}")

        if stored_otp is None or stored_otp != otp:
            return Response(
                {"body": [], "message": "Invalid or expired OTP", "error": True},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cache.delete(f"otp_{email}")

        return Response(
            {"body": [], "message": "OTP verified successfully", "error": False},
            status=status.HTTP_200_OK,
        )


# Password-Reset API
class ResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get("email")
        new_password = request.data.get("new_password")

        if not email or not new_password:
            return Response(
                {
                    "body": [],
                    "message": "Email and new password are required",
                    "error": True,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            return Response(
                {"body": [], "message": "Password reset successfully", "error": False},
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"body": [], "message": "User not found", "error": True},
                status=status.HTTP_400_BAD_REQUEST,
            )


# School
# class SchoolListView(APIView):
#     def get(self, request):
#         schools = School.objects.all().order_by('name')  # optional: order alphabetically
#         serializer = SchoolSerializer(schools, many=True)
#         return Response({
#             "body": serializer.data,
#             "message": "School list retrieved successfully.",
#             "error": False
#         }, status=status.HTTP_200_OK)
#     def post(self, request):
#         data = request.data

#         required_fields = [
#             'country', 'province', 'school_name',
#             'children_count', 'address',
#             'contact_person', 'contact_details'
#         ]

#         for field in required_fields:
#             if not data.get(field):
#                 return Response({
#                     "body": [],
#                     "message": f"{field.replace('_', ' ').capitalize()} is required.",
#                     "error": True
#                 }, status=status.HTTP_400_BAD_REQUEST)

#         # Fetch or create country by name
#         country, created = Country.objects.get_or_create(name=data['country'])

#         # Fetch or create province by name and associate it with the country
#         province, created = Province.objects.get_or_create(name=data['province'], country=country)

#         # Check if the school already exists
#         school = School.objects.filter(name=data['school_name']).first()

#         if school:
#             # School exists, so update the details
#             school.number_of_children = data['children_count']
#             school.address = data['address']
#             school.contact_person = data['contact_person']
#             school.contact_details = data['contact_details']
#             school.referral_clinic = data.get('referral_clinic', school.referral_clinic)

#             # Save the updated school
#             school.save()

#             message = "Details updated successfully."
#         else:
#             # School doesn't exist, create a new one
#             school = School.objects.create(
#                 name=data['school_name'],
#                 country=country,
#                 province=province,
#                 number_of_children=data['children_count'],
#                 address=data['address'],
#                 contact_person=data['contact_person'],
#                 contact_details=data['contact_details'],
#                 referral_clinic=data.get('referral_clinic', '')
#             )

#             message = "School registered successfully."

#         # Serialize the school data
#         school_data = SchoolSerializer(school).data

#         return Response({
#             "body": [school_data],  # Include school details in the body
#             "message": message,
#             "error": False
#         }, status=status.HTTP_201_CREATED if not school.id else status.HTTP_200_OK)


class schoolView(APIView):
    def get(self, request):
        """
        Returns all schools for dropdown.
        """
        schools = school.objects.all()
        serializer = schoolSerializer(schools, many=True)
        return Response(
            {
                "body": serializer.data,
                "message": "School list fetched successfully.",
                "error": False,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        school_name = request.data.get("school_name", "").strip()
        contact_details = request.data.get("contact_details", "").strip()
        address = request.data.get("address", "").strip()
        province = request.data.get("province", "").strip()
        country = request.data.get("country", "").strip()

        if not school_name:
            return Response(
                {"body": [], "message": "School name is required.", "error": True},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if school.objects.filter(school_name__iexact=school_name).exists():
            return Response(
                {"body": [], "message": "This school already exists.", "error": True},
                status=status.HTTP_200_OK,
            )

        data = {
            "school_name": school_name,
            "contact_details": contact_details,
            "address": address,
            "province": province,
            "country": country,
        }

        serializer = schoolSerializer(data=data)
        if serializer.is_valid():
            school_obj = serializer.save()
            return Response(
                {
                    "body": schoolSerializer(school_obj).data,
                    "message": "School created successfully.",
                    "error": False,
                },
                status=status.HTTP_201_CREATED,
            )

        # DEBUG HERE: SHOW ERRORS
        return Response(
            {
                "body": serializer.errors,
                "message": "Invalid data provided.",
                "error": True,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# class FirstScreeningAPIView(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         serializer = FirstScreeningSerializer(data=request.data)
#         if serializer.is_valid():
#             first_screening = serializer.save()

#             participant, created = Participant.objects.get_or_create(
#                 reference_number=first_screening.reference_number
#             )
#             participant.created_by = request.user
#             participant.first_screening = True
#             participant.save()
#             print("participant-----", participant)

#             return Response(
#                 {
#                     "body": serializer.data,
#                     "message": "Student registered successfully",
#                     "error": False,
#                 },
#                 status=status.HTTP_201_CREATED,
#             )

#         return Response(
#             {
#                 "body": {},
#                 "message": "Validation failed",
#                 "error": True,
#                 "errors": serializer.errors,
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )


class FirstScreeningAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FirstScreeningSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    # Extract or generate unique reference number
                    ref_num = request.data.get("reference_number")
                    if not ref_num or ref_num == "":
                        ref_num = f"SS-{uuid.uuid4().hex[:8].upper()}"
                        

                    # 1. Save FirstScreening instance with reference_number
                    first_screening = serializer.save(
                        created_by=request.user,
                        reference_number=ref_num
                    )

                    # 2. Safely get or create the linked Participant record
                    participant, created = Participant.objects.get_or_create(
                        reference_number=ref_num,
                        defaults={
                            "created_by": request.user,
                            "first_screening": True,
                        }
                    )

                    if not created:
                        participant.created_by = request.user
                        participant.first_screening = True
                        participant.save()

                    # 3. Formulate response payload
                    response_data = serializer.data
                    response_data["reference_number"] = ref_num

                    return Response(
                        {
                            "body": response_data,
                            "message": "Student registered successfully.",
                            "error": False,
                        },
                        status=status.HTTP_201_CREATED,
                    )

            except Exception as e:
                # Catches internal DB errors and returns explicit error context instead of crash 500
                return Response(
                    {
                        "body": str(e),
                        "message": "Database error while processing screening.",
                        "error": True,
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(
            {
                "body": serializer.errors,
                "message": "Validation failed.",
                "error": True,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# Comprehensive API
class ComprehensiveAPIView(APIView):
    def get(self, request):
        """Retrieve all Comprehensive records."""
        records = Comprehensive.objects.all()
        serializer = ComprehensiveSerializer(records, many=True)
        return Response(
            {
                "body": serializer.data,
                "message": "Records retrieved successfully",
                "error": False,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        """Create a new Comprehensive record."""
        serializer = ComprehensiveSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "body": serializer.data,  # Will not include 'id'
                    "message": "Record created successfully",
                    "error": False,
                },
                status=status.HTTP_201_CREATED,
            )
        print("Validation Errors:", serializer.errors)  # Debugging
        return Response(
            {
                "body": {},
                "message": "Validation failed",
                "error": True,
                "details": serializer.errors,  # Helps debug issues
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class ComprehensiveEyeTestAPIView(APIView):

    def get(self, request):
        """Retrieve all Comprehensive Eye Test records."""
        records = ComprehensiveEyeTest.objects.all()
        serializer = ComprehensiveEyeTestSerializer(records, many=True)

        return Response(
            {
                "body": serializer.data,
                "message": "Eye test records retrieved successfully",
                "error": False,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        """Create or update a Comprehensive Eye Test record."""
        reference_number = request.data.get("reference_number")

        if not reference_number:
            return Response(
                {
                    "message": "Reference number is required",
                    "error": True,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Find an existing record, if one exists.
        instance = ComprehensiveEyeTest.objects.filter(
            reference_number=reference_number
        ).first()

        # Check required fields when creating a new record.
        if instance is None:
            missing_fields = [
                field
                for field in (
                    "left_eye_score",
                    "right_eye_score",
                    "test_result",
                )
                if request.data.get(field) is None
                or request.data.get(field) == ""
            ]

           
