from django.urls import path
from django.utils.translation import gettext_lazy as _

from .views import *

app_name = 'buildings'
urlpatterns = [
    path('', BuildingListCreateView.as_view(), name = 'building_list'),
    path(_('<slug>/'), BuildingRedirectView.as_view(), name = 'building_slug'),
    path(_('<slug>/change/'), BuildingUpdateView.as_view(),
        name = 'building_change'),
    path(_('<slug>/delete/'), BuildingDeleteView.as_view(),
        name = 'building_delete'),
    path(_('<slug>/set/add/'), PlanSetCreateView.as_view(),
        name = 'planset_create'),
    path('<slug:build_slug>/set/<slug:set_slug>/',
        BuildingDetailView.as_view(), name = 'building_detail'),
    path(_('<slug:build_slug>/set/<slug:set_slug>/change/'),
        PlanSetUpdateView.as_view(), name = 'planset_change'),
    path(_('<slug:build_slug>/set/<slug:set_slug>/delete/'),
        PlanSetDeleteView.as_view(), name = 'planset_delete'),
    path(_('<slug>/plan/add/'), PlanCreateView.as_view(),
        name = 'plan_create'),
    path(_('<slug:build_slug>/plan/<slug:plan_slug>/'),
        PlanDetailView.as_view(), name = 'plan_detail'),
    path(_('<slug:build_slug>/plan/<slug:plan_slug>/change/'),
        PlanUpdateView.as_view(), name = 'plan_change'),
    path(_('<slug:build_slug>/plan/<slug:plan_slug>/delete/'),
        PlanDeleteView.as_view(), name = 'plan_delete'),
    path(_('<slug>/station/add/'), PhotoStationCreateView.as_view(),
        name = 'station_create'),
    path(_('<slug:build_slug>/station/<slug:stat_slug>/'),
        StationImageListCreateView.as_view(), name = 'station_detail'),
    path(_('<slug:build_slug>/station/<slug:stat_slug>/change/'),
        PhotoStationUpdateView.as_view(), name = 'station_change'),
    path(_('<slug:build_slug>/station/<slug:stat_slug>/delete/'),
        PhotoStationDeleteView.as_view(), name = 'station_delete'),
    path(_('<slug:build_slug>/station/<slug:stat_slug>/image/<pk>/change'),
        StationImageUpdateView.as_view(), name = 'image_change'),
    path(_('<slug:build_slug>/station/<slug:stat_slug>/image/<pk>/delete'),
        StationImageDeleteView.as_view(), name = 'image_delete'),
    path(_('<slug>/stations/<int:year>/<int:month>/<int:day>/'),
        StationImageDayArchiveView.as_view(), name = 'image_day'),
    path(_('<slug>/family/add/'), FamilyListCreateView.as_view(),
        name = 'family_list_create'),
    path(_('<slug:build_slug>/family/<slug:fam_slug>/change/'),
        FamilyUpdateView.as_view(), name = 'family_change'),
    path(_('<slug:build_slug>/family/<slug:fam_slug>/delete/'),
        FamilyDeleteView.as_view(), name = 'family_delete'),
    path(_('<slug>/element/add/'), ElementCreateView.as_view(),
        name = 'element_create'),
    path(_('<slug>/element/<pk>/change/'), ElementUpdateView.as_view(),
        name = 'element_change'),
    path(_('<slug>/element/<pk>/delete/'), ElementDeleteView.as_view(),
        name = 'element_delete'),
    path(_('<slug>/element/download/'), building_element_download,
        name = 'element_download'),
    ]
