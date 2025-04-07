"""
URL configuration for lims project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from equipment.views import *
from core.views import *
from methods.views import *
from quality.views import *
from staff.views import *
from documents.views import *
from rest_framework.authtoken.views import obtain_auth_token
from dashboard.views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    # CORE
    path('', index, name='index'),
    path('error404/', error404, name='error404'),

    # Center
    path('centers/', CenterListView.as_view(), name='center_list'),
    path('centers/add/', CenterCreateView.as_view(), name='center_add'),
    path('centers/<int:pk>/edit/', CenterUpdateView.as_view(), name='center_edit'),
    path('centers/<int:pk>/delete/', CenterDeleteView.as_view(), name='center_delete'),

    # OrganizationalUnit
    path('orgunits/', OrgUnitListView.as_view(), name='orgunit_list'),
    path('orgunits/add/', OrgUnitCreateView.as_view(), name='orgunit_add'),
    path('orgunits/<int:pk>/edit/', OrgUnitUpdateView.as_view(), name='orgunit_edit'),
    path('orgunits/<int:pk>/delete/', OrgUnitDeleteView.as_view(), name='orgunit_delete'),

    # Laboratory
    path('labs/', LaboratoryListView.as_view(), name='laboratory_list'),
    path('labs/add/', LaboratoryCreateView.as_view(), name='laboratory_add'),
    path('labs/<int:pk>/edit/', LaboratoryUpdateView.as_view(), name='laboratory_edit'),
    path('labs/<int:pk>/delete/', LaboratoryDeleteView.as_view(), name='laboratory_delete'),

    # Users
    path('login/', login_view, name='login_route'),
    path('logout/', logout_view, name='logout'),
    path('ajax_logout/', logout_view, name='ajax_logout'),  # This is for the AJAX logout request    
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/add/', CustomUserCreateView.as_view(), name='user_add'),
    path('users/<int:pk>/edit/', CustomUserUpdateView.as_view(), name='user_edit'),
    path('users/<int:pk>/delete/', CustomUserDeleteView.as_view(), name='user_delete'),

    # # RESET LOZINKE (koristi ugrađene Django view-ove)
    # path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    # path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    # path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # EQUIPMENT
    path('equipment/', EquipmentListView.as_view(), name='equipment_list'),
    path('equipment/glavna/', EquipmentListView.as_view(), {'type': 'Glavna'}, name='equipment_glavna_list'),
    path('equipment/pomocna/', EquipmentListView.as_view(), {'type': 'Pomocna'}, name='equipment_pomocna_list'),
    path('equipment/add/', EquipmentCreate.as_view(), name='equipment_add'),
    path('equipment/add/<int:equipment_id>/', EquipmentCreate.as_view(), name='equipment_add'),
    path('equipment/<int:pk>/edit/', EquipmentUpdate.as_view(), name='equipment_edit'),
    path('equipment/<int:pk>/delete/', EquipmentDelete.as_view(), name='equipment_delete'),
    path('equipment/<int:pk>/', EquipmentDetailView.as_view(), name='equipment_detail'),
    # path('userequipment/', UserLabEquipmentListView.as_view(), name='user_equipment_list'),
    path('equipment/<int:equipment_id>/change_status/', change_rashodovana_status, name='change_rashodovana_status'),
    path('rashodovana_equipment/', RashodovanaEquipmentListView.as_view(), name='rashodovana_equipment_list'),
    path('equipment/<int:pk>/select_pomocna/', SelectPomocnaEquipmentView.as_view(), name='select_pomocna_equipment'),
    path('equipment/<int:equipment_id>/qr/', generate_qr_code, name='equipment_qr_code'),
    
    # CALIBRATIONS
    path('calibrations/', CalibrationListView.as_view(), name='calibration_list'),
    path('calibration/add', CalibrationCreate.as_view(), name='calibration_add_new'),
    path('calibration/add/<int:equipment_id>/', CalibrationCreate.as_view(), name='calibration_add'),
    path('calibration/<int:pk>/', CalibrationDetail.as_view(), name='calibration_detail'),
    path('calibration/<int:pk>/edit/', CalibrationUpdate.as_view(), name='calibration_edit'),
    path('calibration/<int:pk>/delete/', CalibrationDelete.as_view(), name='calibration_delete'),


    # INTERNAL CONTROL
    path('internal_control/', InternalControlListView.as_view(), name='internal_control'),
    path('internal_control/add', InternalControlCreate.as_view(), name='internal_control_add_new'),
    path('internal_control/add/<int:equipment_id>/', InternalControlCreate.as_view(), name='internal_control_add'),
    path('internal_control/<int:pk>/', InternalControlDetail.as_view(), name='internal_control_detail'),
    path('internal_control/<int:pk>/edit/', InternalControlUpdate.as_view(), name='internal_control_edit'),
    path('internal_control/<int:pk>/delete/', InternalControlDelete.as_view(), name='internal_control_delete'),
    path('internal_control/<int:pk>/select_kontrolna/', SelectControllingDevicesView.as_view(), name='select_kontrolna_equipment'),

    # REPAIR
    path('repairl/add', RepairCreate.as_view(), name='repair_add_new'),
    path('repair/add/<int:equipment_id>/', RepairCreate.as_view(), name='repair_add'),
    path('repair/<int:pk>/', RepairDetail.as_view(), name='repair_detail'),
    path('repair/<int:pk>/edit/', RepairUpdate.as_view(), name='repair_edit'),
    path('repair/<int:pk>/delete/', RepairDelete.as_view(), name='repair_delete'),

    ###STANDARD
    path('standards/', StandardListView.as_view(), name='standard_list'),
    path('standards/new/', StandardCreateView.as_view(), name='standard_create'),
    path('standards/<int:pk>/edit/', StandardUpdateView.as_view(), name='standard_edit'),
    path('standards/<int:pk>/delete/', StandardDeleteView.as_view(), name='standard_delete'),

    ### TESTING AREA AND SUBJECT
    path('testing_areas/new/', TestingAreaCreateView.as_view(), name='testing_area_create'),
    path('testing_areas/<int:pk>/edit/', TestingAreaUpdateView.as_view(), name='testing_area_update'),
    path('testing_areas/<int:pk>/delete/', TestingAreaDeleteView.as_view(), name='testing_area_delete'),
    path('test_subjects/new/', TestSubjectCreateView.as_view(), name='test_subject_create'),
    path('test_subjects/<int:pk>/edit/', TestSubjectUpdateView.as_view(), name='test_subject_update'),
    path('test_subjects/<int:pk>/delete/', TestSubjectDeleteView.as_view(), name='test_subject_delete'),
    path('testarea_subject/', CombinedListView.as_view(), name='testandarea_list'),

    ### SUBDISCIPLINE
    path('sub_disciplines/', SubDisciplineListView.as_view(), name='sub_discipline_list'),
    path('sub-discipline/<int:pk>/', SubDisciplineDetailView.as_view(), name='sub_discipline_detail'),
    path('sub_disciplines/new/', SubDisciplineCreateView.as_view(), name='sub_discipline_create'),
    path('sub_disciplines/<int:pk>/edit/', SubDisciplineUpdateView.as_view(), name='sub_discipline_update'),
    path('sub_disciplines/<int:pk>/delete/', SubDisciplineDeleteView.as_view(), name='sub_discipline_delete'),

    ### METHOD
    path('methods', MethodListView.as_view(), name='method_list'),
    path('method/<int:pk>/', MethodDetailView.as_view(), name='method_detail'),
    path('method/add/', MethodCreateView.as_view(), name='method_create'),
    path('method/<int:pk>/edit/', MethodUpdateView.as_view(), name='method_update'),
    path('method/<int:pk>/delete/', MethodDeleteView.as_view(), name='method_delete'),
    path('method/<int:pk>/select-equipment/', SelectEquipmentView.as_view(), name='select_equipment'),
    
    ### STAFF
    path('staff/', StaffListView.as_view(), name='staff_list'),
    path('staff/new/', StaffCreateView.as_view(), name='staff_create'),
    path('staff/<int:pk>/', StaffDetailView.as_view(), name='staff_detail'),
    path('staff/<int:pk>/edit/', StaffUpdateView.as_view(), name='staff_update'),
    path('staff/<int:pk>/delete/', StaffDeleteView.as_view(), name='staff_delete'),
    
    path('job_positions/', JobPositionListView.as_view(), name='job_position_list'),
    path('job_position/<int:pk>/', JobPositionDetailView.as_view(), name='job_position_detail'),
    path('job_positions/new/', JobPositionCreateView.as_view(), name='job_position_create'),
    path('job_positions/<int:pk>/edit/', JobPositionUpdateView.as_view(), name='job_position_update'),
    path('job_positions/<int:pk>/delete/', JobPositionDeleteView.as_view(), name='job_position_delete'),

    path('positions/', StaffJobPositionListView.as_view(), name='staffjobposition_list'),
    path('positions/create/', StaffJobPositionCreateView.as_view(), name='staffjobposition_create'),
    path('positions/create/<int:staff_id>/', StaffJobPositionCreateView.as_view(), name='staffjobposition_create'),
    path('positions/update/<int:pk>/', StaffJobPositionUpdateView.as_view(), name='staffjobposition_update'),
    path('positions/delete/<int:pk>/', StaffJobPositionDeleteView.as_view(), name='staffjobposition_delete'),

    path('professional_experiences/', ProfessionalExperienceListView.as_view(), name='professional_experience_list'),
    path('professional_experiences/new/', ProfessionalExperienceCreateView.as_view(), name='professional_experience_create'),
    path('professional_experiences/new/<int:staff_id>/', ProfessionalExperienceCreateView.as_view(), name='professional_experience_create'),
    path('professional_experiences/<int:pk>/edit/', ProfessionalExperienceUpdateView.as_view(), name='professional_experience_update'),
    path('professional_experiences/<int:pk>/delete/', ProfessionalExperienceDeleteView.as_view(), name='professional_experience_delete'),

    path('training_courses/', TrainingCourseListView.as_view(), name='training_course_list'),
    path('training_courses/new/', TrainingCourseCreateView.as_view(), name='training_course_create'),
    path('training_courses/new/<int:staff_id>/', TrainingCourseCreateView.as_view(), name='training_course_create'),
    path('training_courses/<int:pk>/edit/', TrainingCourseUpdateView.as_view(), name='training_course_update'),
    path('training_courses/<int:pk>/delete/', TrainingCourseDeleteView.as_view(), name='training_course_delete'),

    path('memberships/', MembershipInInternationalOrgListView.as_view(), name='membership_international_org_list'),
    path('memberships/new/', MembershipInInternationalOrgCreateView.as_view(), name='membership_international_org_create'),
    path('memberships/new/<int:staff_id>/', MembershipInInternationalOrgCreateView.as_view(), name='membership_international_org_create'),
    path('memberships/<int:pk>/edit/', MembershipInInternationalOrgUpdateView.as_view(), name='membership_international_org_update'),
    path('memberships/<int:pk>/delete/', MembershipInInternationalOrgDeleteView.as_view(), name='membership_international_org_delete'),

    path('trainings/', TrainingListView.as_view(), name='training_list'),
    path('training/<int:pk>/', TrainingDetailView.as_view(), name='training_detail'),
    path('trainings/new/', TrainingCreateView.as_view(), name='training_create'),
    path('trainings/<int:pk>/edit/', TrainingUpdateView.as_view(), name='training_update'),
    path('trainings/<int:pk>/delete/', TrainingDeleteView.as_view(), name='training_delete'),
    path('training-tests/<int:pk>/edit/', TrainingTestUpdateView.as_view(), name='edit_training_test'),
    
    # AUTORIZATION
    path('authorization_types/', AuthorizationTypeListView.as_view(), name='authorization_type_list'),
    path('authorization_types/new/', AuthorizationTypeCreateView.as_view(), name='authorization_type_create'),
    path('authorization_types/<int:pk>/edit/', AuthorizationTypeUpdateView.as_view(), name='authorization_type_update'),
    path('authorization_types/<int:pk>/delete/', AuthorizationTypeDeleteView.as_view(), name='authorization_type_delete'),
    
    path('authorizations/', AuthorizationListView.as_view(), name='authorization_list'),
    path('authorizations/new/', AuthorizationCreateView.as_view(), name='authorization_create'),
    path('authorizations/<int:pk>/edit/', AuthorizationUpdateView.as_view(), name='authorization_update'),
    path('authorizations/<int:pk>/delete/', AuthorizationDeleteView.as_view(), name='authorization_delete'),

    path('nomethodauthorizations/', NoMethodAuthorizationListView.as_view(), name='no_method_authorization_list'),
    path('nomethodauthorizations/new/', NoMethodAuthorizationCreateView.as_view(), name='no_method_authorization_create'),
    path('nomethodauthorizations/<int:pk>/edit/', NoMethodAuthorizationUpdateView.as_view(), name='no_method_authorization_update'),
    path('nomethodauthorizations/<int:pk>/delete/', NoMethodAuthorizationDeleteView.as_view(), name='no_method_authorization_delete'),

    ### QUALITY
    path('pt_schemes/', PTSchemeListView.as_view(), name='pt_scheme_list'),
    path('pt_schemes/<int:pk>/', PTSchemeDetailView.as_view(), name='pt_scheme_detail'),
    path('pt_schemes/new/', PTSchemeCreateView.as_view(), name='pt_scheme_create'),
    path('pt_schemes/<int:pk>/edit/', PTSchemeUpdateView.as_view(), name='pt_scheme_update'),
    path('pt_scheme_method/<int:pk>/edit/', PTSchemeMethodUpdateView.as_view(), name='pt_scheme_method_update'),
    path('pt_schemes/<int:pk>/delete/', PTSchemeDeleteView.as_view(), name='pt_scheme_delete'),
    path('pt_schemes/select/', PTSchemeCreateView.as_view(), name='select_method_count'),

    path('control_testings/', ControlTestingListView.as_view(), name='control_testing_list'),
    path('control_testings/<int:pk>', ControlTestingDetailView.as_view(), name='control_testing_detail'),
    path('control_testings/new/', ControlTestingCreateView.as_view(), name='control_testing_create'),
    path('control_testings/<int:pk>/edit/', ControlTestingUpdateView.as_view(), name='control_testing_update'),
    path('control_testings/<int:pk>/delete/', ControlTestingDeleteView.as_view(), name='control_testing_delete'),
  
    path('measurement_uncertainties/', MeasurementUncertaintyListView.as_view(), name='measurement_uncertainties_list'),
    path('measurement_uncertainties/new/', MeasurementUncertaintyCreateView.as_view(), name='measurement_uncertainty_create'),
    path('measurement_uncertainties/<int:pk>/edit/', MeasurementUncertaintyUpdateView.as_view(), name='measurement_uncertainty_update'),
    path('measurement_uncertainties/<int:pk>/delete/', MeasurementUncertaintyDeleteView.as_view(), name='measurement_uncertainty_delete'),

    ### DOCUMENTATION
    path('documents/', DocumentListView.as_view(), name='document_list'),
    path('documents/add/', DocumentCreateView.as_view(), name='document_create'),
    path('documents/<int:pk>/', DocumentDetailView.as_view(), name='document_detail'),
    path('documents/<int:pk>/edit/', DocumentUpdateView.as_view(), name='document_edit'),
    path('documents/<int:pk>/toggle-status/', DocumentToggleStatusView.as_view(), name='document_toggle_status'),


    path('documents/<int:document_id>/versions/add/', DocumentVersionCreateView.as_view(), name='documentversion_add'),
    path('documents/<int:document_id>/versions/', DocumentVersionListView.as_view(), name='documentversion_list'),
    path('documents/version/<int:pk>/download/', DownloadDocumentView.as_view(), name='documentversion_download'),

    path('api/token/', obtain_auth_token),  # ovo dodaj da bi mogao da koristiš token za pristup API-ju
    path('api/core/', include('core.api.urls')),  # ← dodaj ovo!    
    path('api/equipment/', include('equipment.api.urls')),  # API endpointi za opremu
    path('api/methods/', include('methods.api.urls')),
    # path('api/quality/', include('quality.api.urls')),
    # path('api/staff/', include('staff.api.urls')),
    # path('api/documents/', include('documents.api.urls')),

    # path('download/', download_populated_document, name='download_populated_document'),
    # path('select2/', include('django_select2.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)