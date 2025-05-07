"""
Copyright (c) 2022 - present, Daniel Escalona
"""

from django.urls import path, re_path
from . import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # The index
    path('', views.index, name='home'),
    path('plans/', views.indexPlans, name='plans'),
    #path('plans-0/', views.indexPlans0, name='plans-0'),
    #path('plans/disincorporated/', views.indexPlansDisincorporated, name='plans-disincorporated'),
    #path('plans/deleted/', views.indexPlansDeleted, name='plans-deleted'),
    path('clients/', views.indexClient, name='clients'),
    path('providers/', views.indexProviders, name='providers'),
    path('materials/', views.indexMaterials, name='materials'),
    path('materials/types/', views.indexMaterialTypes, name='material_types'),
    path('essays/', views.indexEssays, name='essays'),
    path('essays/units/', views.indexUnits, name='units'),
    #ajax-f
    path('x-materials/', views.ajaxMaterials, name='x-materials'),
    path('x-materials/add/', views.ajaxMaterialsAdd, name='x-add_material'),
    path('x-material-types/', views.ajaxMaterialTypes, name='x-material_types'),
    path('x-material-types/add/', views.ajaxMaterialTypesAdd, name='x-add_material_types'),
    path('x-providers/', views.ajaxProviders, name='x-providers'),
    #forms----------------------
    #Plan
    path('plans/add/', views.PlanCreate, name='add_plan'),
    path('plans/<str:pk>/', views.viewPlan, name='plan_view'),
    path('plans/<str:pk>/pdf/', views.pdfPlan, name='plan_pdf'),
    path('plans/<str:pk>/edit/', views.PlanUpdate, name='edit_plan'),
    path('plans/<str:pk>/disincorporate/', views.disincorporatePlan, name='disincorporate_plan'),
    path('plans/<str:pk>/disincorporate-request/', views.disincorporatePlanRequest, name='disincorporate_request'),
    path('plans/<str:pk>/reject-disincorporate-request/', views.rejectdisincorporatePlanRequest, name='reject_disincorporate_request'),
    path('plans/<str:pk>/reincorporate/', views.reincorporatePlan, name='reincorporate_plan'),
    path('plans/<str:pk>/delete/', views.deletePlan, name='delete_plan'),
    path('plans/<str:pk>/clone/', views.clonePlan, name='clone_plan'),
    path('plans/<str:pk>/restore/', views.restorePlan, name='restore_plan'),
    path('plans/<str:pk>/perm_delete/', views.deleteTruePlan, name='delete_true_plan'),
    path('plans/deleted/delete_mass/', views.deleteTruePlanMass, name='delete_true_plan_mass'),
    #Provider
    path('providers/add/', views.addProvider, name='add_provider'),
    path('providers/<str:pk>/edit', views.editProvider, name='edit_provider'),
    path('providers/<str:pk>/delete/', views.deleteProvider, name='delete_provider'),
    #Client
    path('clients/add/', views.addClient, name='add_client'),
    path('clients/<str:pk>/edit/', views.editClient, name='edit_client'),
    path('clients/<str:pk>/delete/', views.deleteClient, name='delete_client'),
    #Material
    path('materials/add/', views.addMaterial, name='add_material'),
    path('materials/<str:pk>/edit/', views.editMaterial, name='edit_material'),
    path('materials/<str:pk>/delete/', views.deleteMaterial, name='delete_material'),
    #Material Type
    path('materials/types/add/', views.addMaterialType, name='add_material_type'),
    path('materials/types/<str:pk>/edit/', views.editMaterialType, name='edit_material_type'),
    path('materials/types/<str:pk>/delete/', views.deleteMaterialType, name='delete_material_type'),
    #Essay
    path('essays/add/', views.addEssay, name='add_essay'),
    path('essays/<str:pk>/edit/', views.editEssay, name='edit_essay'),
    path('essays/<str:pk>/delete/', views.deleteEssay, name='delete_essay'),
    #Unit
    path('essays/units/add/', views.addUnit, name='add_unit'),
    path('essays/units/<str:pk>/edit/', views.editUnit, name='edit_unit'),
    path('essays/units/<str:pk>/delete/', views.deleteUnit, name='delete_unit'),
] 
