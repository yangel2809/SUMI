"""
Copyright (c) 2022 - present, Daniel Escalona
"""
from django.urls import path, re_path
from . import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('production/', OrderListView.as_view(), name='order_list'),
    path('production/asign/', OrderAssign, name='order_assign'),
    path('production/<str:pk>/', OrderDetails, name='order_details'),
    path('production/<str:pk>/edit/', OrderEdit, name='order_edit'),
    path('production/<str:pk>/delete/', OrderDelete, name='order_delete'),
    #Order childs

    #PrinterBoot----------------------------------
    path('production/<str:pk>/printer/<str:ck>/', OrderPrinterBootDetails, name='production_printer_details'),
    path('production/<str:pk>/printer/', OrderPrinterBootAdd, name='production_printer_add'),
    path('production/<str:pk>/printer/<str:ck>/edit', OrderPrinterBootEdit, name='production_printer_edit'),
    path('production_printer/<str:pk>/delete', OrderPrinterBootDelete, name='production_printer_delete'),

    #LaminatorBoot--------------------------------
    path('production/<str:pk>/laminator/<str:ck>/', OrderLaminatorBootDetails, name='production_laminator_details'),
    path('production/<str:pk>/laminator/', OrderLaminatorBootAdd, name='production_laminator_add'),
    path('production/<str:pk>/laminator/<str:ck>/edit', OrderLaminatorBootEdit, name='production_laminator_edit'),
    path('production_laminator/<str:pk>/delete', OrderLaminatorBootDelete, name='production_laminator_delete'),

    #TechSpecs-----------------------------------
    path('production/<str:pk>/techspecs/', OrderTechSpecsDetails, name='production_techspecs_details'),
    path('production/<str:pk>/techspecs/add', OrderTechSpecsAdd, name='production_techspecs_add'),
    path('production/<str:pk>/techspecs/<str:ck>/edit', OrderTechSpecsEdit, name='production_techspecs_edit'),
    #path('production_cutter/<str:pk>/delete', OrderTechSpecDelete, name='production_techspecs_delete'),
    
    #CutterBoot----------------------------------
    path('production/<str:pk>/cutter/', OrderCutterBootAdd, name='production_cutter_add'),
    path('production/<str:pk>/cutter/<str:ck>/', OrderCutterBootDetails, name='production_cutter_details'),
    path('production/<str:pk>/cutter/<str:ck>/edit', OrderCutterBootEdit, name='production_cutter_edit'),
    path('production_cutter/<str:pk>/delete', OrderCutterBootDelete, name='production_cutter_delete'),

    #Export Boot----------------------------------
    path('production/<str:pk>/<str:machine>/<str:ck>/export', views.ExportBoot, name='export_boot_production'), # type: ignore

    #Reports--------------------------------------
    path('production/<str:pr>/<str:machine>/<str:ck>/report', views.ProductionReportAdd, name='report_boot_pr'),
    path('production/<str:pr>/<str:machine>/<str:ck>/report/<str:rp>/edit', views.ProductionReportEdit, name='edit_report'),
    path('production/<str:pr>/<str:machine>/<str:ck>/report/<str:rp>/delete', views.ProductionReportDelete, name='delete_report_pr'),
    #Bobbin
    path('production/<str:tr>/<str:machine>/<str:ck>/report/<str:tf>/bobbin/add', views.ReportBobbinAdd, name='report_bobbin_add'),
    path('production/bobbin/<str:pk>/delete', views.ReportBobbinDelete, name='bobbin_delete'),
    #Test
    path('production/test_file/essay/<str:pk>/<str:op>/add/<str:machine>/<str:ck>', views.ReportEssayAdd, name='test_file_essay_add'),
    path('production/test_file/essay/<str:pk>/<str:op>/edit/<str:machine>/<str:ck>', views.ReportEssayEdit, name='test_file_essay_edit'),
    path('production/test_file/essay/<str:pk>/delete', views.ReportEssayDelete, name='test_file_essay_delete'),

    #Annex----------------------------------------
    path('production/<str:pk>/annexes/', OrderAnnexes, name='production_annexes'),
    path('production/<str:pk>/annexes/add/', OrderAnnexAdd, name='production_annex_add'),
    path('production/<str:pk>/annexes/<str:ck>/delete/', OrderAnnexDelete, name='production_annex_delete'),

    path('test_or_order/', test_or_order, name='test_or_order'),
]