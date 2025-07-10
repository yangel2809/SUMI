"""
Copyright (c) 2023 - present, Daniel Escalona
"""
import os, uuid
from cProfile import label
from django import forms
from django.forms import ModelForm, TextInput, Select
from django.core.validators import *
from django.forms.models import inlineformset_factory, modelform_factory, modelformset_factory#, BaseFormSet, formset_factory

from documents.validators import validate_file_type, validate_file_size
from documents.utils import limit_file_name
from documents.models import Document
from documents.forms import MultipleFileField, MultipleFileInput

from django.forms import *
from django.utils import timezone, dateformat
from .models import *
from .models import ArtAnalysis

# Formulario simple para los colores del formset
class ArtColorForm(forms.Form):
    color1 = CharField(label='Color / Estación 1', required=False, widget=TextInput(attrs={'class': 'form-control'}))
    color2 = CharField(label='Color / Estación 2', required=False, widget=TextInput(attrs={'class': 'form-control'}))
    color3 = CharField(label='Color / Estación 3', required=False, widget=TextInput(attrs={'class': 'form-control'}))

ArtColorFormSet = formset_factory(ArtColorForm, extra=0, can_delete=True)

class BaseInlineFormset(BaseInlineFormSet):
    def get_deletion_widget(self):
        return CheckboxInput(attrs={'class': 'form-check-input justify-content-center'})

class EntryElementForm(ModelForm):
    class Meta:
        model = EntryElement
        fields = '__all__'
        widgets ={
            'sales_test_request':   Select(attrs={'class':'form-control myform-focus text-center', 'id':'sales_test_request'}),
            'product_client':       Select(attrs={'class':'form-control myform-focus text-center', 'id':'product_client'}),
            'client':               Select(attrs={'class':'form-control myform-focus text-center', 'id':'client', 'required':''}),
            'date':                 DateInput(attrs={'class':'form-control myform-focus text-center date-widget', 'value':dateformat.format(timezone.now(), 'd/m/Y'), 'placeholder':'DD/MM/AAAA', 'id':'date'}),
            'ambiental_description':TextInput(attrs={'class':'form-control myform-focus d-none', 'placeholder':'Especifique', 'id':'ambiental_description'}),
            'ee_other_description': TextInput(attrs={'class':'form-control myform-focus d-none', 'placeholder':'Especifique', 'id':'ee_other_description' }),
            'lr_other_description': TextInput(attrs={'class':'form-control myform-focus d-none', 'placeholder':'Especifique', 'id':'lr_other_description' }),
            'sc_other_description': TextInput(attrs={'class':'form-control myform-focus d-none', 'placeholder':'Especifique', 'id':'sc_other_description' }),
            'ssmtc_description':    TextInput(attrs={'class':'form-control myform-focus d-none', 'placeholder':'Especifique', 'id':'ssmtc_description'    }),
            'nmp_description':      TextInput(attrs={'class':'form-control myform-focus d-none', 'placeholder':'Especifique', 'id':'nmp_description'      }),
            'norms_description':    TextInput(attrs={'class':'form-control myform-focus d-none', 'placeholder':'Indique',     'id':'norms_other_description'    }),
            'tech_inv_description': TextInput(attrs={'class':'form-control myform-focus d-none', 'placeholder':'Especifique', 'id':'tech_inv_description' }),
            'hr_description':       TextInput(attrs={'class':'form-control myform-focus d-none', 'placeholder':'Especifique', 'id':'hr_description'       }),
            'failure_description':  TextInput(attrs={'class':'form-control myform-focus', 'placeholder':'', 'id':'failure_specification'  }),
            'service_requirements': TextInput(attrs={'class':'form-control myform-focus', 'placeholder':'', 'id':'service_requirements'}),
            'involved_processes':   TextInput(attrs={'class':'form-control myform-focus', 'placeholder':'', 'id':'involved_processes'  }),
            'fail_consequence':     TextInput(attrs={'class':'form-control myform-focus', 'placeholder':'', 'id':'fail_consequence'    }),
            'test_client':          TextInput(attrs={'class':'form-control myform-focus', 'placeholder':'', 'id':'test_client'         }),
            'description':          TextInput(attrs={'class':'form-control myform-focus', 'placeholder':'', 'id':'description'         }),
            'elaborator':           TextInput(attrs={'class':'form-control myform-focus', 'placeholder':'', 'id':'elaborator'          }),
            'reviewer':             TextInput(attrs={'class':'form-control myform-focus', 'placeholder':'', 'id':'reviewer'            }),
            'product':              TextInput(attrs={'class':'form-control myform-focus', 'placeholder':'', 'id':'product'             }),
            'design':               TextInput(attrs={'class':'form-control myform-focus', 'placeholder':'', 'id':'design'              }),
            'op':                   TextInput(attrs={'class':'form-control myform-focus', 'placeholder':'', 'id':'op'                  }),
            'technical_assistance': CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'technical_assistance'}),
            'check_test_client':    CheckboxInput(attrs={'class':'d-none',                'id':'check_test_client'   }),
            'mechanichal_plans':    CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'mechanichal_plans'   }),
            'post_sale_service':    CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'post_sale_service'   }),
            'technical_specs':      CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'technical_specs'     }),
            'delivery_date':        CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'delivery_date'       }),
            'quantity':             CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'quantity'            }),
            'mounting':             CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'mounting'            }),
            'printing':             CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'printing'            }),
            'lamination':           CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'lamination'          }),
            'covering':             CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'covering'            }),
            'cutting':              CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'cutting'             }),
            'reaming':              CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'reaming'             }),
            'bagging':              CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'bagging'             }),
            'gazette':              CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'gazette'             }),
            'iso':                  CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'iso'                 }),
            'not_applicable':       CheckboxInput(attrs={'class':'form-check-input mt-2 na-check', 'childs':'lr-check', 'id':'not_applicable'}),
            'cpe':                  CheckboxInput(attrs={'class':'form-check-input mt-2 lr-check', 'id':'cpe'                 }),
            'barcode':              CheckboxInput(attrs={'class':'form-check-input mt-2 lr-check', 'id':'barcode'             }),
            'nutrituonal_table':    CheckboxInput(attrs={'class':'form-check-input mt-2 lr-check', 'id':'nutrituonal_table'   }),
            'net_content':          CheckboxInput(attrs={'class':'form-check-input mt-2 lr-check', 'id':'net_content'         }),
            'sanitary_reg':         CheckboxInput(attrs={'class':'form-check-input mt-2 lr-check', 'id':'sanitary_reg'        }),
            'lr_other':             CheckboxInput(attrs={'class':'form-check-input mt-2 lr-check description-selector', 'id':'lr_other'}),
            'ee_other':             CheckboxInput(attrs={'class':'form-check-input mt-2 description-selector', 'id':'ee_other'}),
            'sc_other':             CheckboxInput(attrs={'class':'form-check-input mt-2 description-selector', 'id':'sc_other'}),
            'ssmtc':                CheckboxInput(attrs={'class':'form-check-input mt-2 description-selector', 'id':'ssmtc'   }),
            'nmp':                  CheckboxInput(attrs={'class':'form-check-input mt-2 description-selector', 'id':'nmp'     }),
            'norms':                CheckboxInput(attrs={'class':'form-check-input mt-2 description-selector', 'id':'norms'   }),
            'norms_other':          CheckboxInput(attrs={'class':'form-check-input mt-2 description-selector', 'id':'norms_other'}),
            'tech_inv':             CheckboxInput(attrs={'class':'form-check-input mt-2 description-selector', 'id':'tech_inv'}),
            'failure':              CheckboxInput(attrs={'class':'form-check-input mt-2 description-selector', 'id':'failure' }),
            'hr':                   CheckboxInput(attrs={'class':'form-check-input mt-2 description-selector', 'id':'hr'      }),
            'similar_products':     CheckboxInput(attrs={'class':'form-check-input mt-2 description-selector', 'id':'similar_products'}),
            'ambiental':            CheckboxInput(attrs={'class':'form-check-input mt-2 description-selector', 'id':'ambiental'       }),
            'samples':              CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'samples'             }),
            'art':                  CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'art'                 }),
        }
        labels = {
            'check_test_client':'Usar Cliente de Prueba',
            'test_client':'Cliente de Prueba',
            'client':'Cliente',
            'date':'Fecha',
            'product':'Nombre Completo del Producto',
            'design':'Diseño',
            'samples':'Muestras del Cliente',
            'mechanichal_plans':'Planos Mecánicos del Cliente',
            'technical_specs':'Especificaciones Técnicas del Cliente',
            'art':'Arte del Cliente',
            'ee_other':'Otros',
            'ee_other_description':'Especifique',
            'product_performance':'Requisitos Funcionales del Producto',
            'service_requirements':'Requisitos del Servicio',
            'cpe':'C.P.E.',
            'barcode':'Código de Barras',
            'nutrituonal_table':'Tabla Nutricional',
            'net_content':'Contenido Neto',
            'sanitary_reg':'Registro Sanitario',
            'lr_other':'Otros',
            'lr_other_description':'Especifique',
            'not_applicable':'No Aplica',
            'delivery_date':'Fecha de entrega',
            'quantity':'Cantidad',
            'technical_assistance':'Asistencia Técnica',
            'post_sale_service':'Servicio Post-Venta',
            'sc_other':'Otro',
            'sc_other_description':'Especifique',
            'ssmtc':'¿Se requiere de alguna condición de almacenamiento, manipulación, transporte y entrega específica?',
            'ssmtc_description':'Especifique',
            'nmp':'¿Se Requiere Desarrollo de nuevas materias primas y/o proveedores?',
            'nmp_description':'Especifique',
            'norms':'Normas Nacionales y/o Internacionales',
            'iso':'Norma ISO 9001-2015',
            'gazette':'<abbr title="Normas sobre Prácticas para la Fabricación, Almacenamiento y Transporte de Envases, Empaques y/o Artículos Destinados a estar en Contacto con Alimentos">Gaceta Oficial Nº 38.678 del 8 de mayo de 2007</abbr>',
            'norms_other':'Otras',
            'mounting':'Montaje',
            'printing':'Impresión',
            'lamination':'Laminación',
            'covering':'Recubrimiento',
            'cutting':'Corte',
            'reaming':'Resmado',
            'bagging':'Bolseado',
            'tech_inv':'¿Se requiere inversión tecnológica para este desarrollo?',
            'tech_inv_description':'Especifique',
            'hr':'¿Se requiere de recursos humanos para el diseño y desarrollo?',
            'hr_description':'Especifique',
            'similar_products':'¿Se tienen registros de productos similares?',
            'op':'OP Nro.',
            'description':'Descripción',
            'product_client':'Cliente',

            'ambiental':'¿Se requiere de condiciones ambientales especiales para mantener el producto?',
            'ambiental_description':'Especifique',
            'failure':'¿Existen fallas potenciales?',
            'failure_description':'Especifique',
            'fail_consequence':'¿Cuales serían las Consecuencias de éstas fallas?',

            'sales_test_request':'Solicitud de Ventas',

            'observation':'Observaciones',
            'elaborator':'Realizado Por',
            'reviewer':'Revisado Por',
        }

    documents = MultipleFileField(
        required=False,
        widget=MultipleFileInput(attrs={'multiple': True, 'class':'d-none', 'id': 'documents', 'accept': '.pdf,.doc,.docx,.xls,.xlsx,.xlsm,.jpeg,.jpg,.png'}),
        label='Documentos'
    )
    def save(self, commit=True):
        instance = super(EntryElementForm, self).save(commit=False)
        if commit:
            instance.save()
            files = self.cleaned_data.get('documents', [])
            for file in files:
                validate_file_type(file)
                validate_file_size(file)

                original_filename = file.name
                extension = os.path.splitext(original_filename)[1]
                new_filename = f"entry_element_{instance.id}-{uuid.uuid4()}{extension}"
                file.name = new_filename

                doc = Document.objects.create(file=file, label=limit_file_name(original_filename))

                instance.documents.add(doc)
            instance.save()
        return instance

class ExitElementForm(ModelForm):
    class Meta:
        model = ExitElement
        fields = '__all__'
        widgets = {
            'shelf_life_date': DateInput(attrs={'class':'form-control myform-focus text-center date-widget', 'autocomplete':'off', 'placeholder':'DD/MM/AAAA', 'id':'shelf_life_date'}),
            'technical_specs' :CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'technical_specs'}),
            'delivery_time' :CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'delivery_time'}),
            'replicavility' :CheckboxInput(attrs={'class':'form-check-input mt-2 description-selector', 'id':'replicavility'}),
            'replicavility_description':TextInput(attrs={'class':'form-control myform-focus d-none', 'placeholder':'Indique', 'id':'replicavility_description'}),
            'dimensions' :CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'dimensions'}),
            'guarantee' :CheckboxInput(attrs={'class':'form-check-input mt-2 description-selector', 'id':'guarantee'}),
            'ae_other' :CheckboxInput(attrs={'class':'form-check-input mt-2 description-selector', 'id':'ae_other'}),
            'failure' :CheckboxInput(attrs={'class':'form-check-input mt-2 description-selector', 'id':'failure'}),
            'ae_other_description':TextInput(attrs={'class':'form-control myform-focus d-none', 'placeholder':'Indique', 'id':'ae_other_description'}),
            'guarantee_description':TextInput(attrs={'class':'form-control myform-focus d-none', 'placeholder':'Indique', 'id':'guarantee_description'}),
            'failure_description':TextInput(attrs={'class':'form-control myform-focus', 'placeholder':'', 'id':'failure_description_l'}), #these failures go together
            'failure_consequence':TextInput(attrs={'class':'form-control myform-focus', 'placeholder':'', 'id':'failure_consequence'}), #these failures go together
            'functionallity_and_performance':Textarea(attrs={'class':'form-control myform-focus', 'placeholder':'', 'id':'functionallity_and_performance'}),
            'technical_assistance':Select(attrs={'class':'form-control myform-focus select-2', 'placeholder':'Seleccione...', 'id':'technical_assistance'}),
            'after_sales_service':Select(attrs={'class':'form-control myform-focus select-2', 'placeholder':'Seleccione...', 'id':'after_sales_service'}),
            'lab_analysis':Select(attrs={'class':'form-control myform-focus select-2', 'placeholder':'Seleccione...', 'id':'lab_analysis'}),
            'machinability':Select(attrs={'class':'form-control myform-focus select-2', 'placeholder':'Seleccione...', 'id':'machinability'}),
            'shelf_life':Select(attrs={'class':'form-control myform-focus select-2', 'placeholder':'Seleccione...', 'id':'shelf_life'}),
            'handling':Select(attrs={'class':'form-control myform-focus select-2', 'placeholder':'Seleccione...', 'id':'handling'}),
            'delivery':Select(attrs={'class':'form-control myform-focus select-2', 'placeholder':'Seleccione...', 'id':'delivery'}),
            'storage':Select(attrs={'class':'form-control myform-focus select-2', 'placeholder':'Seleccione...', 'id':'storage'}),
            'elaborator':TextInput(attrs={'class':'form-control myform-focus', 'placeholder':'', 'id':'elaborator'}),
            'reviewer':TextInput(attrs={'class':'form-control myform-focus', 'placeholder':'', 'id':'reviewer'}),
        }

        labels = {
            'dimensions':'Dimensiones',
            'technical_specs':'Especificaciones Técnicas',
            'delivery_time':'Tiempo de Entrega',
            'ae_other':'Otro',
            'ae_other_description':'Especifique',
            'functionallity_and_performance':'Funcionalidad y desempeño del producto y/o servicio',
            'replicavility':'¿Es reproducible el producto o servicio para garantizar su provisión?',

            'lab_analysis':'Analisis de Laboratorio',
            'machinability':'Mecanabilidad',
            'handling':'Manejo',
            'shelf_life':'Vida Util',
            'delivery':'Entrega',
            'storage':'Almacenamiento',
            'technical_assistance':'Asistencia Técnica',
            'after_sales_service':'Servicio Post-Venta',
            
            'failure':'¿Existieron fallas sobre el diseño y desarrollo?',
            'failure_description':'Especifique',
            'failure_consequence':'¿Cuales fueron las consecuencias de éstas fallas?',
            'guarantee':'¿Se garantiza que los productos y servicios cumplan con su propósito y su provisión sea segura y correcta?',
            'guarantee_description':'Especifique',
            'elaborator':'Realizado Por',
            'reviewer':'Revisado Por',
            'observation':'Observaciones',
        }
    documents = MultipleFileField(
        required=False,
        widget=MultipleFileInput(attrs={'multiple': True, 'class':'d-none', 'id': 'documents', 'accept': '.pdf,.doc,.docx,.xls,.xlsx,.xlsm,.jpeg,.jpg,.png'}),
        label='Documentos'
    )
    def save(self, commit=True):
        instance = super(ExitElementForm, self).save(commit=False)
        if commit:
            instance.save()
            files = self.cleaned_data.get('documents', [])
            for file in files:
                validate_file_type(file)
                validate_file_size(file)

                original_filename = file.name
                extension = os.path.splitext(original_filename)[1]
                new_filename = f"exit_element_{instance.id}-{uuid.uuid4()}{extension}"
                file.name = new_filename

                doc = Document.objects.create(file=file, label=limit_file_name(original_filename))

                instance.documents.add(doc)
            instance.save()
        return instance

class TestRequestForm(ModelForm):
    class Meta:
        model = TestRequest
        fields = (
            #'format', 
            'number', 
            'company', 
            'origin', 
            'check_test_client', 
            'test_client', 
            'client', 
            #art
            'art_number', 
            'art_date', 
            'product', 
            'design', 
            #TestStructure
            'lamination_process', 
            'print_selector',
            'printer', 
            'surface_selector',
            #'surface_over',
            'reverse_selector',
            #'reverse_over',
            'sindex',
            'sustrate_width',
            'print_width',
            'print_width_unit',
            'colors',
            #Lamination
            #'lamination_selector',
            #dimendiosns
            'dist_boder_cell_material',
            'repetition',
            'repetition_unit',
            'width_photo',
            'lenght_photo',
            'unit_photo',
            #bobbin
            'check_bobbin',
            'width_bobbin',
            'width_bobbin_unit',
            'develop',
            'develop_unit',
            'exterior_dia_bobbin',
            'exterior_dia_bobbin_unit',
            'core_dia_bobbin',
            'winding',
            'photocell_side',
            'winding_description',
            #ream
            'check_ream',
            'width_ream',
            'lenght_ream',
            'weight_ream',
            #production
            'quantity', 
            'unit', 
            'tolerance',
            'packaging',
            'tie_color',
            'observation', 
            #production
            'applicant', 
            'elaborator', 
            'reviewer',
            #checks 
            'pre_print', 
            'colorimetry', 
            'plan_crx', 
            'plan_mcl', 
            'logistics', 
            'quality'
            )
            
        widgets ={
            #'format': Select(attrs={'class': 'form-control myform-focus text-center', 'aria-label':'Formato', 'id':'format'}),
            'number': TextInput(attrs={'class':'form-control align-items-center myform-focus text-center', 'style':'text-transform: uppercase !important;', 'pattern':'^[0-9]{2}[-][0-9]{6}$', 'Title':'Sólo se admite el formato 00-000000', 'placeholder':'00-000000', 'id':'number'}),
            'company': Select(attrs={'class': 'form-control myform-focus text-center', 'aria-label':'Empresa', 'id':'company'}),
            'origin': Select(attrs={'class': 'form-control myform-focus text-center', 'aria-label':'Origen', 'id':'origin'}),
            'check_test_client': CheckboxInput(attrs={'aria-label':'Cliente de Prueba', 'id':'check_test_client', 'style':'display: none'}),
            'test_client':TextInput(attrs={'class':'form-control align-items-center myform-focus text-center', 'placeholder':'Nombre...', 'id':'test_client'}),
            'client': Select(attrs={'class': 'form-control myform-focus text-center', 'aria-label':'Cliente', 'required':'','id':'client'}),
            #art
            'art_number': TextInput(attrs={'class':'form-control align-items-center myform-focus text-center', 'style':'text-transform: uppercase !important;', 'placeholder':'00000000', 'id':'art_number'}),
            'art_date': DateInput(attrs={'class':'form-control align-items-center myform-focus text-center', 'autocomplete':'off', 'placeholder':'DD/MM/AAAA', 'id':'art_date'}),
            'product': TextInput(attrs={'class':'form-control align-items-center myform-focus', 'placeholder':'Nombre completo del Producto', 'id':'product' }),
            'design': TextInput(attrs={'class':'form-control align-items-center myform-focus', 'aria-label':'Diseño', 'placeholder':'', 'id':'design' }),
            'print_selector': CheckboxInput(attrs={'class':'form-check-input justify-content-center', 'aria-label':'En superficie', 'id':'print_selector'}),
            'printer': Select(attrs={'class': 'form-control myform-focus text-center', 'aria-label':'Impresora', 'id':'printer'}),
            'surface_selector': CheckboxInput(attrs={'class':'form-check-input justify-content-center', 'type':'radio', 'aria-label':'En superficie', 'id':'surface_selector'}),
            'reverse_selector': CheckboxInput(attrs={'class':'form-check-input justify-content-center', 'type':'radio', 'aria-label':'En reverso', 'id':'reverse_selector'}),
            'sindex':HiddenInput(attrs={'id':'sindex'}),
            'sustrate_width': NumberInput(attrs={'class':'form-control align-items-center myform-focus', 'aria-label':'Sustrato', 'placeholder':'0', 'id':'sustrate_width' }),
            'print_width': TextInput(attrs={'class':'form-control align-items-center myform-focus flat-right', 'placeholder':'0', 'id':'print_width', 'style':'padding-right: 1.3em !important'}),
            'print_width_unit': Select(attrs={'class':'text-center form-control myform-focus text-center flat-left', 'id':'print_width_unit' }),
            'colors': TextInput(attrs={'class':'form-control align-items-center myform-focus', 'placeholder':'Colores', 'id':'colors' }),
            'dist_boder_cell_material': TextInput(attrs={'class':'form-control align-items-center myform-focus', 'placeholder':'0', 'id':'dist_boder_cell_material'}),
            'repetition': TextInput(attrs={'class':'form-control align-items-center myform-focus flat-right', 'style':'padding-right: 1.4em !important;', 'placeholder':'0', 'id':'repetition', 'style':'padding-right: 1.3em !important'}),
            'repetition_unit': Select(attrs={'class':'text-center form-control myform-focus text-center flat-left', 'id':'repetition_unit' }),
            'width_photo': NumberInput(attrs={'class': 'form-control myform-focus text-center justify-content-center', 'min':'0', 'placeholder':'0', 'id':'width_photo'}),
            'lenght_photo': NumberInput(attrs={'class': 'form-control align-items-center myform-focus justify-content-center flat-right', 'min':'0', 'placeholder':'0', 'id':'lenght_photo'}),
            'unit_photo': Select(attrs={'class':'text-center form-control align-items-center myform-focus flat-left', 'id':'unit_photo'}),
            #bobbin
            'check_bobbin': CheckboxInput(attrs={'class': 'form-check-input justify-content-center', 'aria-label':'Bobina', 'id':'check_bobbin'}),
            'width_bobbin': TextInput(attrs={'class':'form-control align-items-center myform-focus flat-right', 'style':'padding-right: 1.4em !important;', 'placeholder':'0', 'id':'width_bobbin', 'style':'padding-right: 1.3em !important'}),
            'width_bobbin_unit': Select(attrs={'class':'text-center form-control align-items-center myform-focus flat-left', 'id':'width_bobbin_unit'}),
            'develop': TextInput(attrs={'class': 'form-control myform-focus flat-right', 'style':'padding-right: 1.4em !important;', 'placeholder':'', 'id':'develop', 'style':'padding-right: 1.3em !important'}),
            'develop_unit': Select(attrs={'class': 'form-control myform-focus flat-left', 'placeholder':'', 'id':'develop_unit'}),
            'exterior_dia_bobbin': TextInput(attrs={'class':'form-control align-items-center myform-focus flat-right', 'style':'padding-right: 1.4em !important;', 'placeholder':'0', 'id':'exterior_dia_bobbin'}),
            'exterior_dia_bobbin_unit': Select(attrs={'class':'text-center form-control align-items-center myform-focus flat-left', 'id':'exterior_dia_bobbin_unit'}),
            'core_dia_bobbin': Select(attrs={'class': 'form-control myform-focus text-center', 'aria-label':'Diámetro de corte bobina', 'id':'core_dia_bobbin'}),
            'winding': Select(attrs={'class': 'form-control myform-focus text-center', 'placeholder':'Sentido de embobinado', 'id':'winding' }),
            'photocell_side': Select(attrs={'class': 'form-control myform-focus text-center', 'placeholder':'Lado de fotocelda', 'id':'photocell_side' }),
            'winding_description': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'winding_description'}),
            #ream
            'check_ream': CheckboxInput(attrs={'class': 'form-check-input justify-content-center', 'aria-label':'Resma', 'id':'check_ream'}),
            'width_ream': TextInput(attrs={'class':'form-control align-items-center myform-focus', 'placeholder':'0', 'id':'width_ream'}),
            'lenght_ream': TextInput(attrs={'class':'form-control align-items-center myform-focus', 'placeholder':'0', 'id':'lenght_ream'}),
            'weight_ream': TextInput(attrs={'class':'form-control align-items-center myform-focus', 'placeholder':'0', 'id':'weight_ream'}),
            'quantity': NumberInput(attrs={'class': 'form-control myform-focus text-center justify-content-center', 'min':'0', 'aria-label':'Cantidad', 'placeholder':'0', 'id':'quantity'}),
            'unit': Select(attrs={'class': 'form-control myform-focus text-center', 'aria-label':'Unidad', 'id':'unit'}),
            'tolerance': NumberInput(attrs={'class': 'form-control myform-focus text-center justify-content-center', 'min':'0', 'aria-label':'Tolerancia', 'placeholder':'0', 'id':'tolerance'}),
            'packaging': TextInput(attrs={'class':'form-control align-items-center myform-focus', 'placeholder':'', 'id':'packaging'}),
            'tie_color': TextInput(attrs={'class':'form-control align-items-center myform-focus', 'placeholder':'', 'id':'tie_color'}),
            #'observation':
            #evaluators
            'applicant': TextInput(attrs={'class':'form-control align-items-center myform-focus', 'aria-label':'', 'placeholder':'Nombre/Departamento', 'id':'applicant'}),
            'elaborator': TextInput(attrs={'class':'form-control align-items-center myform-focus', 'aria-label':'', 'placeholder':'Nombre, Apellido y/o Cargo', 'id':'elaborator'}),
            'reviewer': TextInput(attrs={'class':'form-control align-items-center myform-focus', 'aria-label':'', 'placeholder':'Nombre, Apellido y/o Cargo', 'id':'reviewer'}),
            #checks
            'pre_print': CheckboxInput(attrs={'class': 'form-check-input justify-content-center', 'aria-label':'Seleccionar Pre-Prensa', 'id':'pre_print'}),
            'colorimetry': CheckboxInput(attrs={'class': 'form-check-input justify-content-center', 'aria-label':'Seleccionar Colorimetría', 'id':'colorimetry'}),
            'plan_crx': CheckboxInput(attrs={'class': 'form-check-input justify-content-center', 'aria-label':'Seleccionar Prod. Curex', 'id':'plan_crx'}),
            'plan_mcl': CheckboxInput(attrs={'class': 'form-check-input justify-content-center', 'aria-label':'Seleccionar Prod. Morrocel', 'id':'plan_mcl'}),
            'logistics': CheckboxInput(attrs={'class': 'form-check-input justify-content-center', 'aria-label':'Seleccionar Planificación y Logística', 'id':'logistics'}),
            'quality': CheckboxInput(attrs={'class': 'form-check-input justify-content-center', 'aria-label':'Seleccionar Calidad', 'id':'quality'}),
        }   
   
class ArtRequestForm(ModelForm):
    class Meta:
        model = ArtRequest
        fields = [
            "client", "applicant", "company", "date", "product_name",
            "work_type", "supplied_material", "other_supplied_material", "printer",
            "print_substrate", "print_type", "product_structure", "printing_colors",
            "company_logo", "logo_type", "plant_reel_width", "client_reel_width",
            "packaging_unit_width", "packaging_unit_length", "tolerance",
            "has_photocell", "photocell_width", "photocell_length",
            "photocell_distance", "photocell_colors", "observations",
            "elaborator", "reviewer"
        ]
        widgets = {
            'date': DateInput(attrs={'class': 'form-control', 'type': 'text', 'autocomplete': 'off'}),
            'client': Select(attrs={'class': 'form-control'}),
            'applicant': TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del solicitante'}),
            'company': Select(attrs={'class': 'form-control', 'placeholder': 'Empresa que solicita'}),
            'product_name': TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'}),
            'work_type': TextInput(attrs={'class': 'form-control', 'placeholder': 'Tipo de trabajo'}),
            'supplied_material': TextInput(attrs={'class': 'form-control', 'placeholder': 'Material de referencia'}),
            'other_supplied_material': TextInput(attrs={'class': 'form-control', 'placeholder': 'Otro material de referencia'}),
            'printer': Select(attrs={'class': 'form-control'}),
            'print_substrate': TextInput(attrs={'class': 'form-control', 'placeholder': 'Sustrato'}),
            'print_type': TextInput(attrs={'class': 'form-control', 'placeholder': 'Superficie o Reverso'}),
            'product_structure': Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Ej: TINTA, ALUMINIO, RESINA'}),
            'printing_colors': Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Ej: {\"1\": \"Amarillo\", \"2\": \"Cyan\"}'}),
            'company_logo': TextInput(attrs={'class': 'form-control', 'placeholder': 'Logo a utilizar'}),
            'logo_type': TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: No Abreviado'}),
            'plant_reel_width': NumberInput(attrs={'class': 'form-control', 'placeholder': 'mm'}),
            'client_reel_width': NumberInput(attrs={'class': 'form-control', 'placeholder': 'mm'}),
            'packaging_unit_width': NumberInput(attrs={'class': 'form-control', 'placeholder': 'mm'}),
            'packaging_unit_length': NumberInput(attrs={'class': 'form-control', 'placeholder': 'mm'}),
            'tolerance': NumberInput(attrs={'class': 'form-control', 'placeholder': 'mm'}),
            'has_photocell': CheckboxInput(attrs={'class': 'form-check-input'}),
            'photocell_width': NumberInput(attrs={'class': 'form-control', 'placeholder': 'mm'}),
            'photocell_length': NumberInput(attrs={'class': 'form-control', 'placeholder': 'mm'}),
            'photocell_distance': NumberInput(attrs={'class': 'form-control', 'placeholder': 'mm'}),
            'photocell_colors': TextInput(attrs={'class': 'form-control', 'placeholder': 'Colores'}),
            'observations': Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'elaborator': TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre y Apellido'}),
            'reviewer': TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre y Apellido'}),
        }
   
TestStructureFormset = inlineformset_factory(TestRequest, TestStructure,
        fields = (
            #'test_material_check',
            #'test_material',
            'material_type',
            'provider',
            'weight',
            'w_counts',
            'code',
            'thickness',
            't_counts',
            'description',
            'from_production'
        ),
        formset=BaseInlineFormset,
        widgets = { 
            #'test_material_check': CheckboxInput(attrs={'class': 'form-check-input justify-content-center', 'aria-label':'Usar Material de prueba'}),
            #'test_material': TextInput(attrs={'class': 'form-control myform-focus text-center', 'autocomplete':'off', 'aria-label':'Material de prueba', 'placeholder':'Material...'}),
            'code': TextInput(attrs={'class': 'form-control myform-focus text-center justify-content-center text-uppercase', 'autocomplete':'off', 'aria-label':'Material de prueba', 'placeholder':'Código...'}),
            'material_type': Select(attrs={'class': 'form-control myform-focus text-center', 'aria-label':'Tipo de material'}),
            'provider': Select(attrs={'class': 'form-control myform-focus text-center', 'aria-label':'Proveedor'}),
            'weight':  TextInput(attrs={'class': 'form-control myform-focus text-center justify-content-center', 'min':'0', 'aria-label':'Peso', 'placeholder':'0'}),
            'w_counts':CheckboxInput(attrs={'style':'display: none;'}),
            'thickness': NumberInput(attrs={'class': 'form-control myform-focus text-center justify-content-center', 'min':'0', 'aria-label':'Espesor', 'placeholder':'0'}),
            't_counts':CheckboxInput(attrs={'style':'display: none;'}),
            'description': TextInput(attrs={'class': 'form-control myform-focus text-center justify-content-center', 'autocomplete':'off', 'aria-label':'Descripción', 'placeholder':'Descripción', 'style':'padding-right: 1.3em !important'}),
            'from_production':  TextInput(attrs={'style':'display:none;'}),
        }, 
        extra=0,
        can_delete=True
        )
ArtStructureFormset = inlineformset_factory(ArtRequest, ArtStructure,
        fields = (
            #'test_material_check',
            #'test_material',
            'material_type',
            'provider',
            'weight',
            'w_counts',
            'code',
            'thickness',
            't_counts',
            'description',
            'from_production'
        ),
        formset=BaseInlineFormset,
        widgets = { 
            #'test_material_check': CheckboxInput(attrs={'class': 'form-check-input justify-content-center', 'aria-label':'Usar Material de prueba'}),
            #'test_material': TextInput(attrs={'class': 'form-control myform-focus text-center justify-content-center', 'autocomplete':'off', 'aria-label':'Material de prueba', 'placeholder':'Material...'}),
            'code': TextInput(attrs={'class': 'form-control myform-focus text-center justify-content-center text-uppercase', 'autocomplete':'off', 'aria-label':'Material de prueba', 'placeholder':'Código...'}),
            'material_type': Select(attrs={'class': 'form-control myform-focus text-center', 'aria-label':'Tipo de material'}),
            'provider': Select(attrs={'class': 'form-control myform-focus text-center', 'aria-label':'Proveedor'}),
            'weight':  TextInput(attrs={'class': 'form-control myform-focus text-center justify-content-center', 'min':'0', 'aria-label':'Peso', 'placeholder':'0'}),
            'w_counts':CheckboxInput(attrs={'style':'display: none;'}),
            'thickness': NumberInput(attrs={'class': 'form-control myform-focus text-center justify-content-center', 'min':'0', 'aria-label':'Espesor', 'placeholder':'0'}),
            't_counts':CheckboxInput(attrs={'style':'display: none;'}),
            'description': TextInput(attrs={'class': 'form-control myform-focus text-center justify-content-center', 'autocomplete':'off', 'aria-label':'Descripción', 'placeholder':'Descripción', 'style':'padding-right: 1.3em !important'}),
            'from_production':  TextInput(attrs={'style':'display:none;'}),
        }, 
        extra=0,
        can_delete=True
        )
'''
LaminationFormset = inlineformset_factory(TestRequest, Lamination,
        fields = (
            'machine',
            'detail'
        ),
        formset=BaseInlineFormset,
        widgets = {         
            'machine': Select(attrs={'class': 'form-control myform-focus text-center', 'aria-label':'Máquina'}),
            'detail': TextInput(attrs={'class': 'form-control myform-focus text-center justify-content-center', 'autocomplete':'off', 'aria-label':'Material de prueba', 'placeholder':'Especificación'}),
        }, 
        extra=0,
        can_delete=True
        )
        '''      
class PrinterForm(ModelForm):
    class Meta:
        model = Printer
        fields = (
            'name',
            )
        widgets ={
            'name': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'Nombre'})
        }
class LaminatorForm(ModelForm):
    class Meta:
        model = Laminator
        fields = (
            'name',
            )
        widgets ={
            'name': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'Nombre'})
        }
class CutterForm(ModelForm):
    class Meta:
        model = Cutter
        fields = (
            'name',
            )
        widgets ={
            'name': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'Nombre'})
        }
class RewinderForm(ModelForm):
    class Meta:
        model = Rewinder
        fields = (
            'name',
            )
        widgets ={
            'name': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'Nombre'})
        }
class ProductionOperatorForm(ModelForm):
    class Meta:
        model = ProductionOperator
        fields = (
            'name',
            'active',
            )
        widgets ={
            'name': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'Nombre'}),
            'active': CheckboxInput(attrs={'class': 'form-check-input mt-0', 'id':'active'})
        }
class QualityAnalystForm(ModelForm):
    class Meta:
        model = QualityAnalyst
        fields = (
            'name',
            'active',
            )
        widgets ={
            'name': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'Nombre'}),
            'active': CheckboxInput(attrs={'class': 'form-check-input mt-0', 'id':'active'})
        }

class PrinterBootForm(ModelForm):
    quality_analist = ModelChoiceField(
        queryset=QualityAnalyst.objects.filter(active=True).order_by('name'),
        widget=Select(attrs={'class': 'form-control myform-focus', 'id':'quality_analist'})
    )
    production_operator = ModelChoiceField(
        queryset=ProductionOperator.objects.filter(active=True).order_by('name'),
        widget=Select(attrs={'class': 'form-control myform-focus', 'id':'production_operator'})
    )    
    class Meta:
        model = PrinterBoot
        fields = (
            'printer',
            'date_time',
            'turn',
            'machine_speed',
            'check_crown_treatment',
            'crown_treatment_side',
            'surface_tension',
            'sta_01',
            'sta_02',
            'sta_03',
            'sta_04',
            'sta_05',
            'sta_06',
            'sta_07',
            'sta_08',
            'sta_09',
            'sta_10',
            'standar',
            'art',
            'pre_print',
            'develop_folder',
            'register',
            'text',
            'dimensions',
            'cutting_guide',
            'photocell',
            'barcode',
            'develop',
            'develop_unit',
            'develop_result',
            'cut_width_result',
            'design',
            'machine_winding',
            'photocell_side',
            'winding_description',
            'r_left',
            'r_right',
            'r_center',
            'color_standar',
            'anchorage',
            'rub',
            'ther_resistance',
            'anchorage_resistance',
            'cut_diagram',
            'observation',
            'quality_analist',
            'production_operator',
        )
        widgets = {
            'printer': Select(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'printer'}),
            'date_time': DateTimeInput(attrs={'class': 'form-control myform-focus', 'autocomplete':'off', 'placeholder':'DD/MM/AAAA hh:mm:ss', 'id':'date_time'}),
            'turn': Select(attrs={'class': 'form-control myform-focus text-center', 'placeholder':'', 'id':'turn'}),
            'machine_speed': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'machine_speed'}),
            'check_crown_treatment': CheckboxInput(attrs={'class':'form-check-input justify-content-center', 'id':'check_crown_treatment'}),
            'crown_treatment_side': Select(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'crown_treatment_side'}),
            'surface_tension': Select(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'surface_tension'}),
            'sta_01': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'sta_01'}),
            'sta_02': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'sta_02'}),
            'sta_03': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'sta_03'}),
            'sta_04': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'sta_04'}),
            'sta_05': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'sta_05'}),
            'sta_06': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'sta_06'}),
            'sta_07': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'sta_07'}),
            'sta_08': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'sta_08'}),
            'sta_09': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'sta_09'}),
            'sta_10': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'sta_10'}),
            'standar': Select(attrs={'class':'form-control myform-focus justify-content-center', 'id':'standar'}),
            'art': Select(attrs={'class':'form-control myform-focus justify-content-center', 'id':'art'}),
            'pre_print': Select(attrs={'class':'form-control myform-focus justify-content-center', 'id':'pre_print'}),
            'develop_folder': Select(attrs={'class':'form-control myform-focus justify-content-center', 'id':'develop_folder'}),
            'register': Select(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'register'}),
            'text': Select(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'text'}),
            'dimensions': Select(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'dimensions'}),
            'cutting_guide': Select(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'cutting_guide'}),
            'photocell': Select(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'photocell'}),
            'barcode': Select(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'barcode'}),
            'develop': TextInput(attrs={'class': 'form-control myform-focus flat-right', 'style':'padding-right: 1.4em !important;', 'placeholder':'', 'readonly':'', 'id':'develop', 'style':'padding-right: 1.3em !important'}),
            'develop_unit': Select(attrs={'class': 'form-control myform-focus flat-left', 'placeholder':'', 'id':'develop_unit'}),
            'develop_result': NumberInput(attrs={'class': 'form-control myform-focus text-center', 'min':'0', 'placeholder':'0', 'id':'develop_result'}),
            'cut_width_result': NumberInput(attrs={'class': 'form-control myform-focus text-center', 'min':'0', 'placeholder':'0', 'id':'cut_width_result'}),
            'design': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'design'}),
            'machine_winding': Select(attrs={'class': 'form-control myform-focus text-center', 'placeholder':'', 'id':'machine_winding'}),
            'photocell_side': Select(attrs={'class': 'form-control myform-focus text-center', 'placeholder':'Lado de fotocelda', 'id':'photocell_side' }),
            'winding_description': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'winding_description'}),
            'r_left': NumberInput(attrs={'class': 'form-control myform-focus text-center', 'min':'0', 'placeholder':'0', 'id':'r_left'}),
            'r_right': NumberInput(attrs={'class': 'form-control myform-focus text-center', 'min':'0', 'placeholder':'0', 'id':'r_right'}),
            'r_center': NumberInput(attrs={'class': 'form-control myform-focus text-center', 'min':'0', 'placeholder':'0', 'id':'r_center'}),
            'color_standar': Select(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'color_standar'}),
            'anchorage': Select(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'anchorage'}),
            'rub': Select(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'rub'}),
            'ther_resistance': Select(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'ther_resistance'}),
            'anchorage_resistance': Select(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'anchorage_resistance'}),
            'cut_diagram': CheckboxInput(attrs={'class':'form-check-input justify-content-center', 'id':'cut_diagram'}),
            #observation
            
        }
    
class LaminatorBootForm(ModelForm):
    quality_analist = ModelChoiceField(
        queryset=QualityAnalyst.objects.filter(active=True).order_by('name'),
        widget=Select(attrs={'class': 'form-control myform-focus', 'id':'quality_analist'})
    )
    production_operator = ModelChoiceField(
        queryset=ProductionOperator.objects.filter(active=True).order_by('name'),
        widget=Select(attrs={'class': 'form-control myform-focus', 'id':'production_operator'})
    )    
    class Meta:
        model = LaminatorBoot
        fields = (            
            #'production_order',
            #'gp_code',
            #'format',
            'laminator',
            'date_time',
            'turn',
            'machine_speed',
            'crown_treatment_pri',
            'crown_treatment_sec',
            'step',
            'st_1',
            'st_2',
            'st_3',
            'st_4',
            'adhesive',
            'batch',
            'formula',
            #Essay Formset
            'time',
            'temp',
            'observation',
            'quality_analist',
            'production_operator',
        )
        widgets = {
            #'production_order': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'production_order'}),
            #'gp_code': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'gp_code'}),
            #'format': Select(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'format'}),
            'laminator': Select(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'laminator'}),
            'date_time': DateTimeInput(attrs={'class': 'form-control myform-focus', 'autocomplete':'off', 'placeholder':'', 'id':'date_time'}),
            'turn': Select(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'turn'}),
            'machine_speed': NumberInput(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'machine_speed'}),
            'crown_treatment_pri': CheckboxInput(attrs={'class':'form-check-input justify-content-center', 'id':'crown_treatment_pri'}),
            'crown_treatment_sec': CheckboxInput(attrs={'class':'form-check-input justify-content-center', 'id':'crown_treatment_sec'}),
            'step': Select(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'step'}),
            'st_1': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'st_1'}),
            'st_2': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'st_2'}),
            'st_3': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'st_3'}),
            'st_4': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'st_4'}),
            'adhesive': Select(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'adhesive'}),
            'batch': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'batch'}),
            'formula': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'formula'}),
            #Essay Formset
            'time': NumberInput(attrs={'class': 'form-control myform-focus text-center', 'min':'0', 'placeholder':'0', 'id':'time'}),
            'temp': NumberInput(attrs={'class': 'form-control myform-focus text-center', 'min':'0', 'placeholder':'0', 'id':'temp'}),
            #observation
        }
LaminationEssayFormset = inlineformset_factory(LaminatorBoot, LaminationEssay,
        fields = (
            'essay',
            'result_t',
            'result_a',
            'check_a',
            'result_b',
            'check_b',
            'result_c',
            'check_c',
        ),
        formset=BaseInlineFormset,
        widgets = { 
            'essay': Select(attrs={'class': 'form-control myform-focus text-center'}),
            'result_t': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'style':'padding-right: 1.3em !important'}),
            'result_a': NumberInput(attrs={'class': 'form-control myform-focus text-center', 'min':'0', 'placeholder':'A'}),
            'result_c': NumberInput(attrs={'class': 'form-control myform-focus text-center', 'min':'0', 'placeholder':'C'}),
            'result_b': NumberInput(attrs={'class': 'form-control myform-focus text-center', 'min':'0', 'placeholder':'B'}),
        }, 
        extra=2,
        )
class CutterBootForm(ModelForm):
    quality_analist = ModelChoiceField(
        queryset=QualityAnalyst.objects.filter(active=True).order_by('name'),
        widget=Select(attrs={'class': 'form-control myform-focus', 'id':'quality_analist'})
    )
    production_operator = ModelChoiceField(
        queryset=ProductionOperator.objects.filter(active=True).order_by('name'),
        widget=Select(attrs={'class': 'form-control myform-focus', 'id':'production_operator'})
    )    
    class Meta:
        model = CutterBoot
        fields = (
            'machine',
            'rewinder',
            'date_time',
            'turn',
            'machine_speed',
            'as_treatment',
            'r_a',
            'r_b',
            'r_c',
            'w_a',
            'w_b',
            'w_c',
            'apearence',
            'apearence_observation',
            'core',
            'exterior_dia',
            'print_spec',
            'print',
            'winding_position',
            'dist_boder_material',
            'joint_color',
            'joint_color_observation',
            'static_spec',
            'static',
            'packaging_spec',
            'packaging',
            'pallet_spec',
            'pallet',
            'n_litters_spec',
            'n_litters',
            'identification',
            'ex_tag',
            'in_tag',
            'observation',
            'quality_analist',
            'production_operator',
        )

        widgets = {
            'machine': Select(attrs={'class': 'form-control myform-focus text-center', 'id':'machine'}),
            'rewinder': Select(attrs={'class': 'form-control myform-focus text-center', 'id':'rewinder'}),
            'date_time': DateTimeInput(attrs={'class': 'form-control myform-focus', 'autocomplete':'off', 'placeholder':'DD/MM/AAAA hh:mm:ss', 'id':'date_time'}),
            'turn': Select(attrs={'class': 'form-control myform-focus text-center', 'id':'turn'}),
            'machine_speed': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'machine_speed'}),
            'as_treatment': CheckboxInput(attrs={'class':'form-check-input justify-content-center', 'id':'as_treatment'}),
            'r_a': NumberInput(attrs={'class': 'form-control myform-focus text-center', 'min':'0', 'placeholder':'A: Izquierda', 'id':'r_a'}),
            'r_b': NumberInput(attrs={'class': 'form-control myform-focus text-center', 'min':'0', 'placeholder':'B: Derecha', 'id':'r_b'}),
            'r_c': NumberInput(attrs={'class': 'form-control myform-focus text-center', 'min':'0', 'placeholder':'C: Centro', 'id':'r_c'}),
            'w_a': NumberInput(attrs={'class': 'form-control myform-focus text-center', 'min':'0', 'placeholder':'A: Izquierda', 'id':'w_a'}),
            'w_b': NumberInput(attrs={'class': 'form-control myform-focus text-center', 'min':'0', 'placeholder':'B: Derecha', 'id':'w_b'}),
            'w_c': NumberInput(attrs={'class': 'form-control myform-focus text-center', 'min':'0', 'placeholder':'C: Centro', 'id':'w_c'}),
            'apearence': Select(attrs={'class': 'form-control myform-focus text-center', 'id':'apearence', 'style':'background-color: white !important;'}),
            'apearence_observation': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'Observaciones', 'id':'apearence_observation'}),
            'core': Select(attrs={'class': 'form-control myform-focus text-center', 'id':'core'}),
            'exterior_dia': TextInput(attrs={'class': 'form-control myform-focus text-center', 'placeholder':'Resultado', 'id':'exterior_dia'}),
            'print_spec': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'Especificación', 'id':'print_spec'}),
            'print': TextInput(attrs={'class': 'form-control myform-focus text-center', 'placeholder':'Resultado', 'id':'print'}),
            'winding_position': TextInput(attrs={'class': 'form-control myform-focus text-center', 'placeholder':'Resultado', 'id':'winding_position'}),
            'dist_boder_material': TextInput(attrs={'class': 'form-control myform-focus text-center', 'placeholder':'Resultado', 'id':'dist_boder_material'}),
            'joint_color': Select(attrs={'class': 'form-control myform-focus text-center', 'id':'joint_color'}),
            'joint_color_observation': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'Observaciones', 'id':'joint_color_observation'}),
            'static_spec': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'Máximo:', 'id':'static_spec'}),
            'static': TextInput(attrs={'class': 'form-control myform-focus text-center', 'placeholder':'Resultado', 'id':'static'}),
            'packaging_spec': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'Especificación', 'id':'packaging_spec'}),
            'packaging': TextInput(attrs={'class': 'form-control myform-focus text-center', 'placeholder':'Resultado', 'id':'packaging'}),
            'pallet_spec': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'Especificación', 'id':'pallet_spec'}),
            'pallet': TextInput(attrs={'class': 'form-control myform-focus text-center', 'placeholder':'Resultado', 'id':'pallet'}),
            'n_litters_spec': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'Especificación', 'id':'n_litters_spec'}),
            'n_litters': TextInput(attrs={'class': 'form-control myform-focus text-center', 'placeholder':'Resultado', 'id':'n_litters'}),
            'identification': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'Especificación', 'id':'identification'}),
            'ex_tag': CheckboxInput(attrs={'class':'form-check-input justify-content-center', 'id':'ex_tag'}),
            'in_tag': CheckboxInput(attrs={'class':'form-check-input justify-content-center', 'id':'in_tag'}),
        }

class TestFileForm(ModelForm):
    quality_analist = ModelChoiceField(
        queryset=QualityAnalyst.objects.filter(active=True).order_by('name'),
        widget=Select(attrs={'class': 'form-control myform-focus', 'id':'quality_analist'})
    )
    production_operator = ModelChoiceField(
        queryset=ProductionOperator.objects.filter(active=True).order_by('name'),
        widget=Select(attrs={'class': 'form-control myform-focus', 'id':'production_operator'})
    )
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TestFileForm, self).__init__(*args, **kwargs)
        
        if user is not None and not user.has_perm('essays.boss_sign_testfile'):
            self.fields['boss'].widget.attrs['readonly'] = True
        if user is not None and not user.has_perm('essays.idat_sign_testfile'):
            self.fields['idat'].widget.attrs['readonly'] = True
        if user is not None and not user.has_perm('essays.supv_sign_testfile'):
            self.fields['supervisor'].widget.attrs['readonly'] = True

    class Meta:
        model = TestFile
        fields = (
            "turn",
            "date",
            'observation',
            'quality_analist',
            'production_operator',
            'supervisor',
            'boss',
            'idat',
        )
        widgets ={
            'turn': Select(attrs={'class': 'form-control myform-focus text-center', 'aria-label':'Formato', 'id':'turn'}),
            'date': DateInput(attrs={'class':'form-control align-items-center myform-focus text-center', 'autocomplete':'off', 'placeholder':'DD/MM/AAAA', 'id':'date'}),
            'supervisor': TextInput(attrs={'class': 'form-control myform-focus text-center', 'id':'supervisor'}),
            'boss': TextInput(attrs={'class': 'form-control myform-focus text-center', 'id':'boss'}),
            'idat': TextInput(attrs={'class': 'form-control myform-focus text-center', 'id':'idat'}),
        }
        
class TestFileEssayForm(ModelForm): 
    class Meta:
        model = TestFileEssay 
        fields = (
            'essay',
        )
        widgets = { 
            'essay': Select(attrs={'class': 'form-control myform-focus text-center'}),
        } 

   
TestFileEssayFormset = inlineformset_factory(TestFile, TestFileEssay, 
        fields = (
            'essay',
        ),
        formset=BaseInlineFormset,
        widgets = { 
            'essay': Select(attrs={'class': 'form-control myform-focus text-center'}),
        }, 
        extra=0,

    )
    
TestFileEssayResultFormset = inlineformset_factory(TestFileEssay, TestFileEssayResult, 
        fields=(
            'result_t',
            'result_a',
            'check_a',
            'result_c',
            'check_c',
            'result_b',
            'check_b',
            ),
        extra=0,
        formset=BaseInlineFormset,
        widgets = { 
            'bobbin': NumberInput(attrs={'class':'form-control align-items-center myform-focus text-center', 'min':'1', 'placeholder':'-', 'value':'1' }),
            'result_t': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'style':'padding-right: 1.3em !important'}),
            'result_a': NumberInput(attrs={'class': 'form-control myform-focus text-center', 'min':'0', 'placeholder':'A'}),
            'result_c': NumberInput(attrs={'class': 'form-control myform-focus text-center', 'min':'0', 'placeholder':'C'}),
            'result_b': NumberInput(attrs={'class': 'form-control myform-focus text-center', 'min':'0', 'placeholder':'B'}),
        }, 
    )


class TechnicalSpecsForm(ModelForm):
    quality_analist = ModelChoiceField(
        queryset=QualityAnalyst.objects.filter(active=True).order_by('name'),
        widget=Select(attrs={'class': 'form-control myform-focus', 'id':'quality_analist'})
    )   
    class Meta:
        model = TechnicalSpecs
        fields = (
            'date',
            'quality_analist',
            'observation',
            'boss',
        )
        widgets = {
            'date': DateInput(attrs={'class':'form-control align-items-center myform-focus text-center', 'autocomplete':'off', 'placeholder':'DD/MM/AAAA', 'id':'date'}),
            'boss': TextInput(attrs={'class': 'form-control myform-focus', 'id':'boss'}),
        }

class AnnexForm(ModelForm):
    
    class Meta:
        model = Annex
        fields = (
            'identification',
            'image',
            )
        widgets = {
            'identification': Textarea(attrs={'class':'form-control align-items-center myform-focus', 'style':'transition: none !important;', 'rows':'2'}),
        }
class ArtEntryElementForm(ModelForm):
    class Meta:
        model = ArtEntryElement
        fields = '__all__'
        widgets ={
            'sales_test_request':   Select(attrs={'class':'form-control myform-focus text-center', 'id':'sales_test_request'}),
            'product_client':       Select(attrs={'class':'form-control myform-focus text-center', 'id':'product_client'}),
            'client':               Select(attrs={'class':'form-control myform-focus text-center', 'id':'client', 'required':''}),
            'date':                 DateInput(attrs={'class':'form-control myform-focus text-center date-widget', 'value':dateformat.format(timezone.now(), 'd/m/Y'), 'placeholder':'DD/MM/AAAA', 'id':'date'}),
            'ambiental_description':TextInput(attrs={'class':'form-control myform-focus d-none', 'placeholder':'Especifique', 'id':'ambiental_description'}),
            'ee_other_description': TextInput(attrs={'class':'form-control myform-focus d-none', 'placeholder':'Especifique', 'id':'ee_other_description' }),
            'lr_other_description': TextInput(attrs={'class':'form-control myform-focus d-none', 'placeholder':'Especifique', 'id':'lr_other_description' }),
            'sc_other_description': TextInput(attrs={'class':'form-control myform-focus d-none', 'placeholder':'Especifique', 'id':'sc_other_description' }),
            'ssmtc_description':    TextInput(attrs={'class':'form-control myform-focus d-none', 'placeholder':'Especifique', 'id':'ssmtc_description'    }),
            'nmp_description':      TextInput(attrs={'class':'form-control myform-focus d-none', 'placeholder':'Especifique', 'id':'nmp_description'      }),
            'norms_description':    TextInput(attrs={'class':'form-control myform-focus d-none', 'placeholder':'Indique',     'id':'norms_other_description'    }),
            'tech_inv_description': TextInput(attrs={'class':'form-control myform-focus d-none', 'placeholder':'Especifique', 'id':'tech_inv_description' }),
            'hr_description':       TextInput(attrs={'class':'form-control myform-focus d-none', 'placeholder':'Especifique', 'id':'hr_description'       }),
            'failure_description':  TextInput(attrs={'class':'form-control myform-focus', 'placeholder':'', 'id':'failure_specification'  }),
            'service_requirements': TextInput(attrs={'class':'form-control myform-focus', 'placeholder':'', 'id':'service_requirements'}),
            'involved_processes':   TextInput(attrs={'class':'form-control myform-focus', 'placeholder':'', 'id':'involved_processes'  }),
            'fail_consequence':     TextInput(attrs={'class':'form-control myform-focus', 'placeholder':'', 'id':'fail_consequence'    }),
            'test_client':          TextInput(attrs={'class':'form-control myform-focus', 'placeholder':'', 'id':'test_client'         }),
            'description':          TextInput(attrs={'class':'form-control myform-focus', 'placeholder':'', 'id':'description'         }),
            'elaborator':           TextInput(attrs={'class':'form-control myform-focus', 'placeholder':'', 'id':'elaborator'          }),
            'reviewer':             TextInput(attrs={'class':'form-control myform-focus', 'placeholder':'', 'id':'reviewer'            }),
            'product':              TextInput(attrs={'class':'form-control myform-focus', 'placeholder':'', 'id':'product'             }),
            'design':               TextInput(attrs={'class':'form-control myform-focus', 'placeholder':'', 'id':'design'              }),
            'op':                   TextInput(attrs={'class':'form-control myform-focus', 'placeholder':'', 'id':'op'                  }),
            'technical_assistance': CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'technical_assistance'}),
            'check_test_client':    CheckboxInput(attrs={'class':'d-none',                'id':'check_test_client'   }),
            'mechanichal_plans':    CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'mechanichal_plans'   }),
            'post_sale_service':    CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'post_sale_service'   }),
            'technical_specs':      CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'technical_specs'     }),
            'delivery_date':        CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'delivery_date'       }),
            'quantity':             CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'quantity'            }),
            'mounting':             CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'mounting'            }),
            'printing':             CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'printing'            }),
            'lamination':           CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'lamination'          }),
            'covering':             CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'covering'            }),
            'cutting':              CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'cutting'             }),
            'reaming':              CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'reaming'             }),
            'bagging':              CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'bagging'             }),
            'gazette':              CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'gazette'             }),
            'iso':                  CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'iso'                 }),
            'not_applicable':       CheckboxInput(attrs={'class':'form-check-input mt-2 na-check', 'childs':'lr-check', 'id':'not_applicable'}),
            'cpe':                  CheckboxInput(attrs={'class':'form-check-input mt-2 lr-check', 'id':'cpe'                 }),
            'barcode':              CheckboxInput(attrs={'class':'form-check-input mt-2 lr-check', 'id':'barcode'             }),
            'nutrituonal_table':    CheckboxInput(attrs={'class':'form-check-input mt-2 lr-check', 'id':'nutrituonal_table'   }),
            'net_content':          CheckboxInput(attrs={'class':'form-check-input mt-2 lr-check', 'id':'net_content'         }),
            'sanitary_reg':         CheckboxInput(attrs={'class':'form-check-input mt-2 lr-check', 'id':'sanitary_reg'        }),
            'lr_other':             CheckboxInput(attrs={'class':'form-check-input mt-2 lr-check description-selector', 'id':'lr_other'}),
            'ee_other':             CheckboxInput(attrs={'class':'form-check-input mt-2 description-selector', 'id':'ee_other'}),
            'sc_other':             CheckboxInput(attrs={'class':'form-check-input mt-2 description-selector', 'id':'sc_other'}),
            'ssmtc':                CheckboxInput(attrs={'class':'form-check-input mt-2 description-selector', 'id':'ssmtc'   }),
            'nmp':                  CheckboxInput(attrs={'class':'form-check-input mt-2 description-selector', 'id':'nmp'     }),
            'norms':                CheckboxInput(attrs={'class':'form-check-input mt-2 description-selector', 'id':'norms'   }),
            'norms_other':          CheckboxInput(attrs={'class':'form-check-input mt-2 description-selector', 'id':'norms_other'}),
            'tech_inv':             CheckboxInput(attrs={'class':'form-check-input mt-2 description-selector', 'id':'tech_inv'}),
            'failure':              CheckboxInput(attrs={'class':'form-check-input mt-2 description-selector', 'id':'failure' }),
            'hr':                   CheckboxInput(attrs={'class':'form-check-input mt-2 description-selector', 'id':'hr'      }),
            'similar_products':     CheckboxInput(attrs={'class':'form-check-input mt-2 description-selector', 'id':'similar_products'}),
            'ambiental':            CheckboxInput(attrs={'class':'form-check-input mt-2 description-selector', 'id':'ambiental'       }),
            'samples':              CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'samples'             }),
            'art':                  CheckboxInput(attrs={'class':'form-check-input mt-2', 'id':'art'                 }),
        }
        labels = {
            'check_test_client':'Usar Cliente de Prueba',
            'test_client':'Cliente de Prueba',
            'client':'Cliente',
            'date':'Fecha',
            'product':'Nombre Completo del Producto',
            'design':'Diseño',
            'samples':'Muestras del Cliente',
            'mechanichal_plans':'Planos Mecánicos del Cliente',
            'technical_specs':'Especificaciones Técnicas del Cliente',
            'art':'Arte del Cliente',
            'ee_other':'Otros',
            'ee_other_description':'Especifique',
            'product_performance':'Requisitos Funcionales del Producto',
            'service_requirements':'Requisitos del Servicio',
            'cpe':'C.P.E.',
            'barcode':'Código de Barras',
            'nutrituonal_table':'Tabla Nutricional',
            'net_content':'Contenido Neto',
            'sanitary_reg':'Registro Sanitario',
            'lr_other':'Otros',
            'lr_other_description':'Especifique',
            'not_applicable':'No Aplica',
            'delivery_date':'Fecha de entrega',
            'quantity':'Cantidad',
            'technical_assistance':'Asistencia Técnica',
            'post_sale_service':'Servicio Post-Venta',
            'sc_other':'Otro',
            'sc_other_description':'Especifique',
            'ssmtc':'¿Se requiere de alguna condición de almacenamiento, manipulación, transporte y entrega específica?',
            'ssmtc_description':'Especifique',
            'nmp':'¿Se Requiere Desarrollo de nuevas materias primas y/o proveedores?',
            'nmp_description':'Especifique',
            'norms':'Normas Nacionales y/o Internacionales',
            'iso':'Norma ISO 9001-2015',
            'gazette':'<abbr title="Normas sobre Prácticas para la Fabricación, Almacenamiento y Transporte de Envases, Empaques y/o Artículos Destinados a estar en Contacto con Alimentos">Gaceta Oficial Nº 38.678 del 8 de mayo de 2007</abbr>',
            'norms_other':'Otras',
            'mounting':'Montaje',
            'printing':'Impresión',
            'lamination':'Laminación',
            'covering':'Recubrimiento',
            'cutting':'Corte',
            'reaming':'Resmado',
            'bagging':'Bolseado',
            'tech_inv':'¿Se requiere inversión tecnológica para este desarrollo?',
            'tech_inv_description':'Especifique',
            'hr':'¿Se requiere de recursos humanos para el diseño y desarrollo?',
            'hr_description':'Especifique',
            'similar_products':'¿Se tienen registros de productos similares?',
            'op':'OP Nro.',
            'description':'Descripción',
            'product_client':'Cliente',

            'ambiental':'¿Se requiere de condiciones ambientales especiales para mantener el producto?',
            'ambiental_description':'Especifique',
            'failure':'¿Existen fallas potenciales?',
            'failure_description':'Especifique',
            'fail_consequence':'¿Cuales serían las Consecuencias de éstas fallas?',

            'sales_test_request':'Solicitud de Ventas',

            'observation':'Observaciones',
            'elaborator':'Realizado Por',
            'reviewer':'Revisado Por',
        }

    documents = MultipleFileField(
        required=False,
        widget=MultipleFileInput(attrs={'multiple': True, 'class':'d-none', 'id': 'documents', 'accept': '.pdf,.doc,.docx,.xls,.xlsx,.xlsm,.jpeg,.jpg,.png'}),
        label='Documentos'
    )
    def save(self, commit=True):
        instance = super(ArtEntryElementForm, self).save(commit=False)
        if commit:
            instance.save()
            files = self.cleaned_data.get('documents', [])
            for file in files:
                validate_file_type(file)
                validate_file_size(file)

                original_filename = file.name
                extension = os.path.splitext(original_filename)[1]
                new_filename = f"entry_element_{instance.id}-{uuid.uuid4()}{extension}"
                file.name = new_filename

                doc = Document.objects.create(file=file, label=limit_file_name(original_filename))

                instance.documents.add(doc)
            instance.save()
        return instance

class ArtAnalysisForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ArtAnalysisForm, self).__init__(*args, **kwargs)
        self.fields['supplied_material'].choices = [choice for choice in self.fields['supplied_material'].choices if choice[0]]
        self.fields['printer'].choices = [choice for choice in self.fields['printer'].choices if choice[0]]

        self.fields['print_type'].choices = [choice for choice in self.fields['print_type'].choices if choice[0]]
        self.fields['photocell'].choices = [choice for choice in self.fields['photocell'].choices if choice[0]]
        self.fields['displacement'].choices = [choice for choice in self.fields['displacement'].choices if choice[0]]

    class Meta:
        model = ArtAnalysis
        fields = '__all__'
        widgets = {
            'requester': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder': 'Solicitante'}),
            'supplied_material': Select(attrs={'class': 'form-select myform-focus'}),
            'supplied_material_other': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder': 'Otro material'}),
            'printer': Select(attrs={'class': 'form-select myform-focus'}),
            'print_type': Select(attrs={'class': 'form-select myform-focus'}),
            'printed_development_mm': NumberInput(attrs={'class': 'form-control myform-focus', 'step': 'any'}),
            'package_unit_length_mm': NumberInput(attrs={'class': 'form-control myform-focus', 'step': 'any'}),
            'k': TextInput(attrs={'class': 'form-control myform-focus'}),
            'distortion_percent': NumberInput(attrs={'class': 'form-control myform-focus', 'step': 'any'}),
            'distorted_development_mm': NumberInput(attrs={'class': 'form-control myform-focus', 'step': 'any'}),
            'adjusted_printed_unit_length_mm': NumberInput(attrs={'class': 'form-control myform-focus', 'step': 'any'}),
            'repeats_per_development': NumberInput(attrs={'class': 'form-control myform-focus', 'step': 'any'}),
            'client_bobbin_width_mm': NumberInput(attrs={'class': 'form-control myform-focus', 'step': 'any'}),
            'plant_bobbin_width_mm': NumberInput(attrs={'class': 'form-control myform-focus', 'step': 'any'}),
            'repeats_per_printed_width': NumberInput(attrs={'class': 'form-control myform-focus', 'step': 'any'}),
            'printed_width_mm': NumberInput(attrs={'class': 'form-control myform-focus', 'step': 'any'}),
            'distance_between_repeats_width_mm': NumberInput(attrs={'class': 'form-control myform-focus', 'step': 'any'}),
            'package_unit_width_mm': NumberInput(attrs={'class': 'form-control myform-focus', 'step': 'any'}),
            'plate_type': TextInput(attrs={'class': 'form-control myform-focus'}),
            'thickness': TextInput(attrs={'class': 'form-control myform-focus'}),
            'photocell': Select(attrs={'class': 'form-select myform-focus'}),
            'photocell_width_mm': NumberInput(attrs={'class': 'form-control myform-focus', 'step': 'any'}),
            'photocell_length_mm': NumberInput(attrs={'class': 'form-control myform-focus', 'step': 'any'}),
            'distance_between_photocells_mm': NumberInput(attrs={'class': 'form-control myform-focus', 'step': 'any'}),
            'tolerance_mm': NumberInput(attrs={'class': 'form-control myform-focus', 'step': 'any'}),
            'photocell_colors': TextInput(attrs={'class': 'form-control myform-focus'}),
            'total_colors': NumberInput(attrs={'class': 'form-control myform-focus', 'step': 'any'}),
            'cut_bar_colors': TextInput(attrs={'class': 'form-control myform-focus'}),
            'displacement': Select(attrs={'class': 'form-select myform-focus'}),
            'roll_down_suggestions': TextInput(attrs={'class': 'form-control myform-focus'}),
        }
