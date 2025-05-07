"""
Copyright (c) 2022 - present, Daniel Escalona
"""
from django.urls import path, re_path
from . import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import SaleOrderListView, SaleOrderDetailView

urlpatterns = [
    path('plans/<str:pk>/sale_order', views.addSaleOrderQP, name='sale_order_qp'),
    path('sale_orders/', SaleOrderListView.as_view(), name='sale_order_list'),
    path('sale_orders/<int:pk>/', SaleOrderDetailView.as_view(), name='sale_order_view'),
    path('sale_orders/<int:pk>/edit', views.editSaleOrderQP, name='sale_order_edit'),
    
    path('sale_orders/treview/', views.review_sale_order, name='review_sale_order'),
    path('sale_orders/treview/<str:pk>/return', views.return_review_sale_order, name='return_review_sale_order'),

    path('sale_orders/<int:pk>/delete', views.deleteSaleOrderQP, name='sale_order_delete'),
    path('sale_orders/<int:pk>/restore', views.restoreSaleOrderQP, name='sale_order_restore'),
    
    path('sale_orders/<int:pk>/archive', views.archiveSaleOrderQP, name='sale_order_archive'),
    path('sale_orders/<int:pk>/unarchive', views.unarchiveSaleOrderQP, name='sale_order_unarchive'),

    #SalesTestRequest
    path('sales_test_requests/', views.indexSalesTestRequest, name='sales_test_requests'),
    path('sales_test_requests/add/', views.addSalesTestRequest, name='add_sales_test_request'),
    path('sales_test_requests/<str:pk>/edit/', views.editSalesTestRequest, name='edit_sales_test_request'),
    path('sales_test_requests/<str:pk>/delete/', views.deleteSalesTestRequest, name='delete_sales_test_request'),

    path('x_delivery_addresses/', views.get_delivery_addresses, name='get_delivery_addresses'),
]