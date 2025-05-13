# -*- encoding: utf-8 -*-
#Copyright (c) 2022 - present, Daniel Escalona

from django.urls import path, re_path
from .views import *
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [

    # The index
    path('entry_elements/', indexEntryElement.as_view(), name='entry_element'),
    path('test_requests/', views.indexTestRequest, name='test_request'),
    path('test_requests_art/', views.indexTestRequestArt, name='test_request_art'),
    path('exit_elements/', indexExitElement.as_view(), name='exit_element'),
    path('personal/<str:set>/', indexPersonal, name='personal'),
    #path('art_requests/', views.indexArtRequest, name='art_request'),  # Nueva ruta

    #ajax
    path('x-test_requests/', ajaxTestRequest, name='x-test_requests'),

    #Entry Element
    path('entry_elements/add/', addEntryElement, name='add_entry_element'),
    path('entry_elements/<str:pk>/', viewEntryElement, name='view_entry_element'),
    path('entry_elements/<str:pk>/edit/', editEntryElement, name='edit_entry_element'),
    path('entry_elements/<str:pk>/delete/', deleteEntryElement, name='delete_entry_element'),
    
    #Exit Element
    path('exit_elements/add/<str:tr>/', addExitElement, name='add_exit_element'),
    path('exit_elements/<str:pk>/', viewExitElement, name='view_exit_element'),
    path('exit_elements/<str:pk>/edit/', editExitElement, name='edit_exit_element'),
    path('exit_elements/<str:pk>/delete/', deleteExitElement, name='delete_exit_element'),

    #Test Request
    re_path(r'^test_requests/add(?:/(?P<entry_element_id>\d+))?/$', addTestRequest, name='add_test_request'),
    path('test_requests/<str:pk>/', viewTestRequest, name='view_test_request'),
    path('test_requests/<str:pk>/clone/', cloneTestRequest, name='clone_test_request'),
    path('test_requests/<str:pk>/edit/', editTestRequest, name='edit_test_request'),
    path('test_requests/<str:pk>/delete/', deleteTestRequest, name='delete_test_request'),
    path('test_requests/<str:pk>/restore/', restoreTestRequest, name='restore_test_request'),
    path('test_requests/<str:pk>/deleteTrue/', deleteTrueTestRequest, name='delete_true_test_request'),
    path('test_requests/<str:pk>/close/', closeTestRequest, name='close_test_request'),
    path('test_requests/<str:pk>/open/', openTestRequest, name='open_test_request'),
    path('test_requests/<str:pk>/archive/', archiveTestRequest, name='archive_test_request'),
    path('test_requests/<str:pk>/unarchive/', unarchiveTestRequest, name='unarchive_test_request'),

    #Test Request Art
    #re_path(r'^test_requests_art/add(?:/(?P<entry_element_id>\d+))?/$', addTestRequestArt, name='add_test_request_art'),
    path('test_requests_art/<str:pk>/', viewTestRequestArt, name='view_test_request_art'),
    path('test_requests_art/<str:pk>/clone/', cloneTestRequestArt, name='clone_test_request_art'),
    path('test_requests_art/<str:pk>/edit/', editTestRequestArt, name='edit_test_request_art'),
    path('test_requests_art/<str:pk>/delete/', deleteTestRequestArt, name='delete_test_request_art'),
    path('test_requests_art/<str:pk>/restore/', restoreTestRequestArt, name='restore_test_request_art'),
    path('test_requests_art/<str:pk>/deleteTrue/', deleteTrueTestRequestArt, name='delete_true_test_request_art'),
    path('test_requests_art/<str:pk>/close/', closeTestRequestArt, name='close_test_request_art'),
    path('test_requests_art/<str:pk>/open/', openTestRequestArt, name='open_test_request_art'),
    path('test_requests_art/<str:pk>/archive/', archiveTestRequestArt, name='archive_test_request_art'),
    path('test_requests_art/<str:pk>/unarchive/', unarchiveTestRequestArt, name='unarchive_test_request_art'),

    #Printer Boot
    path('test_requests/<str:pk>/printer/<str:ck>/', viewPrinterBoot, name='view_printer_boot_tr'),
    path('test_requests/<str:tr>/printer/', addPrinterBootTR, name='add_printer_boot_tr'),
    path('test_requests/<str:tr>/printer/<str:ck>/edit/', editPrinterBootTR, name='edit_printer_boot_tr'),
    path('test_requests/<str:tr>/printer/<str:ck>/delete/', deletePrinterBootTR, name='delete_printer_boot_tr'),
    
    #Laminator Boot 
    path('test_requests/<str:pk>/laminator/<str:ck>/', viewLaminatorBoot, name='view_laminator_boot_tr'),
    path('test_requests/<str:tr>/laminator/', addLaminatorBootTR, name='add_laminator_boot_tr'),
    path('test_requests/<str:tr>/laminator/<str:ck>/edit/', editLaminatorBootTR, name='edit_laminator_boot_tr'),
    path('test_requests/<str:tr>/laminator/<str:ck>/delete/', deleteLaminatorBootTR, name='delete_laminator_boot_tr'),
    
    #export Boot
    path('test_requests/<str:pk>/<str:machine>/<str:ck>/export', ExportBoot, name='export_boot_essay'),

    #Report
    path('test_requests/<str:tr>/<str:boot_type>/<str:ck>/report/', Report, name='report_boot'),
    path('test_requests/<str:tr>/<str:boot_type>/<str:ck>/report/<str:rp>/edit/', editReport, name='edit_report'),
    path('test_requests/<str:tr>/<str:boot_type>/<str:ck>/report/<str:rp>/delete/', deleteReport, name='delete_report'),

    #TestFileEssays
    path('test_file_essay/<str:pk>/<str:tr>/add/<str:site>/<str:ck>/', addTestFileEssay, name='test_file_essay_add'),
    path('test_file_essay/<str:pk>/<str:tr>/edit/<str:site>/<str:ck>/', editTestFileEssay, name='test_file_essay_edit'),
    path('test_file_essay/<str:pk>/delete/', deleteTestFileEssay, name='test_file_essay_delete'),

    #Bobbin
    path('bobbin/<str:pk>/delete/', deleteBobbin, name='bobbin_delete'),
    path('test_requests/<str:tr>/<str:machine>/<str:ck>/report/<str:tf>/result/add/', addResult, name='machine_essay_result'),

    #Cutter Boot
    path('test_requests/<str:pk>/cutter/<str:ck>/', viewCutterBoot, name='view_cutter_boot_tr'),
    path('test_requests/<str:tr>/cutter/', addCutterBootTR, name='add_cutter_boot_tr'),
    path('test_requests/<str:tr>/cutter/<str:ck>/edit/', editCutterBootTR, name='edit_cutter_boot_tr'),
    path('test_requests/<str:tr>/cutter/<str:ck>/delete/', deleteCutterBootTR, name='delete_cutter_boot_tr'),

    #Technical Specifications
    path('test_requests/<str:pk>/tech_specs/', viewTechSpecs, name='view_tech_specs'),
    path('test_requests/<str:tr>/tech_specs/add/', addTechSpecs, name='add_tech_spec'),
    path('test_requests/<str:tr>/tech_specs/<str:ck>/edit/', editTechSpecs, name='edit_tech_spec'),
    path('test_requests/<str:tr>/tech_specs/<str:ck>/delete/', deleteTechSpecs, name='delete_tech_spec'),

    #Personal
    path('analyst/add/', addQualityAnalyst, name='add_analyst'),
    path('analyst/<str:pk>/edit/', editQualityAnalyst, name='edit_analyst'),
    path('analyst/<str:pk>/delete/', deleteQualityAnalyst, name='delete_analyst'),
    path('operator/add/', addProductionOperator, name='add_operator'),
    path('operator/<str:pk>/edit/', editProductionOperator, name='edit_operator'),
    path('operator/<str:pk>/delete/', deleteProductionOperator, name='delete_operator'),

    #Annexes
    path('test_requests/<str:pk>/annexes/', viewAnnex, name='view_annexes'),
    path('test_requests/<str:tr>/annexes/add/', addAnnex, name='add_annex'),
    path('test_requests/<str:tr>/annexes/<str:ck>/delete/', deleteAnnex, name='delete_annex'),
]