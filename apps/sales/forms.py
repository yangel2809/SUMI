"""
Copyright (c) 2023 - present, Daniel Escalona
"""
from cProfile import label
import os, uuid
from django import forms
from django.utils import timezone
from django.forms import ModelForm, TextInput, Select, ModelChoiceField, CheckboxInput, BaseInlineFormSet, DateInput, NumberInput, HiddenInput
from django.forms.models import inlineformset_factory#, modelform_factory, modelformset_factory, BaseFormSet, formset_factory

from documents.validators import validate_file_type, validate_file_size
from documents.utils import limit_file_name
from documents.models import Document
from documents.forms import MultipleFileField, MultipleFileInput
from .models import *

class BaseInlineFormset(BaseInlineFormSet):
    def get_deletion_widget(self):
        return CheckboxInput(attrs={'class': 'form-check-input justify-content-center'})

    def clean(self):
        super().clean()

        # Don't do anything if some forms have errors
        if any(self.errors):
            return

        dates = [form.cleaned_data.get('delivery_date', None) for form in self.forms]
        initial_dates = [form.initial.get('delivery_date', None) for form in self.forms]

        # Check that dates are not older than their initial value (for editing)
        for i, (date, initial_date) in enumerate(zip(dates, initial_dates)):
            if date and initial_date and date < initial_date:
                self.forms[i].add_error('delivery_date', 'Delivery date must not be older than the initial date.')

        # Check that dates are in ascending order
        for i in range(len(dates) - 1):
            if dates[i] and dates[i + 1] and dates[i] > dates[i + 1]:
                self.forms[i + 1].add_error('delivery_date', 'Delivery date must be later than the previous date.')

class SaleOrderForm(ModelForm):
    class Meta:
        model = SaleOrder
        fields = (
            'plan',
            'request',
            'number',
            'request_date',
            'number_date',
            #'company',
            'origin',
            'printer',
            'unit_photo',
            'bob_or_ream',
            "price",
            "currency",
            "quantity",
            "unit",
            "tolerance",
            'delivery_address', 
            'observation', 
            'elaborator',
            'approver', 
            'representative', 
            )
        widgets ={
            'plan': Select(attrs={'class':'form-control align-items-center myform-focus text-center', 'id':'plan'}),
            'bob_or_ream': Select(attrs={'class':'form-control align-items-center myform-focus text-center', 'id':'bob_or_ream'}),
            'request': TextInput(attrs={'class': 'form-control myform-focus flat-left', 'placeholder':'-', 'id':'request'}),
            'number': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'0000000000', 'id':'number'}),
            'request_date': DateInput(attrs={'class': 'form-control myform-focus text-center justify-content-center', 'autocomplete':'off', 'id':'request_date', 'placeholder':'DD/MM/AAAA'}),
            'number_date': DateInput(attrs={'class': 'form-control myform-focus text-center justify-content-center', 'autocomplete':'off', 'id':'number_date', 'placeholder':'DD/MM/AAAA'}),
            'origin': Select(attrs={'class': 'form-control myform-focus', 'id':'origin'}),
            'printer': Select(attrs={'class': 'form-control myform-focus', 'id':'printer'}),
            'price': TextInput(attrs={'class': 'form-control myform-focus text-end flat-right', 'placeholder':'', 'id':'price'}),
            'currency': Select(attrs={'class':'form-control align-items-center myform-focus text-center flat-left', 'id':'currency'}),
            'quantity': NumberInput(attrs={'class': 'form-control myform-focus text-center justify-content-center', 'min':'0', 'placeholder':'0', 'id':'quantity'}),
            'unit': Select(attrs={'class':'text-center form-control align-items-center myform-focus', 'id':'unit'}),
            'tolerance': NumberInput(attrs={'class': 'form-control myform-focus text-center justify-content-center', 'min':'0', 'placeholder':'0', 'id':'tolerance'}),
            'delivery_address': Select(attrs={'class':'text-center form-control myform-focus', 'id':'delivery_address'}),
            'elaborator': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'elaborator'}),
            'approver': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'approver'}),
            'representative': Select(attrs={'class':'form-control align-items-center myform-focus text-center flat-right', 'id':'representative'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(SaleOrderForm, self).__init__(*args, **kwargs)
        if user:
            span = ''
            if user.first_name and user.last_name:
                span = ' '
            self.fields['elaborator'].initial = f"{user.first_name}{span}{user.last_name}"

DeliveryDateFormset = inlineformset_factory(SaleOrder, DeliveryDate,
        fields = (
            'id',
            'quantity',
            'delivery_date',
        ),
        formset=BaseInlineFormset,
        widgets = { 
            'id':HiddenInput,
            'quantity': NumberInput(attrs={'class': 'form-control myform-focus text-center justify-content-center', 'min':'0', 'aria-label':'Espesor', 'placeholder':'0'}),
            'delivery_date': DateInput(attrs={'class': 'form-control myform-focus text-center justify-content-center date-field-selector', 'autocomplete':'off', 'placeholder':'DD/MM/AAAA', 'style':'padding-right: 1.3em !important'}),
        }, 
        extra=1,
        can_delete=True
        )

class SalesTestRequestForm(ModelForm):
    class Meta:
        model = SalesTestRequest
        fields = '__all__'
        widgets = {
            'date': DateInput(attrs={'class': 'form-control myform-focus text-center justify-content-center', 'autocomplete':'off', 'placeholder':'DD/MM/AAAA', 'id': 'date'}),
            'client': Select(attrs={'class': 'form-control myform-focus text-center', 'id':'client' }),
            'company': Select(attrs={'class': 'form-control myform-focus text-center', 'id':'company',}),
            'product': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'product',}),
            'printed_sample': CheckboxInput(attrs={'class': 'form-check-input mt-2', 'id':'printed_sample',}),
            'mechanical_plan': CheckboxInput(attrs={'class': 'form-check-input mt-2', 'id':'mechanical_plan',}),
            'technichal_specs': CheckboxInput(attrs={'class': 'form-check-input mt-2', 'id':'technichal_specs',}),
            'arts': CheckboxInput(attrs={'class': 'form-check-input mt-2', 'id':'arts',}),
            'product_type': Select(attrs={'class': 'form-control myform-focus', 'id':'product_type',}),
            'design': Select(attrs={'class': 'form-control myform-focus', 'id':'design',}),
        }
        labels = {
            'date': 'Fecha',
            'client': 'Cliente',
            'company': 'Empresa solicitante',
            'product': 'Nombre del producto',
            'printed_sample': 'Muestra impresa',
            'mechanical_plan': 'Plano mecanico',
            'technichal_specs': 'Especificaciones técnicas',
            'arts': 'Artes',
            'design': 'Diseño',
            'product_type': 'Tipo de producto',
        }
    documents = MultipleFileField(
        required=False,
        widget=MultipleFileInput(attrs={'multiple': True, 'class':'d-none', 'id': 'documents', 'accept': '.pdf,.doc,.docx,.xls,.xlsx,.xlsm,.jpeg,.jpg,.png'}),
        label='Documentos'
    )
    def save(self, commit=True):
        instance = super(SalesTestRequestForm, self).save(commit=False)
        if commit:
            instance.save()
            files = self.cleaned_data.get('documents', [])
            for file in files:
                validate_file_type(file)
                validate_file_size(file)

                original_filename = file.name
                extension = os.path.splitext(original_filename)[1]
                new_filename = f"sales_test_request_{instance.id}-{uuid.uuid4()}{extension}"
                file.name = new_filename

                doc = Document.objects.create(file=file, label=limit_file_name(original_filename))

                instance.documents.add(doc)
            instance.save()
        return instance

SalesStructureFormset = inlineformset_factory(SalesTestRequest, SalesStructure,
        fields = (
            'material_type',
            'weight',
            #'w_counts',
            'thickness',
            #'t_counts',
        ),
        formset=BaseInlineFormset,
        widgets = { 
            'material_type': Select(attrs={'class': 'form-control myform-focus text-center mat-type-fields', 'aria-label':'Tipo de material'}),
            'weight':  TextInput(attrs={'class': 'form-control myform-focus text-center justify-content-center', 'min':'0', 'aria-label':'Peso', 'placeholder':'0'}),
            #'w_counts': CheckboxInput(attrs={'style':'display: none;'}),
            'thickness': NumberInput(attrs={'class': 'form-control myform-focus text-center justify-content-center', 'min':'0', 'aria-label':'Espesor', 'placeholder':'0'}),
            #'t_counts': CheckboxInput(attrs={'style':'display: none;'}),
        }, 
        extra=0,
        can_delete=True
        )