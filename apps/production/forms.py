"""
Copyright (c) 2023 - present, Daniel Escalona
"""
from django import forms
from django.forms import ModelForm, TextInput, Select
from django.core.validators import *
from django.forms.models import inlineformset_factory, modelform_factory, modelformset_factory#, BaseFormSet, formset_factory

from django.forms import *
from .models import *
from apps.essays.models import ProductionOperator, QualityAnalyst

class BaseInlineFormset(BaseInlineFormSet):
    def get_deletion_widget(self):
        return CheckboxInput(attrs={'class': 'form-check-input justify-content-center'})

class OpAsignForm(ModelForm):
    class Meta:
        model = Order
        fields = (
            "number",
            "sale_order",
            "date",
            )
        
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
            #'production_order',
            'printer',
            'date_time',
            'turn',
            'machine_speed',
            's_index',
            'provider',
            'sustrate_width',
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
            's_index': HiddenInput(attrs={'id':'s_index'}),
            'sustrate_width':NumberInput(attrs={'class': 'form-control myform-focus text-center', 'min':'0', 'placeholder':'0', 'id':'sustrate_width'}),
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
            'develop': TextInput(attrs={'class': 'form-control myform-focus flat-right', 'style':'padding-right: 1.4em !important;', 'placeholder':'', 'id':'develop', 'style':'padding-right: 1.3em !important'}),
            'develop_unit': Select(attrs={'class': 'form-control myform-focus flat-left', 'placeholder':'', 'id':'develop_unit'}),
            'develop_result': NumberInput(attrs={'class': 'form-control myform-focus text-center', 'min':'0', 'placeholder':'0', 'id':'develop_result'}),
            'cut_width_result': NumberInput(attrs={'class': 'form-control myform-focus text-center', 'min':'0', 'placeholder':'0', 'id':'cut_width_result'}),
            'design': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'design'}),
            'machine_winding': Select(attrs={'class': 'form-control myform-focus text-center', 'placeholder':'', 'id':'machine_winding'}),
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
            'production_order',
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
            'production_order': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'', 'id':'production_order'}),
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
            'exterior_dia_bobbin',
            'exterior_dia_bobbin_unit',
            'exterior_dia',
            'print_spec',
            'print',
            'winding_position',
            'dist_boder_cell_material',
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
            'exterior_dia_bobbin': TextInput(attrs={'class':'form-control align-items-center myform-focus flat-right', 'style':'padding-right: 1.4em !important;', 'placeholder':'0', 'id':'exterior_dia_bobbin'}),
            'exterior_dia_bobbin_unit': Select(attrs={'class':'text-center form-control align-items-center myform-focus flat-left', 'id':'exterior_dia_bobbin_unit'}),
            'exterior_dia': TextInput(attrs={'class': 'form-control myform-focus text-center', 'placeholder':'Resultado', 'id':'exterior_dia'}),
            'print_spec': TextInput(attrs={'class': 'form-control myform-focus', 'placeholder':'Especificación', 'id':'print_spec'}),
            'print': TextInput(attrs={'class': 'form-control myform-focus text-center', 'placeholder':'Resultado', 'id':'print'}),
            'winding_position': TextInput(attrs={'class': 'form-control myform-focus text-center', 'placeholder':'Resultado', 'id':'winding_position'}),
            'dist_boder_cell_material': TextInput(attrs={'class':'form-control text-center myform-focus', 'placeholder':'0mm', 'id':'dist_boder_cell_material'}),
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

        if user is not None and not user.has_perm('essays.change_testfile'):
            self.fields['turn'].widget.attrs['disabled'] = True
            self.fields['date'].widget.attrs['disabled'] = True
            self.fields['quality_analist'].widget.attrs['disabled'] = True
            self.fields['production_operator'].widget.attrs['disabled'] = True
        if user is not None and not user.has_perm('essays.boss_sign_testfile'):
            self.fields['boss'].widget.attrs['readonly'] = True
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
        )
        widgets ={
            'turn': Select(attrs={'class': 'form-control myform-focus text-center', 'aria-label':'Formato', 'id':'turn'}),
            'date': DateInput(attrs={'class':'form-control align-items-center myform-focus text-center', 'autocomplete':'off', 'placeholder':'DD/MM/AAAA', 'id':'date'}),
            'supervisor': TextInput(attrs={'class': 'form-control myform-focus text-center', 'id':'supervisor'}),
            'boss': TextInput(attrs={'class': 'form-control myform-focus text-center', 'id':'boss'}),
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
DispatchFormset = inlineformset_factory(TechnicalSpecs, Dispatch,
    fields = (
        'id',
        'f_date',
        'e_date',
        'batch_number',
        'quantity',
    ),
    formset=BaseInlineFormset,
    widgets = { 
        'id': HiddenInput(),
        'f_date': DateInput(attrs={'class':'form-control align-items-center myform-focus text-center', 'autocomplete':'off', 'placeholder':'Fecha de Fabricación', 'id':'date'}),
        'e_date': DateInput(attrs={'class':'form-control align-items-center myform-focus text-center', 'autocomplete':'off', 'placeholder':'Fecha de Vencimiento', 'id':'date'}),
        'batch_number': NumberInput(attrs={'class': 'form-control myform-focus text-center', 'min':'0', 'placeholder':'Nº de Lote'}),
        'quantity': NumberInput(attrs={'class': 'form-control myform-focus text-center', 'min':'0', 'placeholder':'Cantidad (Kg neto)'}),
    }, 
    extra=2,
    )
