from django.urls import path
from . import views

urlpatterns=[
    path('register', views.RegisterAPIView.as_view(), name='register'),
    path('login', views.UserLoginView.as_view(), name='login'),
    path('logout', views.UserLogoutView.as_view(), name='logout'),
    path('send-otp', views.SendOTPView.as_view(), name='send-otp'),
    path('verify-otp', views.VerifyOTPView.as_view(), name='verify-otp'),
    path('password-reset', views.ResetPasswordView.as_view(), name='password-reset'),
    # path('School', views.SchoolListView.as_view(), name='School'),
    # path('students-register', views.RegisterStudentView.as_view(), name='student-register'),
    path('first-screening', views.FirstScreeningAPIView.as_view(), name='first-screening-create'),
    path('Comprehensive', views.ComprehensiveAPIView.as_view(), name='Comprehensive'),
    path('Second-screening', views.SecondscreeningAPIView.as_view(), name='Comprehensive'),
    path('Dispensing', views.DispensingAPIView.as_view(), name='Retest'),
    path('Refraction-Examination', views.RefractionExaminationAPIView.as_view(), name='Refraction-Examination'),
    path('Diagnosis', views.DiagnosisView.as_view(), name='Diagnosis'),
    path('Profile', views.ParticipantView.as_view(), name='Profile'),
    path('Spectacle-History', views.SpectacleHistoryAPIView.as_view(), name='Spectacle-History'),
    path('Surgery-History', views.SurgeryTreatmentHistoryAPIView.as_view(), name='Surgery-History'),
    path('Other-Medical-History', views.OtherMedicalIssueResponseView.as_view(), name='Medical-History'),
    path('Family-History', views.FamilyHistoryAPIView.as_view(), name='Family-History'),
    path('Current_Medical', views.CurrentMedicalAPIView.as_view(), name='Current_Medical'),
    path('VisualAcuity', views.VisualAcuityMeasurementAPIView.as_view(), name='VisualAcuity'),
    path('RefractionSpectacle', views.RefractionSpectacleAPIView.as_view(), name='RefractionSpectacle'),
    path('complaints', views.ComplaintView.as_view(), name='complaints'),
    path('failed-students', views.FailedStudents.as_view(), name='failed_students_for_second_screening'),
    # path('reference_  number', views.ReferenceNumberCheckAPIView.as_view(), name='reference_number')
    path('school', views.schoolView.as_view(), name='school'),
    path('ali-text-search', views.AliExpressProductSearchAPIView.as_view(), name='ali-text-search'),
]