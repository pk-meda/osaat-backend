import os
import random
import re
import string
import uuid
from datetime import timedelta
from uuid import uuid4
import csv

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
                {"body": [], "message": "Invalid email or password", "error": True},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(username=user.username, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)

            # Serialize user info
            user_data = {
                "id": user.id,
                "name": f"{user.first_name} {user.last_name}".strip(),
                "email": user.email,
                "mobile_number": user.username,  # Here stored the mobile number
            }

            return Response(
                {
                    "body": {"token": token.key, "user": user_data},
                    "message": "Login successful",
                    "error": False,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"body": [], "message": "Invalid email or password", "error": True},
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
                {"message": "Reference number is required", "error": True},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 1. Get all valid field names on the ComprehensiveEyeTest model
        # This keeps the request clean and prevents unexpected DB crashes from extra payload keys
        model_fields = {f.name for f in ComprehensiveEyeTest._meta.get_fields()}
        
        # 2. Build safe defaults containing only existing fields
        safe_defaults = {
            key: value for key, value in request.data.items()
            if key in model_fields and key != 'reference_number'
        }

        # 3. Safely update or create the record
        obj, created = ComprehensiveEyeTest.objects.update_or_create(
            reference_number=reference_number,
            defaults=safe_defaults,
        )

        # 4. Sync with Participant model if you track its overall status
        try:
            participant = Participant.objects.get(reference_number=reference_number)
            participant.comprehensive_eye_test = True  
            participant.save()
        except Participant.DoesNotExist:
            pass

        serializer = ComprehensiveEyeTestSerializer(obj)
        return Response(
            {
                "body": serializer.data,
                "message": "Eye test saved successfully" if created else "Eye test updated successfully",
                "error": False,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class Echo:
    """An object that implements just the write method of the file-like interface."""
    def write(self, value):
        return value

class SpecOrderReportView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        school_filter = request.query_params.get('school', None)

        participants = Participant.objects.all()

        if school_filter and school_filter.strip():
            clean_school = school_filter.strip()

            # 1. Collect reference numbers from FirstScreening matching the school name
            fs_ref_numbers = Firstscreening.objects.filter(
                school__icontains=clean_school
            ).values_list('reference_number', flat=True)

            # 2. Collect reference numbers from SecondScreening matching the school name
            ss_ref_numbers = SecondScreening.objects.filter(
                school__icontains=clean_school
            ).values_list('reference_number', flat=True)

            # 3. Combine both sets of reference numbers
            matching_ref_numbers = set(fs_ref_numbers).union(set(ss_ref_numbers))

            # 4. Filter participants by these reference numbers
            participants = participants.filter(reference_number__in=matching_ref_numbers)

        headers = [
            'Reference Number', 'Screening Date', 'Name', 'Surname', 'Age', 'Gender', 'School', 'Grade',
            'RE Sph (Final)', 'RE Cyl (Final)', 'RE Axis (Final)',
            'LE Sph (Final)', 'LE Cyl (Final)', 'LE Axis (Final)',
            'Frame Choice', 'Lenses Type', 'PD Distance', 'Comments'
        ]

        def stream_rows():
            # Write CSV header row
            writer = csv.writer(Echo())
            yield writer.writerow(headers)

            for p in participants.iterator():
                ref_num = str(p.reference_number).strip() if p.reference_number else ''

                # 1. First Screening lookup
                fs = (
                    (hasattr(p, 'first_screenings') and p.first_screenings.first()) or
                    Firstscreening.objects.filter(reference_number__iexact=ref_num).first()
                )

                # 2. Second Screening lookup
                ss = (
                    (hasattr(p, 'second_screenings') and p.second_screenings.first()) or
                    SecondScreening.objects.filter(reference_number__iexact=ref_num).first()
                )

                # 3. Refraction Examination lookup
                refraction = RefractionExamination.objects.filter(
                    reference_number__iexact=ref_num
                ).first()

                # 4. Robust Dispensing lookup:
                dispensing = (
                    (hasattr(p, 'dispensings') and p.dispensings.order_by('-id').first()) or
                    Dispensing.objects.filter(participant=p).order_by('-id').first() or
                    Dispensing.objects.filter(reference_number__iexact=ref_num).order_by('-id').first()
                )

                # Extract screening date safely (checks created_at / date / date_created across FS and SS)
                screening_obj = fs or ss
                created_at_val = getattr(screening_obj, 'created_at', None) or getattr(screening_obj, 'date_created', None) or getattr(screening_obj, 'date', None)
                
                if created_at_val:
                    # Format as YYYY-MM-DD if it's a datetime/date object
                    screening_date = created_at_val.strftime('%Y-%m-%d') if hasattr(created_at_val, 'strftime') else str(created_at_val)
                else:
                    screening_date = ""

                # Safely extract participant & screening fields
                name = ss.name if ss and ss.name else ""
                surname = ss.surname if ss and ss.surname else ""
                age = fs.age if fs and fs.age is not None else ""
                gender = fs.gender if fs and fs.gender else ""
                school_name = (
                    (ss.school if ss and ss.school else None) or 
                    (fs.school if fs and fs.school else "")
                )
                grade = fs.grade if fs and fs.grade else ""

                # Extract dispensing fields safely
                frame_choice = dispensing.frame_choice if dispensing and dispensing.frame_choice else ""
                lenses_type = dispensing.lenses_type if dispensing and dispensing.lenses_type else ""
                pd_distance = dispensing.pd_distance if dispensing and dispensing.pd_distance else ""
                comments = dispensing.comments if dispensing and dispensing.comments else ""

                row = [
                    ref_num,
                    screening_date,
                    name,
                    surname,
                    age,
                    gender,
                    school_name,
                    grade,
                    refraction.sph_RE_final if refraction and refraction.sph_RE_final else "",
                    refraction.cyl_RE_final if refraction and refraction.cyl_RE_final else "",
                    refraction.axis_RE_final if refraction and refraction.axis_RE_final else "",
                    refraction.sph_LE_final if refraction and refraction.sph_LE_final else "",
                    refraction.cyl_LE_final if refraction and refraction.cyl_LE_final else "",
                    refraction.axis_LE_final if refraction and refraction.axis_LE_final else "",
                    frame_choice,
                    lenses_type,
                    pd_distance,
                    comments
                ]

                yield writer.writerow(row)

        response = StreamingHttpResponse(stream_rows(), content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="spec_order_sheet.csv"'
        return response
        
# class SecondscreeningAPIView(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]
#     parser_classes = (MultiPartParser, FormParser)

#     def get(self, request, *args, **kwargs):
#         reference_number = request.query_params.get("reference_number")

#         if reference_number:
#             screenings = SecondScreening.objects.filter(
#                 reference_number=reference_number, created_by=request.user
#             )
#         else:
#             screenings = SecondScreening.objects.filter(created_by=request.user)

#         serializer = SecondscreeningSerializer(screenings, many=True)

#         if serializer.data:
#             return Response(
#                 {
#                     "body": serializer.data,
#                     "message": "Data fetched successfully",
#                     "error": False,
#                 },
#                 status=status.HTTP_200_OK,
#             )
#         else:
#             return Response(
#                 {
#                     "body": [],
#                     "message": "No records found",
#                     "error": True,
#                 },
#                 status=status.HTTP_404_NOT_FOUND,
#             )

#     def post(self, request, *args, **kwargs):
#         reference_number = request.data.get("reference_number")

#         if not reference_number:
#             return Response(
#                 {"body": {}, "message": "Reference number is required", "error": True},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         instance = SecondScreening.objects.filter(
#             reference_number=reference_number
#         ).first()

#         serializer = SecondscreeningSerializer(
#             instance, data=request.data, partial=True
#         )

#         if serializer.is_valid():
#             second_screening = serializer.save(created_by=request.user)

#             participant, _ = Participant.objects.get_or_create(
#                 reference_number=second_screening.reference_number
#             )
#             participant.created_by = request.user
#             participant.second_screening = True
#             participant.save()

#             return Response(
#                 {
#                     "body": serializer.data,
#                     "message": "Details updated successfully"
#                     if instance
#                     else "Details created successfully",
#                     "error": False,
#                 },
#                 status=status.HTTP_200_OK if instance else status.HTTP_201_CREATED,
#             )

#         first_error = next(iter(serializer.errors.values()))[0]
#         return Response(
#             {
#                 "body": {},
#                 "message": f"Validation failed - {first_error}",
#                 "error": True,
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )


# class SecondscreeningAPIView(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]
#     parser_classes = (MultiPartParser, FormParser)

#     def get(self, request, *args, **kwargs):
#         """
#         Get all second screening records or filter by reference number.
#         """
#         reference_number = request.query_params.get("reference_number")

#         if reference_number:
#             screenings = SecondScreening.objects.filter(
#                 reference_number=reference_number, created_by=request.user
#             )
#         else:
#             screenings = SecondScreening.objects.filter(created_by=request.user)

#         serializer = SecondscreeningSerializer(screenings, many=True)

#         if screenings.exists():
#             return Response(
#                 {
#                     "body": serializer.data,
#                     "message": "Data fetched successfully",
#                     "error": False,
#                 },
#                 status=status.HTTP_200_OK,
#             )
#         else:
#             return Response(
#                 {
#                     "body": [],
#                     "message": "No records found",
#                     "error": True,
#                 },
#                 status=status.HTTP_404_NOT_FOUND,
#             )

#     def post(self, request, *args, **kwargs):
#         """
#         Create or update a Second Screening record.
#         If ID is present → update that record (do not create a new one).
#         If reference_number changes → delete the old record with the old reference_number.
#         """
#         second_screening_id = request.data.get("id", None)
#         new_ref_number = request.data.get("reference_number", "").strip()
#         old_ref_number = request.data.get("old_reference_number", "").strip()
#         print("old ref number:--->>", old_ref_number)
#         instance = None
#         # old_ref_number = None

#         # ✅ Try to fetch the record by ID if provided
#         if second_screening_id not in [None, "", "null"]:
#             try:
#                 instance = SecondScreening.objects.get(id=int(second_screening_id))
#                 # old_ref_number = instance.reference_number
#             except (SecondScreening.DoesNotExist, ValueError, TypeError):
#                 instance = None

#         # ✅ Prevent duplicate reference number (excluding current instance)
#         if new_ref_number:
#             existing = SecondScreening.objects.filter(reference_number=new_ref_number)
#             if instance:
#                 existing = existing.exclude(id=instance.id)
#             if existing.exists():
#                 return Response(
#                     {
#                         "body": {},
#                         "message": "This reference number already exists. Please use a unique one.",
#                         "error": True,
#                     },
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )

#         # ✅ Save (create or update)
#         serializer = SecondscreeningSerializer(
#             instance, data=request.data, partial=True
#         )
#         if serializer.is_valid():
#             second_screening = serializer.save(created_by=request.user)
#             print("done")
#             print("old ref number:", old_ref_number)
#             print("new ref number:", new_ref_number)

#             # ✅ If the reference number has changed → delete the old record
#             if old_ref_number and old_ref_number != new_ref_number:
#                 SecondScreening.objects.filter(reference_number=old_ref_number).exclude(
#                     id=second_screening.id
#                 ).delete()
#                 # Optional: also delete old participant with old reference
#                 print("deleting old reference number participant:", old_ref_number)
#                 Participant.objects.filter(reference_number=old_ref_number).delete()
#                 print("deleted old reference number:", old_ref_number)

#             # ✅ Sync with Participant (for new reference)
#             participant, _ = Participant.objects.get_or_create(
#                 reference_number=second_screening.reference_number
#             )
#             participant.created_by = request.user
#             participant.second_screening = True
#             participant.save()

#             return Response(
#                 {
#                     "body": serializer.data,
#                     "message": (
#                         "Details updated successfully"
#                         if instance
#                         else "Record created successfully"
#                     ),
#                     "error": False,
#                 },
#                 status=status.HTTP_200_OK,
#             )


#         first_error = next(iter(serializer.errors.values()))[0]
#         return Response(
#             {
#                 "body": {},
#                 "message": f"Validation failed - {first_error}",
#                 "error": True,
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )


class SecondscreeningAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, *args, **kwargs):
        """
        Get all second screening records or filter by reference number.
        """
        reference_number = request.query_params.get("reference_number")

        if reference_number:
            screenings = SecondScreening.objects.filter(
                reference_number=reference_number, created_by=request.user
            )
        else:
            screenings = SecondScreening.objects.filter(created_by=request.user)

        serializer = SecondscreeningSerializer(screenings, many=True)

        if screenings.exists():
            return Response(
                {
                    "body": serializer.data,
                    "message": "Data fetched successfully",
                    "error": False,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "body": [],
                    "message": "No records found",
                    "error": True,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request, *args, **kwargs):
        """
        Create or update a Second Screening record.
        - If ID is present → update the existing record (don’t create a new one)
        - If reference_number changes → delete the old record & participant
        """
        second_screening_id = request.data.get("id")
        new_ref_number = request.data.get("reference_number", "").strip()
        instance = None
        old_ref_number = None

        # ✅ Fetch the instance if ID is provided (auto-detect old reference number)
        if second_screening_id not in [None, "", "null"]:
            try:
                instance = SecondScreening.objects.get(id=int(second_screening_id))
                old_ref_number = instance.reference_number  # auto-detect old ref
            except (SecondScreening.DoesNotExist, ValueError, TypeError):
                instance = None

        print(f"🔹 Old Reference Number: {old_ref_number}")
        print(f"🔹 New Reference Number: {new_ref_number}")

        # ✅ Prevent duplicate reference numbers (excluding current record)
        if new_ref_number:
            existing = SecondScreening.objects.filter(reference_number=new_ref_number)
            if instance:
                existing = existing.exclude(id=instance.id)
            if existing.exists():
                return Response(
                    {
                        "body": {},
                        "message": "This reference number already exists. Please use a unique one.",
                        "error": True,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # ✅ Validate and save (create or update)
        serializer = SecondscreeningSerializer(
            instance, data=request.data, partial=True
        )
        if serializer.is_valid():
            second_screening = serializer.save(created_by=request.user)

            # ✅ If the reference number changed → delete old records
            if old_ref_number and old_ref_number != new_ref_number:
                print(f"🗑️ Deleting old record with reference_number={old_ref_number}")
                SecondScreening.objects.filter(reference_number=old_ref_number).exclude(
                    id=second_screening.id
                ).delete()
                Participant.objects.filter(reference_number=old_ref_number).delete()

            # ✅ Sync with Participant (new reference)
            participant, _ = Participant.objects.get_or_create(
                reference_number=second_screening.reference_number
            )
            participant.created_by = request.user
            participant.second_screening = True
            participant.save()

            return Response(
                {
                    "body": serializer.data,
                    "message": (
                        "Record updated successfully"
                        if instance
                        else "Record created successfully"
                    ),
                    "error": False,
                },
                status=status.HTTP_200_OK,
            )

        # ❌ Handle validation errors
        first_error = next(iter(serializer.errors.values()))[0]
        return Response(
            {
                "body": {},
                "message": f"Validation failed - {first_error}",
                "error": True,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# Dispensing API
class DispensingAPIView(APIView):

    def get(self, request):
        """
        Retrieve the latest dispensing record based on reference number.
        If no record exists yet, return empty defaults with HTTP 200 to allow creation.
        """
        reference_number = request.GET.get("reference_number")

        if not reference_number:
            return Response(
                {"message": "Reference number is required", "error": True},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Clean string whitespace
        reference_number = reference_number.strip()

        latest_dispensing_record = (
            Dispensing.objects.filter(reference_number__iexact=reference_number)
            .order_by("-id")
            .first()
        )

        # If no record exists, return an empty payload instead of a 404 error
        if not latest_dispensing_record:
            return Response(
                {
                    "body": {
                        "reference_number": reference_number,
                        "frame_choice": "",
                        "lenses_type": "",
                        "pd_distance": "",
                        "comments": ""
                    },
                    "message": "No previous dispensing record found. Ready for new submission.",
                    "error": False,
                    "is_new": True
                },
                status=status.HTTP_200_OK,
            )

        serializer = DispensingSerializer(latest_dispensing_record)
        return Response(
            {"body": serializer.data, "error": False, "is_new": False}, 
            status=status.HTTP_200_OK
        )

    def post(self, request):
        """
        Save or update dispensing details.
        """
        data = request.data.copy()
        
        # Ensure reference_number whitespace is stripped if present
        if 'reference_number' in data and isinstance(data['reference_number'], str):
            data['reference_number'] = data['reference_number'].strip()

        serializer = DispensingSerializer(data=data)

        if serializer.is_valid():
            dispensing_obj = serializer.save()

            # Update Participant status
            reference_number = dispensing_obj.reference_number
            Participant.objects.filter(reference_number__iexact=reference_number).update(dispensing=True)

            return Response(
                {
                    "body": serializer.data,
                    "message": "Dispensing details saved successfully",
                    "error": False,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "body": [],
                "message": "Validation failed",
                "error": True,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# Refraction-Examination API
class RefractionExaminationAPIView(generics.ListCreateAPIView):
    queryset = RefractionExamination.objects.all()
    serializer_class = RefractionExaminationSerializer

    def post(self, request, *args, **kwargs):
        reference_number = request.data.get("reference_number")

        if not reference_number:
            return Response(
                {"message": "Reference number is required", "error": True},
                status=status.HTTP_400_BAD_REQUEST,
            )

        obj, created = RefractionExamination.objects.update_or_create(
            reference_number=reference_number,  # Lookup field
            defaults=request.data,  # Update or create with request data
        )

        # ✅ Update Participant profile to reflect the refraction examination
        try:
            participant = Participant.objects.get(reference_number=reference_number)
            participant.refraction_and_examination = (
                True  # Set refraction examination to True
            )
            participant.save()
        except Participant.DoesNotExist:
            pass  # If no participant exists, do nothing (or create if needed)

        return Response(
            {
                "body": request.data,
                "message": "Refraction Examination created successfully"
                if created
                else "Refraction Examination updated successfully",
                "error": False,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def get(self, request, *args, **kwargs):
        """Retrieve a specific Refraction Examination record based on reference number"""
        reference_number = request.GET.get(
            "reference_number"
        )  # Get reference_number from query params

        if not reference_number:
            return Response(
                {"message": "Reference number is required", "error": True},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Fetch the latest record for the given reference_number
        refraction_exam = (
            RefractionExamination.objects.filter(reference_number=reference_number)
            .order_by("-id")
            .first()
        )

        if not refraction_exam:
            return Response(
                {"message": "Refraction Examination record not found", "error": True},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.serializer_class(refraction_exam)  # Serialize the record

        return Response(
            {"body": serializer.data, "error": False}, status=status.HTTP_200_OK
        )


# # class DiagnosisView(APIView):
# class DiagnosisView(APIView):
#     def post(self, request):
#         reference_number = request.data.get("reference_number")

#         if not reference_number:
#             return Response(
#                 {"message": "Reference number is required", "error": True},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         obj, created = Diagnosis.objects.update_or_create(
#             reference_number=reference_number, defaults=request.data
#         )

#         # ✅ Update Participant profile to reflect the diagnosis
#         try:
#             participant = Participant.objects.get(reference_number=reference_number)
#             participant.diagnosis_management = True  # Set diagnosis to True
#             participant.save()
#         except Participant.DoesNotExist:
#             pass  # If no participant exists, do nothing (or create if needed)

#         return Response(
#             {
#                 "message": "Diagnosis saved successfully"
#                 if created
#                 else "Diagnosis updated successfully",
#                 "error": False,
#             },
#             status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
#         )

#     def get(self, request):
#         """
#         Retrieve a specific diagnosis record based on reference number.
#         """
#         reference_number = request.query_params.get("reference_number")

#         if not reference_number:
#             return Response(
#                 {"message": "Reference number is required", "error": True},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         try:
#             diagnosis = Diagnosis.objects.get(reference_number=reference_number)
#             serializer = DiagnosisSerializer(diagnosis)
#             return Response(
#                 {
#                     "body": serializer.data,
#                     "message": "Diagnosis record retrieved successfully",
#                     "error": False,
#                 },
#                 status=status.HTTP_200_OK,
#             )
#         except Diagnosis.DoesNotExist:
#             return Response(
#                 {"message": "Diagnosis record not found", "error": True},
#                 status=status.HTTP_404_NOT_FOUND,
#             )


class DiagnosisView(APIView):
    """
    Handles creation, update, and retrieval of Diagnosis records.
    """

    def post(self, request):
        reference_number = request.data.get("reference_number")

        if not reference_number:
            return Response(
                {"message": "Reference number is required", "error": True},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if record exists → update else create
        try:
            instance = Diagnosis.objects.get(reference_number=reference_number)
            serializer = DiagnosisSerializer(instance, data=request.data, partial=True)
        except Diagnosis.DoesNotExist:
            serializer = DiagnosisSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            # ✅ Update Participant status
            Participant.objects.update_or_create(
                reference_number=reference_number,
                defaults={"diagnosis_management": True},
            )

            return Response(
                {
                    "message": "Diagnosis saved successfully",
                    "error": False,
                    "body": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"message": "Invalid data", "error": True, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def get(self, request):
        """
        Retrieve a diagnosis record by reference_number.
        """
        reference_number = request.query_params.get("reference_number")

        if not reference_number:
            return Response(
                {"message": "Reference number is required", "error": True},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            diagnosis = Diagnosis.objects.get(reference_number=reference_number)
            serializer = DiagnosisSerializer(diagnosis)
            return Response(
                {
                    "message": "Diagnosis record retrieved successfully",
                    "error": False,
                    "body": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Diagnosis.DoesNotExist:
            return Response(
                {"message": "Diagnosis record not found", "error": True},
                status=status.HTTP_404_NOT_FOUND,
            )


# profile-API
# class ParticipantView(APIView):
#     def get(self, request, *args, **kwargs):
#         reference_number = request.query_params.get("reference_number")

#         if not reference_number:
#             return Response({"error": "Reference number is required"}, status=status.HTTP_400_BAD_REQUEST)

#         participant = get_object_or_404(Participant, reference_number=reference_number)
#         serializer = ParticipantSerializer(participant)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def post(self, request, *args, **kwargs):
#         reference_number = request.data.get("reference_number")

#         if not reference_number:
#             return Response({"error": "Reference number is required"}, status=status.HTTP_400_BAD_REQUEST)

#         participant, _ = Participant.objects.get_or_create(reference_number=reference_number)
#         serializer = ParticipantSerializer(participant)
#         return Response(serializer.data, status=status.HTTP_200_OK)


class ParticipantView(APIView):
    def get(self, request, *args, **kwargs):
        reference_number = request.query_params.get("reference_number")

        if not reference_number:
            return Response(
                {"error": "Reference number is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        participant = get_object_or_404(Participant, reference_number=reference_number)
        serializer = ParticipantSerializer(participant)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        reference_number = request.data.get("reference_number")

        if not reference_number:
            return Response(
                {"error": "Reference number is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ Get or create participant
        participant, _ = Participant.objects.get_or_create(
            reference_number=reference_number
        )
        participant_data = ParticipantSerializer(participant).data

        # ✅ Fetch First Screening details
        try:
            first_screening = Firstscreening.objects.get(
                reference_number=reference_number
            )
            first_screening_data = FirstScreeningSerializer(first_screening).data
        except Firstscreening.DoesNotExist:
            first_screening_data = {}

        # ✅ Fetch Second Screening details
        try:
            second_screening = SecondScreening.objects.get(
                reference_number=reference_number
            )
            second_screening_data = SecondscreeningSerializer(second_screening).data
        except SecondScreening.DoesNotExist:
            second_screening_data = {}

        # ✅ Merge all data
        response_data = {
            **participant_data,  # Include participant details
            **first_screening_data,  # Include first screening details
            **second_screening_data,  # Include second screening details
        }

        return Response(response_data, status=status.HTTP_200_OK)


# SpectacleHistory API
class SpectacleHistoryAPIView(APIView):
    def post(self, request):
        reference_number = request.data.get("reference_number")

        if not reference_number:
            return Response(
                {"message": "Reference number is required", "error": True},
                status=status.HTTP_400_BAD_REQUEST,
            )

        obj, created = SpectacleHistory.objects.update_or_create(
            reference_number=reference_number,  # Lookup field
            defaults=request.data,  # Update or create with request data
        )

        # Try updating Participant model if it exists
        try:
            participant = Participant.objects.get(reference_number=reference_number)
            participant.spectacle_wearing_history = (
                True  # Assuming this field exists in Participant model
            )
            participant.save()
        except Participant.DoesNotExist:
            pass  # If Participant does not exist, do nothing

        return Response(
            {
                "message": "Spectacle history saved successfully"
                if created
                else "Spectacle history updated successfully",
                "error": False,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def get(self, request):
        """
        Retrieve a specific spectacle history record based on reference number.
        """
        reference_number = request.query_params.get("reference_number")

        if not reference_number:
            return Response(
                {"message": "Reference number is required", "error": True},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            spectacle_history = SpectacleHistory.objects.get(
                reference_number=reference_number
            )
            serializer = SpectacleHistorySerializer(spectacle_history)
            return Response(
                {
                    "body": serializer.data,
                    "message": "Spectacle history record retrieved successfully",
                    "error": False,
                },
                status=status.HTTP_200_OK,
            )
        except SpectacleHistory.DoesNotExist:
            return Response(
                {"message": "Spectacle history record not found", "error": True},
                status=status.HTTP_404_NOT_FOUND,
            )


# Surgery-History API
class SurgeryTreatmentHistoryAPIView(APIView):
    def post(self, request):
        reference_number = request.data.get("reference_number")

        if not reference_number:
            return Response(
                {"message": "Reference number is required", "error": True},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Extract surgery_history from the payload
        surgery_history = request.data.pop("surgery_history", None)

        # Prepare the data for update_or_create
        defaults = request.data

        # If surgery_history is provided, map it to the model fields
        if surgery_history:
            left_eye = surgery_history.get("leftEye", {})
            right_eye = surgery_history.get("rightEye", {})

            defaults.update(
                {
                    "left_eye_trauma": left_eye.get("trauma", False),
                    "left_eye_cataract": left_eye.get("cataract", False),
                    "left_eye_squint": left_eye.get("squint", False),
                    "left_eye_lid": left_eye.get("lid", False),
                    "left_eye_other": left_eye.get("other", False),
                    "left_eye_none": left_eye.get("none", False),
                    "right_eye_trauma": right_eye.get("trauma", False),
                    "right_eye_cataract": right_eye.get("cataract", False),
                    "right_eye_squint": right_eye.get("squint", False),
                    "right_eye_lid": right_eye.get("lid", False),
                    "right_eye_other": right_eye.get("other", False),
                    "right_eye_none": right_eye.get("none", False),
                }
            )

        # Update or create the record
        obj, created = SurgeryTreatmentHistory.objects.update_or_create(
            reference_number=reference_number, defaults=defaults
        )

        # Serialize the response
        serializer = SurgeryTreatmentHistorySerializer(obj)

        return Response(
            {
                "message": "SurgeryTreatmentHistory saved successfully"
                if created
                else "SurgeryTreatmentHistory updated successfully",
                "data": serializer.data,
                "error": False,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def get(self, request):
        """Retrieve Surgery Treatment History record based on reference number"""
        reference_number = request.GET.get(
            "reference_number"
        )  # Get reference_number from query params

        if not reference_number:
            return Response(
                {"message": "Reference number is required", "error": True},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Fetch the record, if it exists
        surgery_history = get_object_or_404(
            SurgeryTreatmentHistory, reference_number=reference_number
        )

        # Formatting response in the required structure
        response_data = {
            "reference_number": surgery_history.reference_number,
            "surgery_history": {
                "leftEye": {
                    "trauma": surgery_history.left_eye_trauma,
                    "cataract": surgery_history.left_eye_cataract,
                    "squint": surgery_history.left_eye_squint,
                    "lid": surgery_history.left_eye_lid,
                    "other": surgery_history.left_eye_other,
                    "none": surgery_history.left_eye_none,
                },
                "rightEye": {
                    "trauma": surgery_history.right_eye_trauma,
                    "cataract": surgery_history.right_eye_cataract,
                    "squint": surgery_history.right_eye_squint,
                    "lid": surgery_history.right_eye_lid,
                    "other": surgery_history.right_eye_other,
                    "none": surgery_history.right_eye_none,
                },
            },
        }

        return Response(
            {"body": response_data, "error": False}, status=status.HTTP_200_OK
        )


# # other-Medical API
# class OtherMedicalIssueResponseView(APIView):
#     def get(self, request):
#         reference_number = request.query_params.get("reference_number")

#         if not reference_number:
#             return Response(
#                 {"body": {}, "message": "Reference number is required", "error": True},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         medical_issue = OtherMedicalIssueResponse.objects.filter(
#             reference_number__iexact=reference_number.strip()
#         ).first()

#         if not medical_issue:
#             return Response(
#                 {
#                     "body": {},
#                     "message": "Medical issue response not found",
#                     "error": True,
#                 },
#                 status=status.HTTP_404_NOT_FOUND,
#             )

#         serializer = OtherMedicalIssueResponseSerializer(medical_issue)

#         return Response(
#             {
#                 "body": serializer.data,
#                 "message": "Medical issue response retrieved successfully",
#                 "error": False,
#             },
#             status=status.HTTP_200_OK,
#         )

#     def post(self, request):
#         serializer = OtherMedicalIssueResponseSerializer(data=request.data)

#         if serializer.is_valid():
#             obj = serializer.save()  # Save the validated data
#             reference_number = serializer.validated_data.get("reference_number")

#             # Try updating Participant model if it exists
#             try:
#                 participant = Participant.objects.get(reference_number=reference_number)
#                 participant.other_medical_issues = (
#                     obj.other_medical_issues
#                 )  # Update field
#                 participant.save()
#             except Participant.DoesNotExist:
#                 pass  # If Participant does not exist, do nothing

#             return Response(
#                 {
#                     "body": serializer.data,
#                     "message": "Other Medical history saved successfully",
#                     "error": False,
#                 },
#                 status=status.HTTP_201_CREATED,
#             )

#         return Response(
#             {
#                 "body": {},
#                 "message": "Invalid input",
#                 "error": True,
#                 "details": serializer.errors,
#             },
#             status=status.HTTP_400_BAD_REQUEST,
#         )


class OtherMedicalIssueResponseView(APIView):
    def get(self, request):
        reference_number = request.query_params.get("reference_number")

        if not reference_number:
            return Response(
                {"body": {}, "message": "Reference number is required", "error": True},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            medical_issue = OtherMedicalIssueResponse.objects.get(
                reference_number__iexact=reference_number.strip()
            )
        except OtherMedicalIssueResponse.DoesNotExist:
            return Response(
                {
                    "body": {},
                    "message": "Medical issue response not found",
                    "error": True,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = OtherMedicalIssueResponseSerializer(medical_issue)
        return Response(
            {
                "body": serializer.data,
                "message": "Medical issue response retrieved successfully",
                "error": False,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        reference_number = request.data.get("reference_number")

        if not reference_number:
            return Response(
                {"body": {}, "message": "Reference number is required", "error": True},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = OtherMedicalIssueResponseSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            # Update or Create ek hi record per reference_number
            obj, created = OtherMedicalIssueResponse.objects.update_or_create(
                reference_number=reference_number,
                defaults={
                    "medical_issue": data.get("medical_issue"),
                    "other_medical_issues": data.get("other_medical_issues"),
                },
            )

            try:
                participant = Participant.objects.get(reference_number=reference_number)
                participant.other_medical_issues = obj.other_medical_issues
                participant.save()
            except Participant.DoesNotExist:
                pass

            return Response(
                {
                    "body": OtherMedicalIssueResponseSerializer(obj).data,
                    "message": "Other Medical history saved successfully",
                    "error": False,
                },
                status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED,
            )

        return Response(
            {
                "body": {},
                "message": "Invalid input",
                "error": True,
                "details": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# # Family-History API
# class FamilyHistoryAPIView(APIView):
#     def post(self, request):
#         reference_number = request.data.get("reference_number")

#         if not reference_number:
#             return Response(
#                 {
#                     "body": [],
#                     "message": "Failed to save Family History",
#                     "error": True,
#                     "errors": {"reference_number": ["This field is required."]},
#                 },
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         obj, created = FamilyHistory.objects.update_or_create(
#             reference_number=reference_number, defaults=request.data
#         )

#         try:
#             participant = Participant.objects.get(reference_number=reference_number)
#             participant.family_history = (
#                 True  # Assuming you have this field in Participant model
#             )
#             participant.save()
#         except Participant.DoesNotExist:
#             pass

#             # Formatting response in the required structure
#         response_data = {
#             "reference_number": obj.reference_number,
#             "family_history": {
#                 "Hypertension": obj.Hypertension,
#                 "Diabetes": obj.Diabetes,
#                 "Cataract": obj.Cataract,
#                 "Glaucoma": obj.Glaucoma,
#                 "Other_glasses": obj.Other_glasses,
#                 "Other": obj.Other,
#                 "none": obj.none,
#             },
#             "relationshipwithchild": obj.relationshipwithchild,
#             "SerachTerm": obj.search_term if obj.search_term else "",
#         }

#         return Response(
#             {
#                 "body": response_data,
#                 "message": "Family History saved successfully"
#                 if created
#                 else "Family History updated successfully",
#                 "error": False,
#             },
#             status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
#         )

#     def get(self, request):
#         """Retrieve a specific Family History record based on reference number"""
#         reference_number = request.GET.get(
#             "reference_number"
#         )  # Get reference_number from query params

#         if not reference_number:
#             return Response(
#                 {"message": "Reference number is required", "error": True},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         # Fetch the latest record for the given reference_number
#         family_history = (
#             FamilyHistory.objects.filter(reference_number=reference_number)
#             .order_by("-id")
#             .first()
#         )

#         if not family_history:
#             return Response(
#                 {"message": "Family History record not found", "error": True},
#                 status=status.HTTP_404_NOT_FOUND,
#             )

#         # Formatting response in the required structure
#         response_data = {
#             "reference_number": family_history.reference_number,
#             "family_history": {
#                 "Hypertension": family_history.Hypertension,
#                 "Diabetes": family_history.Diabetes,
#                 "Cataract": family_history.Cataract,
#                 "Glaucoma": family_history.Glaucoma,
#                 "Other_glasses": family_history.Other_glasses,
#                 "Other": family_history.Other,
#                 "none": family_history.none,
#             },
#             "relationshipwithchild": family_history.relationshipwithchild,
#             "SerachTerm": family_history.search_term
#             if family_history.search_term
#             else "",
#         }

#         return Response(
#             {"body": response_data, "error": False}, status=status.HTTP_200_OK
#         )


class FamilyHistoryAPIView(APIView):
    def post(self, request):
        reference_number = request.data.get("reference_number")

        if not reference_number:
            return Response(
                {"message": "Reference number is required", "error": True},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = request.data.copy()

        # ✅ Normalize all boolean fields: ensure True/False saved correctly
        bool_fields = [
            "Hypertension",
            "Diabetes",
            "Cataract",
            "Glaucoma",
            "Other_glasses",
            "Other",
            "none",
        ]
        for field in bool_fields:
            value = data.get(field)
            data[field] = str(value).lower() in ["true", "1", "yes"]

            # ✅ if False, remove related relationship fields
            if not data[field]:
                rel_field = f"{field}_relationship"
                if rel_field in data:
                    data.pop(rel_field, None)

        # ✅ Create or Update
        obj, created = FamilyHistory.objects.update_or_create(
            reference_number=reference_number, defaults=data
        )

        # ✅ Update Participant flag
        try:
            participant = Participant.objects.get(reference_number=reference_number)
            participant.family_history = True
            participant.save()
        except Participant.DoesNotExist:
            pass

        serializer = FamilyHistorySerializer(obj)

        return Response(
            {
                "body": serializer.data,
                "message": "Family History created successfully"
                if created
                else "Family History updated successfully",
                "error": False,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def get(self, request):
        reference_number = request.GET.get("reference_number")
        if not reference_number:
            return Response(
                {"message": "Reference number is required", "error": True},
                status=status.HTTP_400_BAD_REQUEST,
            )

        family_history = FamilyHistory.objects.filter(
            reference_number=reference_number
        ).first()
        if not family_history:
            return Response(
                {"message": "Family History record not found", "error": True},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = FamilyHistorySerializer(family_history)
        return Response(
            {"body": serializer.data, "error": False}, status=status.HTTP_200_OK
        )


# current-medical API
class CurrentMedicalAPIView(APIView):
    serializer_class = CurrentMedicalSerializer

    def post(self, request):
        reference_number = request.data.get("reference_number")

        if not reference_number:
            return Response(
                {"message": "Reference number is required", "error": True},
                status=status.HTTP_400_BAD_REQUEST,
            )

        obj, created = CurrentMedicalTreatment.objects.update_or_create(
            reference_number=reference_number, defaults=request.data
        )

        # Try updating Participant model if it exists
        try:
            participant = Participant.objects.get(reference_number=reference_number)
            participant.current_medical_treatment = (
                True  # Assuming this field exists in Participant model
            )
            participant.save()
        except Participant.DoesNotExist:
            pass  # If Participant does not exist, do nothing

        return Response(
            {
                "message": "CurrentMedicalTreatment saved successfully"
                if created
                else "CurrentMedicalTreatment updated successfully",
                "error": False,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def get(self, request):
        """Retrieve Current Medical Treatment based on reference number"""
        reference_number = request.GET.get(
            "reference_number"
        )  # Get reference_number from query params

        if not reference_number:
            return Response(
                {"message": "Reference number is required", "error": True},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Fetch the record, if it exists
        current_medical = get_object_or_404(
            CurrentMedicalTreatment, reference_number=reference_number
        )

        # Serialize the response
        serializer = CurrentMedicalSerializer(current_medical)

        return Response(
            {
                "message": "Current Medical Treatment retrieved successfully",
                "body": serializer.data,
                "error": False,
            },
            status=status.HTTP_200_OK,
        )


# Visual-Acuity API


class VisualAcuityMeasurementAPIView(APIView):
    serializer_class = VisualacuitySerializer

    def post(self, request):
        reference_number = request.data.get("reference_number")

        if not reference_number:
            return Response(
                {"message": "Reference number is required", "error": True},
                status=status.HTTP_400_BAD_REQUEST,
            )

        obj, created = VisualAcuityMeasurement.objects.update_or_create(
            reference_number=reference_number, defaults=request.data
        )

        # Try updating Participant model if it exists
        try:
            participant = Participant.objects.get(reference_number=reference_number)
            participant.measure_visual_acuity = (
                True  # Assuming this field exists in Participant model
            )
            participant.save()
        except Participant.DoesNotExist:
            pass  # If Participant does not exist, do nothing

        return Response(
            {
                "message": "Measure Visual acuity saved successfully"
                if created
                else "Measure Visual acuity updated successfully",
                "error": False,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def get(self, request):
        """Retrieve visual acuity measurement record based on reference number"""
        reference_number = request.GET.get(
            "reference_number"
        )  # Get reference_number from query params

        if not reference_number:
            return Response(
                {"message": "Reference number is required", "error": True},
                status=status.HTTP_400_BAD_REQUEST,
            )

        measurement = get_object_or_404(
            VisualAcuityMeasurement, reference_number=reference_number
        )  # Fetch the record
        serializer = self.serializer_class(measurement)  # Serialize the record

        return Response(
            {"body": serializer.data, "error": False}, status=status.HTTP_200_OK
        )


# Refraction-Spectacle API
# class RefractionSpectacleAPIView(APIView):
#     def post(self, request):
#         reference_number = request.data.get("reference_number")

#         if not reference_number:
#             return Response(
#                 {"message": "Reference number is required", "error": True},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         obj, created = RefractionSpectacle.objects.update_or_create(
#             reference_number=reference_number, defaults=request.data
#         )

#         # Try updating Participant model if it exists
#         try:
#             participant = Participant.objects.get(reference_number=reference_number)
#             participant.refraction_spectacle_presentation = (
#                 True  # Assuming this field exists in Participant model
#             )
#             participant.save()
#         except Participant.DoesNotExist:
#             pass  # If Participant does not exist, do nothing

#         return Response(
#             {
#                 "message": "RefractionSpectacle saved successfully"
#                 if created
#                 else "RefractionSpectacle updated successfully",
#                 "error": False,
#             },
#             status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
#         )

#     def get(self, request):
#         """Retrieve Refraction Spectacle based on reference number"""
#         reference_number = request.GET.get(
#             "reference_number"
#         )  # Get reference_number from query params

#         if not reference_number:
#             return Response(
#                 {"message": "Reference number is required", "error": True},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         # Fetch the record, if it exists
#         refraction_spectacle = get_object_or_404(
#             RefractionSpectacle, reference_number=reference_number
#         )

#         # Serialize the response
#         serializer = RefractionSpectacleSerializer(refraction_spectacle)

#         return Response(
#             {
#                 "message": "Refraction Spectacle retrieved successfully",
#                 "body": serializer.data,
#                 "error": False,
#             },
#             status=status.HTTP_200_OK,
#         )


class RefractionSpectacleAPIView(APIView):
    def post(self, request):
        reference_number = request.data.get("reference_number")

        if not reference_number:
            return Response(
                {"message": "Reference number is required", "error": True},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update or create record
        obj, created = RefractionSpectacle.objects.update_or_create(
            reference_number=reference_number,
            defaults=request.data,
        )

        # ✅ Update Participant model if it exists
        try:
            participant = Participant.objects.get(reference_number=reference_number)
            participant.refraction_spectacle_presentation = True
            participant.save()
        except Participant.DoesNotExist:
            pass

        return Response(
            {
                "message": "Refraction Spectacle created successfully"
                if created
                else "Refraction Spectacle updated successfully",
                "error": False,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def get(self, request):
        reference_number = request.GET.get("reference_number")
        if not reference_number:
            return Response(
                {"message": "Reference number is required", "error": True},
                status=status.HTTP_400_BAD_REQUEST,
            )

        refraction_spectacle = get_object_or_404(
            RefractionSpectacle, reference_number=reference_number
        )

        serializer = RefractionSpectacleSerializer(refraction_spectacle)

        return Response(
            {
                "message": "Refraction Spectacle retrieved successfully",
                "body": serializer.data,
                "error": False,
            },
            status=status.HTTP_200_OK,
        )


# sahithi's code
# class ComplaintView(APIView):
#     def post(self, request):
#         """
#         Create a new patient complaint with selected complaints.
#         """
#         serializer = PatientComplaintSerializer(data=request.data)
#         if serializer.is_valid():
#             # Save the patient complaint object
#             patient_complaint = serializer.save()
#             return Response(
#                 {
#                     "body": PatientComplaintSerializer(patient_complaint).data,
#                     "message": "Details updated successfully.",
#                     "error": False,
#                 },
#                 status=status.HTTP_201_CREATED,
#             )


#         return Response(
#             {"body": [], "message": "Failed to update details.", "error": True},
#             status=status.HTTP_400_BAD_REQUEST,
#         )


class ComplaintView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        reference_number = request.query_params.get("reference_number")

        if reference_number:
            complaints = PatientComplaint.objects.filter(
                reference_number=reference_number, created_by=request.user
            )
        else:
            complaints = PatientComplaint.objects.filter(created_by=request.user)

        serializer = PatientComplaintSerializer(complaints, many=True)

        if serializer.data:
            return Response(
                {
                    "body": serializer.data,
                    "message": "Data fetched successfully",
                    "error": False,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"body": [], "message": "No records found", "error": True},
            status=status.HTTP_404_NOT_FOUND,
        )

    def post(self, request, *args, **kwargs):
        reference_number = request.data.get("reference_number")
        if not reference_number:
            return Response(
                {"body": {}, "message": "Reference number is required", "error": True},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance = PatientComplaint.objects.filter(
            reference_number=reference_number
        ).first()
        if instance:
            serializer = PatientComplaintSerializer(
                instance, data=request.data, partial=True
            )
        else:
            serializer = PatientComplaintSerializer(data=request.data)

        if serializer.is_valid():
            complaint = serializer.save(created_by=request.user)

            return Response(
                {
                    "body": PatientComplaintSerializer(complaint).data,
                    "message": "Details updated successfully"
                    if instance
                    else "Details created successfully",
                    "error": False,
                },
                status=status.HTTP_200_OK if instance else status.HTTP_201_CREATED,
            )
        first_error = next(iter(serializer.errors.values()))[0]
        return Response(
            {
                "body": {},
                "message": f"Validation failed - {first_error}",
                "error": True,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class FailedStudents(APIView):
    def get(self, request):
        # Get the school ID from query parameters
        school_id = request.query_params.get("school")

        # Check if school ID is provided
        if not school_id:
            return Response(
                {"body": [], "message": "School ID is required.", "error": True},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Fetch the school by ID
            school = school.objects.get(id=school_id)
        except school.DoesNotExist:
            return Response(
                {"body": [], "message": "School not found.", "error": True},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Filter students who failed the first screening for the given school
        failed_students = Firstscreening.objects.filter(
            school=school, first_screening_passed=False
        )

        # Serialize the failed students data
        serializer = FirstScreeningSerializer(failed_students, many=True)

        return Response(
            {
                "body": serializer.data,
                "message": "Failed students retrieved successfully.",
                "error": False,
            },
            status=status.HTTP_200_OK,
        )

    # class ReferenceNumberCheckAPIView(APIView):
    def post(self, request):
        file = request.FILES.get("file")

        if not file:
            return Response(
                {"message": "No file uploaded", "error": True},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Load the Excel file
            workbook = openpyxl.load_workbook(file)
            sheet = workbook.active

            reference_numbers = set()  # Store unique reference numbers
            existing_reference_numbers = (
                set()
            )  # Store reference numbers already in the database
            pattern = re.compile(
                r"^[A-Za-z0-9]+$"
            )  # Match alphanumeric reference numbers (e.g., DGF288401)

            # Loop through all rows and cells to find all valid reference numbers
            for row in sheet.iter_rows(values_only=True):
                for cell in row:
                    if isinstance(cell, str) and pattern.match(
                        cell
                    ):  # Check for valid reference number
                        ref_number = cell.strip()
                        # Check if reference number already exists in the database
                        if Firstscreening.objects.filter(
                            reference_number=ref_number
                        ).exists():
                            existing_reference_numbers.add(ref_number)
                        reference_numbers.add(ref_number)

            if not reference_numbers:
                return Response(
                    {
                        "message": "No valid reference numbers found in the file",
                        "error": True,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if any reference numbers already exist in the database
            if existing_reference_numbers:
                return Response(
                    {
                        "message": f"The following reference numbers already exist: {', '.join(existing_reference_numbers)}",
                        "is_unique": False,
                        "error": True,
                    },
                    status=status.HTTP_409_CONFLICT,
                )

            # If all reference numbers are valid and unique, return success without the actual numbers
            return Response(
                {
                    "message": "All reference numbers are valid and unique",
                    "is_unique": True,
                    "error": False,
                },
                status=status.HTTP_200_OK,
            )

        except openpyxl.utils.exceptions.InvalidFileException:
            return Response(
                {"message": "Invalid or corrupted Excel file", "error": True},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {
                    "message": "An error occurred while processing the file",
                    "details": str(e),
                    "error": True,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


import hashlib
import time

import requests

APP_KEY = "515264"
APP_SECRET = "4vm5gdmjKsw3vs8bTPmzJhYtfvYdjTHX"


def generate_sign(params, app_secret):
    # Sort parameters alphabetically by key name
    sorted_keys = sorted(params.keys())
    sign_str = app_secret + "".join(f"{k}{params[k]}" for k in sorted_keys) + app_secret
    return hashlib.md5(sign_str.encode("utf-8")).hexdigest().upper()


class AliExpressProductSearchAPIView(APIView):
    def post(self, request):
        keyword = request.data.get("keyword")
        if not keyword:
            return Response(
                {"error": "Missing 'keyword' in request body"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        url = "https://api-sg.aliexpress.com/sync"

        params = {
            "method": "aliexpress.affiliate.product.query",
            "app_key": APP_KEY,
            "sign_method": "md5",
            "timestamp": str(int(time.time() * 1000)),
            "keywords": keyword,
            "fields": "product_id,product_title,product_url,image_url,sale_price",
            "page_no": "1",
            "page_size": "5",
            "target_currency": "USD",
            "target_language": "EN",
            "country": "US",
        }

        # Generate signature
        params["sign"] = generate_sign(params, APP_SECRET)

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return Response(response.json())
        except requests.exceptions.RequestException as e:
            return Response(
                {"error": "AliExpress API request failed", "details": str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )


# get all participants registered by the logged in user
# class UserParticipantsAPIView(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user_refs = Participant.objects.filter(created_by=request.user).values_list(
#             "reference_number", flat=True
#         )

#         print("User Reference Numbers:", list(user_refs))

#         combined_data = []

#         for ref in user_refs:
#             # merged_obj = {"reference_number": ref}
#             merged_obj = {}

#             # FirstScreening
#             first = Firstscreening.objects.filter(reference_number=ref).first()
#             if first:
#                 merged_obj.update(FirstScreeningSerializer(first).data)

#             # SecondScreening
#             second = SecondScreening.objects.filter(reference_number=ref).first()

#             if second:
#                 merged_obj.update(SecondscreeningSerializer(second).data)

#             # Dispensing (latest)
#             dispensing = (
#                 Dispensing.objects.filter(reference_number=ref).order_by("-id").first()
#             )

#             if dispensing:
#                 print("done dispensing-->>>")
#                 merged_obj.update(DispensingSerializer(dispensing).data)

#             if merged_obj:
#                 print("merged_obj-->>>", merged_obj)

#                 combined_data.append(merged_obj)

#         return Response(
#             {
#                 "body": combined_data,
#                 "message": "All participants retrieved successfully.",
#                 "error": False,
#             },
#             status=status.HTTP_200_OK,
#         )


class UserParticipantsAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_refs = Participant.objects.filter(created_by=request.user).values_list(
            "reference_number", flat=True
        )

        combined_data = []
        for ref in user_refs:
            merged = {}
            first = Firstscreening.objects.filter(reference_number=ref).first()
            second = SecondScreening.objects.filter(reference_number=ref).first()
            dispensing = (
                Dispensing.objects.filter(reference_number=ref).order_by("-id").first()
            )

            if first:
                merged.update(FirstScreeningSerializer(first).data)
            if second:
                merged.update(SecondscreeningSerializer(second).data)
            if dispensing:
                merged.update(DispensingSerializer(dispensing).data)

            if merged:
                combined_data.append(merged)

        return Response(
            {
                "body": combined_data,
                "message": "All participants retrieved successfully.",
                "error": False,
            },
            status=status.HTTP_200_OK,
        )
