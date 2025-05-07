"""
Copyright (c) 2022 - present, Daniel Escalona
"""
import django_filters
from django_filters import *
from .models import *
from django.forms import *

#Client Provider MaterialType Unit
class PlanFilter(django_filters.FilterSet):
    product = CharFilter(field_name="product", lookup_expr="unaccent__icontains", widget=TextInput(attrs={'name':'search_product', 'form':'filter', 'autocomplete':'off', 'class':'form-control myform-search', 'aria-label':'', 'placeholder':'Nombre del Producto', 'id':'s_pr'}))
    pc = CharFilter(field_name="pc", lookup_expr="icontains", widget=TextInput(attrs={'name':'search_pc', 'form':'filter', 'autocomplete':'off', 'class':'form-control myform-search', 'maxlength':'8', 'placeholder':'X00-00', 'id':'s_pc'}))
    gp_code = CharFilter(field_name="gp_code", lookup_expr="icontains", widget=TextInput(attrs={'name':'search_gp_code', 'form':'filter', 'autocomplete':'off', 'class':'form-control myform-search', 'maxlength':'13', 'placeholder':'Código GP', 'id':'s_gp'}))
    rev_date = DateFilter(field_name="rev_date", lookup_expr="gte", widget=TextInput(attrs={'name':'search_rev_date','title':'A partir de la fecha selecionada', 'form':'filter', 'autocomplete':'off', 'class':'form-control myform-search', 'maxlength':'9', 'placeholder':'D/M/A', 'id':'s_dt'}))
    client = ModelChoiceFilter(queryset=Client.objects.all(), field_name="client", widget=Select(attrs={'name':'search_client', 'form':'filter', 'autocomplete':'off', 'class':'form-control align-items-center text-center', 'aria-label':'Cliente', 'id':'s_cl'}))
    class Meta:
        model = Plan
        fields = (
            'product',
            'pc',
            'gp_code',
            'rev_date',
            'client',
            )
        localized_fields=('rev_date',)

class MaterialFilter(django_filters.FilterSet):
    name = CharFilter(field_name="name", lookup_expr="icontains", widget=TextInput(attrs={'name':'search_name', 'form':'filter', 'autocomplete':'off', 'class':'form-control myform-search', 'placeholder':'Nombre', 'id':'s_nm'}))
    material_type = ModelChoiceFilter(queryset = MaterialType.objects.all(), field_name="material_type", widget=Select(attrs={'name':'search_material_type', 'form':'filter', 'autocomplete':'off', 'class':'form-control align-items-center text-center', 'id':'id_mt'}))
    provider = ModelChoiceFilter(queryset = Provider.objects.all(), field_name="provider", widget=Select(attrs={'name':'search_provider', 'form':'filter', 'autocomplete':'off', 'class':'form-control align-items-center text-center', 'id':'id_pv'}))
    class Meta:
        model = Material
        fields = (            
            'name',
            'material_type',
            'provider',
            )

class EssayFilter(django_filters.FilterSet):
    name = CharFilter(field_name="name", lookup_expr="icontains", widget=TextInput(attrs={'name':'search_name', 'form':'filter', 'autocomplete':'off', 'class':'form-control myform-search', 'placeholder':'Nombre', 'id':'s_nm'}))
    unit = ModelChoiceFilter(queryset = Unit.objects.all(), field_name="unit", widget=Select(attrs={'name':'search_provider', 'form':'filter', 'autocomplete':'off', 'class':'form-control align-items-center text-center', 'aria-label':'Proveedor', 'id':'id_unit'}))
    method = CharFilter(field_name="method", lookup_expr="icontains", widget=TextInput(attrs={'name':'search_method', 'form':'filter', 'autocomplete':'off', 'class':'form-control myform-search', 'placeholder':'Metodo', 'id':'s_mt'}))
    detail = CharFilter(field_name="detail", lookup_expr="icontains", widget=TextInput(attrs={'name':'search_detail', 'form':'filter', 'autocomplete':'off', 'class':'form-control myform-search', 'placeholder':'Descripción', 'id':'s_dt'}))
    class Meta:
        model = Essay
        fields = (            
            'name',
            'unit',
            'method', 
            'detail',
            )

class ClientFilter(django_filters.FilterSet):
    name = CharFilter(field_name="name", lookup_expr="icontains", widget=TextInput(attrs={'name':'search_name', 'form':'filter', 'autocomplete':'off', 'class':'form-control myform-search', 'placeholder':'Nombre', 'id':'s_nm'}))
    rif_num = CharFilter(field_name="rif_num", lookup_expr="icontains", widget=TextInput(attrs={'name':'search_rif_num', 'form':'filter', 'autocomplete':'off', 'class':'form-control myform-search', 'placeholder':'Número RIF', 'id':'s_rf'}))
    class Meta:
        model = Client
        fields = (            
            'name',
            'rif_num'
            )

class ProviderFilter(django_filters.FilterSet):
    name = CharFilter(field_name="name", lookup_expr="icontains", widget=TextInput(attrs={'name':'search_name', 'form':'filter', 'autocomplete':'off', 'class':'form-control myform-search', 'placeholder':'Nombre', 'id':'s_nm'}))
    #rif_num = CharFilter(field_name="rif_num", lookup_expr="icontains", widget=TextInput(attrs={'name':'search_rif_num', 'form':'filter', 'autocomplete':'off', 'class':'form-control myform-search', 'placeholder':'Número RIF', 'id':'s_rf'}))
    class Meta:
        model = Provider
        fields = (            
            'name',
            #'rif_num'
            )