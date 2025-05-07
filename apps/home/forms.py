"""
Copyright (c) 2022 - present, Daniel Escalona
"""
from typing import Any
from django import forms
from django.core.validators import *
from django.core.exceptions import ValidationError
from django.forms.models import inlineformset_factory, modelform_factory, modelformset_factory#, BaseFormSet, formset_factory

#from django_select2 import forms as s2forms
from django.forms import *
from .models import *
from apps.sales.models import DeliveryAddress

class PlanForm(ModelForm):
    class Meta:
        model = Plan
        fields = (
            'pc',
            'revission',
            'rev_date',
            'client',
            'product',
            'gp_code',
            'code',
            'observation',
            'continuation',
            'dispatch_conditions',
            'elaborator',
            'reviewer'          
        )
        localized_fields=('rev_date',)
        widgets = {
            'pc': TextInput(attrs={'class':'form-control myform-focus', 'pattern':'^[A-Z]\d{2}\.\d{2}(-\d{1,2})?|0{8}$', 'style':'padding-left: 65px !important;', 'placeholder':'X00.00 / X00.00-00', 'value':'00000000', 'id':'pc'}),#type: ignore
            'revission': NumberInput(attrs={'class':'form-control myform-focus text-center', 'min':'0', 'placeholder':'-', 'value':'0', 'id':'revission' }),
            'rev_date': DateInput(attrs={'class':'form-control myform-focus text-center', 'autocomplete':'off', 'placeholder':'DD/MM/AAAA', 'id':'date'}),
            'client': Select(attrs={'class':'form-control myform-focus text-center', 'aria-label':'Cliente', 'id':'id_client'}),
            'product': TextInput(attrs={'class':'form-control myform-focus', 'aria-label':'', 'placeholder':'Nombre completo del Producto', 'id':'product' }),
            'gp_code': TextInput(attrs={'class':'form-control myform-focus text-center', 'style':'text-transform: uppercase !important;', 'placeholder':'XXXXXX000X000', 'id':'gp_code' }),
            'code': TextInput(attrs={'class':'form-control myform-focus text-center', 'style':'text-transform: uppercase !important;', 'placeholder':'0000000000000', 'value':'0000000000000', 'id':'code'}),
            'observation': Textarea(attrs={'class':'form-control myform-focus', 'id':'obsrevation'}),
            'continuation': Textarea(attrs={'class':'form-control myform-focus', 'id':'continuation' }),
            'dispatch_conditions': Textarea(attrs={'class':'form-control myform-focus', 'id':'dispatch_conditions' }),
            'elaborator': TextInput(attrs={'class':'form-control myform-focus', 'aria-label':'', 'placeholder':'Nombre, Apellido y/o Cargo', 'id':'elaborator' }),
            'reviewer': TextInput(attrs={'class':'form-control myform-focus', 'aria-label':'', 'placeholder':'Nombre, Apellido y/o Cargo', 'id':'reviewer' })
        }
    def clean(self):
        cleaned_data = super().clean()

        pc = cleaned_data.get("pc")
        reviewer = cleaned_data.get("reviewer")
        
        if pc != '00000000' and reviewer == None:
            msg = "No se peude publicar un plan sin ser revisado"
            self.add_error("pc", msg)
            self.add_error("reviewer", msg)

class BaseInlineFormset(BaseInlineFormSet):
    def get_deletion_widget(self):
        return CheckboxInput(attrs={'class': 'form-check-input justify-content-center', 'title':"Marque la casilla para Eliminar después de guardar" })
        
StructureFormset = inlineformset_factory(Plan, Structure,
        fields = (
            'material_type',
            'weight',
            'w_counts',
            'thickness',
            't_counts',
            'material'
        ),
        formset=BaseInlineFormset,
        widgets = { 
            'material_type': Select(attrs={'class': 'form-control myform-focus text-center mat-type-fields', 'aria-label':'Tipo de material'}),
            'weight':  TextInput(attrs={'class': 'form-control myform-focus text-center justify-content-center', 'min':'0', 'aria-label':'Peso', 'placeholder':'0'}),
            'w_counts': CheckboxInput(attrs={'style':'display: none;'}),
            'thickness': NumberInput(attrs={'class': 'form-control myform-focus text-center justify-content-center', 'min':'0', 'aria-label':'Espesor', 'placeholder':'0'}),
            't_counts': CheckboxInput(attrs={'style':'display: none;'}),
            'material': SelectMultiple(attrs={'class': 'form-control myform-focus'})          
        }, 
        extra=0,
        can_delete=True
        )
        
TestFormset = inlineformset_factory(Plan, Test,
        fields=(
            'essay',
            'critic',
            'spec'
        ),
        formset=BaseInlineFormset,        
        widgets = {
            'essay':  Select(attrs={'class': 'form-control myform-focus text-center', 'aria-label':'Ensayo', 'placeholder':''}),
            'critic': CheckboxInput(attrs={'class': 'form-check-input justify-content-center', 'aria-label':'Variable crítica'}),
            'spec': TextInput(attrs={'class': 'form-control myform-focus', 'aria-label':'Specificación', 'title':'Omitir para Peso básico y Espesor. Especificar la varicón para ensayos de Aplicación', 'placeholder':'','style':'padding-left: 1.5rem !important'})
        },
        extra = 0,
        can_delete=True
        )

class ClientForm(ModelForm):
    class Meta:
        model = Client
        fields = (
            'name',
            'rif_type',
            'rif_num',
            )
            
        widgets ={
            'name': TextInput(attrs={'class': 'form-control myform-focus', 'aria-label':'Nombre'}),
            'rif_type': Select(attrs={'class': 'form-control flat-right text-center myform-focus', 'aria-label':'Tipo de RIF', 'id':'rif_type'}),
            'rif_num': TextInput(attrs={'class': 'form-control flat-left myform-focus height-correct', 'aria-label':'RIF', 'placeholder':'00000000-0'})
        }

    def clean(self):
        cleaned_data = super().clean()
        rif_type = cleaned_data.get('rif_type')
        rif_num = cleaned_data.get('rif_num')

        # Check if the combination already exists in the database
        existing_clients = Client.objects.filter(rif_num=rif_num, rif_type=rif_type)
        if self.instance:
            existing_clients = existing_clients.exclude(pk=self.instance.pk)

        if existing_clients.exists():
            self.add_error('rif_type', "Este RIF ya existe")

        return cleaned_data


        
DeliveryAddressFormset = inlineformset_factory(Client, DeliveryAddress,
        fields=(
            'id',
            'client',
            'address',
        ),
        formset=BaseInlineFormset,        
        widgets = {
            'id': HiddenInput(),
            'client': HiddenInput(),
            'address': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':''})
        },
        extra = 1,
        can_delete=True
        )

#, validators=[MinLengthValidator(10), validate_unicode_slug]
class ProviderForm(ModelForm):
    class Meta:
        model = Provider
        fields = (
            'name',
            #'rif_type',
            #'rif_num',
            )
        widgets ={
            'name': TextInput(attrs={'class': 'form-control myform-focus', 'aria-label':'Nombre'}),
            #'rif_type': Select(attrs={'class': 'form-control text-center myform-focus', 'aria-label':'Tipo de RIF', 'id':'rif_type'}),
            #'rif_num': TextInput(attrs={'class': 'form-control myform-focus', 'aria-label':'RIF', 'style':'border-top-left-radius:0% !important; border-left:0 !important; border-bottom-left-radius:0% !important;', 'placeholder':'00000000-0'})
        }

class MaterialForm(ModelForm):
    class Meta:
        model = Material
        fields = (
            'provider',
            'material_type',
            'name',
            )
        widgets ={
            'provider': Select(attrs={'class': 'form-control myform-focus text-center', 'id':'provider' }),
            'material_type': Select(attrs={'class': 'form-control myform-focus text-center', 'id':'material_type'}),
            'name': TextInput(attrs={'class': 'form-control myform-focus text-center', 'id':'name', 'placeholder':'Material'}),
        }

class MaterialTypeForm(ModelForm):
    class Meta:
        model = MaterialType
        fields = (
            'name',
            )
        widgets ={
            'name': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'Nombre', 'id':'name'})
        }
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if MaterialType.objects.filter(name=name).exists():
            raise forms.ValidationError("Un Tipo de material con este nombre ya existe.")
        return name


class EssayForm(ModelForm):
    class Meta:
        model = Essay
        fields = (
            'name',
            'detail',
            'method',
            'unit',
            'confidential',
            )
        widgets ={
            'name': TextInput(attrs={'class': 'form-control myform-focus'}),
            'detail': TextInput(attrs={'class': 'form-control myform-focus' }),
            'method': TextInput(attrs={'class': 'form-control myform-focus'}),
            'unit': Select(attrs={'class': 'form-control myform-focus text-center', 'id':'unit'}),
            'confidential':CheckboxInput(attrs={'class': 'form-check-input justify-content-center', 'id':'confidential'}),
        }

class UnitForm(ModelForm):
    class Meta:
        model = Unit
        fields = (
            'name',
            'symbol',
            'description'
            )
        widgets ={
            'name': TextInput(attrs={'class': 'form-control myform-focus'}),
            'symbol': TextInput(attrs={'class': 'form-control myform-focus'}),
            'description': TextInput(attrs={'class': 'form-control myform-focus'})      
        }
