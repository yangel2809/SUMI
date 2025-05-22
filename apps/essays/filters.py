import django_filters
from django_filters import *
from apps.home.models import Client
from .models import *
from django.forms import *

#Client Provider MaterialType Unit
class TestRequestFilter(django_filters.FilterSet):
    production_order = CharFilter(field_name="production_order", lookup_expr="icontains", widget=TextInput(attrs={'name':'search_production_order', 'form':'filter', 'autocomplete':'off', 'class':'form-control myform-search', 'maxlength':'7', 'placeholder':'Órden de Producción', 'id':'s_op'}))
    number = CharFilter(field_name="number", lookup_expr="icontains", widget=TextInput(attrs={'name':'search_number', 'form':'filter', 'autocomplete':'off', 'class':'form-control myform-search', 'maxlength':'13', 'placeholder':'N° Solicitud', 'id':'s_no'}))
    client = ModelChoiceFilter(queryset=Client.objects.all(), field_name="client", widget=Select(attrs={'name':'search_client', 'form':'filter', 'autocomplete':'off', 'class':'form-control align-items-center text-center', 'aria-label':'Cliente', 'id':'s_cl'}))
    product = CharFilter(field_name="product", lookup_expr="icontains", widget=TextInput(attrs={'name':'search_product', 'form':'filter', 'autocomplete':'off', 'class':'form-control myform-search', 'aria-label':'', 'placeholder':'Nombre del Producto', 'id':'s_pr'}))
    date = DateFilter(field_name="date", lookup_expr="gte", widget=TextInput(attrs={'name':'search_date','title':'A partir de la fecha selecionada', 'form':'filter', 'autocomplete':'off', 'class':'form-control myform-search', 'maxlength':'9', 'placeholder':'D/M/A', 'id':'s_dt'}))
    class Meta:
        model = ArtRequest
        fields = (  
            'product',          
            'number',
            'production_order',
            'date',
            'closed',
            )
        localized_fields=('date',)
