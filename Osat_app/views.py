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

COUNTRY_CODE_MAP = {
    "AF": "AFG",
    "AFGHANISTAN": "AFG",
    "AL": "ALB",
    "ALBANIA": "ALB",
    "DZ": "DZA",
    "ALGERIA": "DZA",
    "AD": "AND",
    "ANDORRA": "AND",
    "AO": "AGO",
    "ANGOLA": "AGO",
    "AG": "ATG",
    "ANTIGUA AND BARBUDA": "ATG",
    "AR": "ARG",
    "ARGENTINA": "ARG",
    "AM": "ARM",
    "ARMENIA": "ARM",
    "AU": "AUS",
    "AUSTRALIA": "AUS",
    "AT": "AUT",
    "AUSTRIA": "AUT",
    "AZ": "AZE",
    "AZERBAIJAN": "AZE",
    "BS": "BHS",
    "BAHAMAS": "BHS",
    "THE BAHAMAS": "BHS",
    "BH": "BHR",
    "BAHRAIN": "BHR",
    "BD": "BGD",
    "BANGLADESH": "BGD",
    "BB": "BRB",
    "BARBADOS": "BRB",
    "BY": "BLR",
    "BELARUS": "BLR",
    "BE": "BEL",
    "BELGIUM": "BEL",
    "BZ": "BLZ",
    "BELIZE": "BLZ",
    "BJ": "BEN",
    "BENIN": "BEN",
    "BT": "BTN",
    "BHUTAN": "BTN",
    "BO": "BOL",
    "BOLIVIA": "BOL",
    "BOLIVIA (PLURINATIONAL STATE OF)": "BOL",
    "BA": "BIH",
    "BOSNIA AND HERZEGOVINA": "BIH",
    "BW": "BWA",
    "BOTSWANA": "BWA",
    "BR": "BRA",
    "BRAZIL": "BRA",
    "BN": "BRN",
    "BRUNEI DARUSSALAM": "BRN",
    "BRUNEI": "BRN",
    "BG": "BGR",
    "BULGARIA": "BGR",
    "BF": "BFA",
    "BURKINA FASO": "BFA",
    "BI": "BDI",
    "BURUNDI": "BDI",
    "CV": "CPV",
    "CABO VERDE": "CPV",
    "CAPE VERDE": "CPV",
    "KH": "KHM",
    "CAMBODIA": "KHM",
    "CM": "CMR",
    "CAMEROON": "CMR",
    "CA": "CAN",
    "CANADA": "CAN",
    "CF": "CAF",
    "CENTRAL AFRICAN REPUBLIC": "CAF",
    "TD": "TCD",
    "CHAD": "TCD",
    "CL": "CHL",
    "CHILE": "CHL",
    "CN": "CHN",
    "CHINA": "CHN",
    "CO": "COL",
    "COLOMBIA": "COL",
    "KM": "COM",
    "COMOROS": "COM",
    "CG": "COG",
    "CONGO": "COG",
    "REPUBLIC OF THE CONGO": "COG",
    "CD": "COD",
    "DEMOCRATIC REPUBLIC OF THE CONGO": "COD",
    "DRC": "COD",
    "CR": "CRI",
    "COSTA RICA": "CRI",
    "CI": "CIV",
    "CÔTE D'IVOIRE": "CIV",
    "COTE DIVOIRE": "CIV",
    "IVORY COAST": "CIV",
    "HR": "HRV",
    "CROATIA": "HRV",
    "CU": "CUB",
    "CUBA": "CUB",
    "CY": "CYP",
    "CYPRUS": "CYP",
    "CZ": "CZE",
    "CZECHIA": "CZE",
    "CZECH REPUBLIC": "CZE",
    "DK": "DNK",
    "DENMARK": "DNK",
    "DJ": "DJI",
    "DJIBOUTI": "DJI",
    "DM": "DMA",
    "DOMINICA": "DMA",
    "DO": "DOM",
    "DOMINICAN REPUBLIC": "DOM",
    "EC": "ECU",
    "ECUADOR": "ECU",
    "EG": "EGY",
    "EGYPT": "EGY",
    "SV": "SLV",
    "EL SALVADOR": "SLV",
    "GQ": "GNQ",
    "EQUATORIAL GUINEA": "GNQ",
    "ER": "ERI",
    "ERITREA": "ERI",
    "EE": "EST",
    "ESTONIA": "EST",
    "SZ": "SWZ",
    "ESWATINI": "SWZ",
    "SWAZILAND": "SWZ",
    "ET": "ETH",
    "ETHIOPIA": "ETH",
    "FJ": "FJI",
    "FIJI": "FJI",
    "FI": "FIN",
    "FINLAND": "FIN",
    "FR": "FRA",
    "FRANCE": "FRA",
    "GA": "GAB",
    "GABON": "GAB",
    "GM": "GMB",
    "GAMBIA": "GMB",
    "THE GAMBIA": "GMB",
    "GE": "GEO",
    "GEORGIA": "GEO",
    "DE": "DEU",
    "GERMANY": "DEU",
    "GH": "GHA",
    "GHANA": "GHA",
    "GR": "GRC",
    "GREECE": "GRC",
    "GD": "GRD",
    "GRENADA": "GRD",
    "GT": "GTM",
    "GUATEMALA": "GTM",
    "GN": "GIN",
    "GUINEA": "GIN",
    "GW": "GNB",
    "GUINEA-BISSAU": "GNB",
    "GY": "GUY",
    "GUYANA": "GUY",
    "HT": "HTI",
    "HAITI": "HTI",
    "HN": "HND",
    "HONDURAS": "HND",
    "HU": "HUN",
    "HUNGARY": "HUN",
    "IS": "ISL",
    "ICELAND": "ISL",
    "IN": "IND",
    "INDIA": "IND",
    "ID": "IDN",
    "INDONESIA": "IDN",
    "IR": "IRN",
    "IRAN": "IRN",
    "IRAN (ISLAMIC REPUBLIC OF)": "IRN",
    "IQ": "IRQ",
    "IRAQ": "IRQ",
    "IE": "IRL",
    "IRELAND": "IRL",
    "IL": "ISR",
    "ISRAEL": "ISR",
    "IT": "ITA",
    "ITALY": "ITA",
    "JM": "JAM",
    "JAMAICA": "JAM",
    "JP": "JPN",
    "JAPAN": "JPN",
    "JO": "JOR",
    "JORDAN": "JOR",
    "KZ": "KAZ",
    "KAZAKHSTAN": "KAZ",
    "KE": "KEN",
    "KENYA": "KEN",
    "KI": "KIR",
    "KIRIBATI": "KIR",
    "KP": "PRK",
    "NORTH KOREA": "PRK",
    "DEMOCRATIC PEOPLE'S REPUBLIC OF KOREA": "PRK",
    "KR": "KOR",
    "SOUTH KOREA": "KOR",
    "REPUBLIC OF KOREA": "KOR",
    "XK": "XKX",
    "KOSOVO": "XKX",
    "KW": "KWT",
    "KUWAIT": "KWT",
    "KG": "KGZ",
    "KYRGYZSTAN": "KGZ",
    "LA": "LAO",
    "LAOS": "LAO",
    "LAO PEOPLE'S DEMOCRATIC REPUBLIC": "LAO",
    "LV": "LVA",
    "LATVIA": "LVA",
    "LB": "LBN",
    "LEBANON": "LBN",
    "LS": "LSO",
    "LESOTHO": "LSO",
    "LR": "LBR",
    "LIBERIA": "LBR",
    "LY": "LBY",
    "LIBYA": "LBY",
    "LI": "LIE",
    "LIECHTENSTEIN": "LIE",
    "LT": "LTU",
    "LITHUANIA": "LTU",
    "LU": "LUX",
    "LUXEMBOURG": "LUX",
    "MG": "MDG",
    "MADAGASCAR": "MDG",
    "MW": "MWI",
    "MALAWI": "MWI",
    "MY": "MYS",
    "MALAYSIA": "MYS",
    "MV": "MDV",
    "MALDIVES": "MDV",
    "ML": "MLI",
    "MALI": "MLI",
    "MT": "MLT",
    "MALTA": "MLT",
    "MH": "MHL",
    "MARSHALL ISLANDS": "MHL",
    "MR": "MRT",
    "MAURITANIA": "MRT",
    "MU": "MUS",
    "MAURITIUS": "MUS",
    "MX": "MEX",
    "MEXICO": "MEX",
    "FM": "FSM",
    "MICRONESIA": "FSM",
    "MICRONESIA (FEDERATED STATES OF)": "FSM",
    "MD": "MDA",
    "MOLDOVA": "MDA",
    "REPUBLIC OF MOLDOVA": "MDA",
    "MC": "MCO",
    "MONACO": "MCO",
    "MN": "MNG",
    "MONGOLIA": "MNG",
    "ME": "MNE",
    "MONTENEGRO": "MNE",
    "MA": "MAR",
    "MOROCCO": "MAR",
    "MZ": "MOZ",
    "MOZAMBIQUE": "MOZ",
    "MM": "MMR",
    "MYANMAR": "MMR",
    "BURMA": "MMR",
    "NA": "NAM",
    "NAMIBIA": "NAM",
    "NR": "NRU",
    "NAURU": "NRU",
    "NP": "NPL",
    "NEPAL": "NPL",
    "NL": "NLD",
    "NETHERLANDS": "NLD",
    "THE NETHERLANDS": "NLD",
    "NZ": "NZL",
    "NEW ZEALAND": "NZL",
    "NI": "NIC",
    "NICARAGUA": "NIC",
    "NE": "NER",
    "NIGER": "NER",
    "NG": "NGA",
    "NIGERIA": "NGA",
    "MK": "MKD",
    "NORTH MACEDONIA": "MKD",
    "NO": "NOR",
    "NORWAY": "NOR",
    "OM": "OMN",
    "OMAN": "OMN",
    "PK": "PAK",
    "PAKISTAN": "PAK",
    "PW": "PLW",
    "PALAU": "PLW",
    "PS": "PSE",
    "PALESTINE": "PSE",
    "STATE OF PALESTINE": "PSE",
    "PA": "PAN",
    "PANAMA": "PAN",
    "PG": "PNG",
    "PAPUA NEW GUINEA": "PNG",
    "PY": "PRY",
    "PARAGUAY": "PRY",
    "PE": "PER",
    "PERU": "PER",
    "PH": "PHL",
    "PHILIPPINES": "PHL",
    "THE PHILIPPINES": "PHL",
    "PL": "POL",
    "POLAND": "POL",
    "PT": "PRT",
    "PORTUGAL": "PRT",
    "QA": "QAT",
    "QATAR": "QAT",
    "RO": "ROU",
    "ROMANIA": "ROU",
    "RU": "RUS",
    "RUSSIA": "RUS",
    "RUSSIAN FEDERATION": "RUS",
    "RW": "RWA",
    "RWANDA": "RWA",
    "KN": "KNA",
    "SAINT KITTS AND NEVIS": "KNA",
    "LC": "LCA",
    "SAINT LUCIA": "LCA",
    "VC": "VCT",
    "SAINT VINCENT AND THE GRENADINES": "VCT",
    "WS": "WSM",
    "SAMOA": "WSM",
    "SM": "SMR",
    "SAN MARINO": "SMR",
    "ST": "STP",
    "SAO TOME AND PRINCIPE": "STP",
    "SÃO TOMÉ AND PRÍNCIPE": "STP",
    "SA": "SAU",
    "SAUDI ARABIA": "SAU",
    "SN": "SEN",
    "SENEGAL": "SEN",
    "RS": "SRB",
    "SERBIA": "SRB",
    "SC": "SYC",
    "SEYCHELLES": "SYC",
    "SL": "SLE",
    "SIERRA LEONE": "SLE",
    "SG": "SGP",
    "SINGAPORE": "SGP",
    "SK": "SVK",
    "SLOVAKIA": "SVK",
    "SI": "SVN",
    "SLOVENIA": "SVN",
    "SB": "SLB",
    "SOLOMON ISLANDS": "SLB",
    "SO": "SOM",
    "SOMALIA": "SOM",
    "ZA": "ZAF",
    "SOUTH AFRICA": "ZAF",
    "SS": "SSD",
    "SOUTH SUDAN": "SSD",
    "ES": "ESP",
    "SPAIN": "ESP",
    "LK": "LKA",
    "SRI LANKA": "LKA",
    "SD": "SDN",
    "SUDAN": "SDN",
    "SR": "SUR",
    "SURINAME": "SUR",
    "SE": "SWE",
    "SWEDEN": "SWE",
    "CH": "CHE",
    "SWITZERLAND": "CHE",
    "SY": "SYR",
    "SYRIA": "SYR",
    "SYRIAN ARAB REPUBLIC": "SYR",
    "TW": "TWN",
    "TAIWAN": "TWN",
    "TJ": "TJK",
    "TAJIKISTAN": "TJK",
    "TZ": "TZA",
    "TANZANIA": "TZA",
    "UNITED REPUBLIC OF TANZANIA": "TZA",
    "TH": "THA",
    "THAILAND": "THA",
    "TL": "TLS",
    "TIMOR-LESTE": "TLS",
    "EAST TIMOR": "TLS",
    "TG": "TGO",
    "TOGO": "TGO",
    "TO": "TON",
    "TONGA": "TON",
    "TT": "TTO",
    "TRINIDAD AND TOBAGO": "TTO",
    "TN": "TUN",
    "TUNISIA": "TUN",
    "TR": "TUR",
    "TURKEY": "TUR",
    "TÜRKIYE": "TUR",
    "TURKIYE": "TUR",
    "TM": "TKM",
    "TURKMENISTAN": "TKM",
    "TV": "TUV",
    "TUVALU": "TUV",
    "UG": "UGA",
    "UGANDA": "UGA",
    "UA": "UKR",
    "UKRAINE": "UKR",
    "AE": "ARE",
    "UNITED ARAB EMIRATES": "ARE",
    "UAE": "ARE",
    "GB": "GBR",
    "UK": "GBR",
    "UNITED KINGDOM": "GBR",
    "US": "USA",
    "USA": "USA",
    "UNITED STATES": "USA",
    "UNITED STATES OF AMERICA": "USA",
    "UY": "URY",
    "URUGUAY": "URY",
    "UZ": "UZB",
    "UZBEKISTAN": "UZB",
    "VU": "VUT",
    "VANUATU": "VUT",
    "VA": "VAT",
    "VATICAN CITY": "VAT",
    "HOLY SEE": "VAT",
    "VE": "VEN",
    "VENEZUELA": "VEN",
    "VENEZUELA (BOLIVARIAN REPUBLIC OF)": "VEN",
    "VN": "VNM",
    "VIETNAM": "VNM",
    "VIET NAM": "VNM",
    "YE": "YEM",
    "YEMEN": "YEM",
    "ZM": "ZMB",
    "ZAMBIA": "ZMB",
    "ZW": "ZWE",
    "ZIMBABWE": "ZWE",
}


def resolve_country_prefix(data) -> str:
    raw_code = str(data.get("country_code") or "").strip().upper()
    raw_country = str(data.get("country") or "").strip().upper()

    for candidate in (raw_code, raw_country):
        if candidate in COUNTRY_CODE_MAP:
            return COUNTRY_CODE_MAP[candidate]

    cleaned = "".join(ch for ch in (raw_code or raw_country) if ch.isalpha())
    if len(cleaned) >= 3:
        return cleaned[:3]
    if len(cleaned) > 0:
        return cleaned
    return "SS"


class FirstScreeningAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FirstScreeningSerializer(data=request.data)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    ref_num = request.data.get("reference_number")
                    if not ref_num or ref_num == "":
                        prefix = resolve_country_prefix(request.data)
                        ref_num = f"{prefix}-{uuid.uuid4().hex[:8].upper()}"
                        while Firstscreening.objects.filter(reference_number=ref_num).exists():
                            ref_num = f"{prefix}-{uuid.uuid4().hex[:8].upper()}"

                    # 1. Save FirstScreening instance with reference_number
                    first_screening = serializer.save(
                        created_by=request.user,
                        reference_number=ref_num,
                    )

                    # 2. Safely get or create the linked Participant record
                    participant, created = Participant.objects.get_or_create(
                        reference_number=ref_num,
                        defaults={
                            "created_by": request.user,
                            "first_screening": True,
                        },
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

           
