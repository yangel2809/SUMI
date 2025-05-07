# -*- encoding: utf-8 -*-
#Copyright (c) 2024 - present, Daniel Escalona

import decimal
from locale import currency
from django.db import models
from django.db.models import Avg, Q
from django_quill.fields import QuillField
from simple_history.models import HistoricalRecords
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator, int_list_validator, MinValueValidator, MaxValueValidator, MinLengthValidator
from simple_history import register
from django.contrib.auth.models import User

from apps.home.models import Test, Structure
from apps.home.templatetags.home_tags import truncate

class Order(models.Model):

    external_id = models.BigIntegerField(blank=True, null=True)
    number = models.IntegerField(validators=[int_list_validator(allow_negative=False), MinValueValidator(0), MaxValueValidator(999999999)], blank=True, null=True)
    sale_order = models.ForeignKey('sales.SaleOrder', related_name='production_order', on_delete=models.SET_NULL, blank=True, null=True)
    date = models.DateField(null=True)

    deleted = models.BooleanField(default=False, blank=True, null=True)
    deleted_by = models.CharField(max_length=30, blank=True, null=True)
    deleted_time = models.DateTimeField(blank=True, null=True)
    deleted_reason = models.TextField(default='', blank=True, null=True)

    def get_technicalspecs(self):
        try:
            return self.technicalspecs# type: ignore
        except ObjectDoesNotExist:
            return None

    @property
    def status(self):
        statuses = {}
        printer_boot = PrinterBoot.objects.filter(production_order__pk=self.id).last()#type:ignore
        laminator_boot = LaminatorBoot.objects.filter(production_order__pk=self.id).last()#type:ignore
        cutter_boot = CutterBoot.objects.filter(production_order__pk=self.id).last()#type:ignore

        latest_boot = laminator_boot or printer_boot

        if latest_boot:
            if laminator_boot:
                reports = TestFile.objects.filter(boot_l__id=latest_boot.pk)
            else:
                reports = TestFile.objects.filter(boot_p__id=latest_boot.pk)
            latest_report = reports.last()

            if latest_report:
                if not latest_report.boss:
                    reviewer = 'ASCA'
                    code = 'last_report_one_review'
                    statuses['code'] = code
                    statuses['message'] = f'Último reporte pendiente por revisión de {reviewer}'
                    statuses['color'] = 'warning'
                    statuses['icon'] = 'edit_document'
                    statuses['set'] = 'gmi'
                elif self.get_technicalspecs(): # type: ignore
                    if self.technicalspecs.boss:  # type: ignore
                        statuses['code'] = 'closed'
                        statuses['message'] = 'Expediente Completo'
                        statuses['color'] = 'success'
                        statuses['icon'] = 'checklist'
                        statuses['set'] = 'gmi'
                    else:
                        statuses['code'] = 'no_techspecs'
                        statuses['message'] = 'Certificado de Análisis pendiente por revisión'
                        statuses['icon'] = 'unknown_document'
                        statuses['set'] = 'gmi'
                else:
                    statuses['code'] = 'not_signed_techspecs'
                    statuses['message'] = 'Certificado de Análisis pendiente por revisión'
                    statuses['icon'] = 'unknown_document'
                    statuses['set'] = 'gmi'
            else:
                statuses['code'] = 'no_last_report'
                statuses['message'] = 'Último arranque sin reporte'
                statuses['icon'] = 'file-medical'
                statuses['set'] = 'fas'
        else:
            if self.sale_order:
                if not cutter_boot:
                    statuses['code'] = 'no_boot'
                    statuses['message'] = 'Sin arranques registrados'
                    statuses['color'] = 'danger'
                    statuses['icon'] = 'print_error'
                    statuses['set'] = 'gmi'
                else:
                    statuses['code'] = 'cut_no_boot'
                    statuses['message'] = 'Cortado sin arranques de impresora o laminadora registrados'
                    statuses['icon'] = 'print_disabled'
                    statuses['set'] = 'gmi'
            else:
                statuses['code'] = 'not_touched'
                statuses['message'] = 'Listo para producción'
                statuses['color'] = 'success'
                statuses['icon'] = 'print_connect'
                statuses['set'] = 'gmi'

        return statuses

    class Meta:
        verbose_name = ("Órden de Producción")
        verbose_name_plural = ("Órdenes de Producción")

    def __str__(self):
        return f'{self.number} - {self.sale_order.plan.product}'#type: ignore
class PrinterBoot (models.Model):
    #Parent----------------------------------------------
    production_order = models.ForeignKey('production.Order', on_delete=models.CASCADE, blank=True, null=True)#Comes from test request
    origin = models.CharField(max_length=15, blank=True, default=None, null=True)
    
    CRW_OPT=(
        ('e', 'Externa'),
        ('i', 'Interna'),
    )
    TRN_OPT=(
        ('I', 'I'),
        ('II', 'II'),
        ('III', 'III'),
    )
    DIN_OPT=(
        ('36', '36'),
        ('38', '38'),
        ('40', '40'),
        ('42', '42'),
        ('44', '44'),
        ('46', '46'),
    )
    UNT_OPT=(
        ('mm','mm'),
        ('cm','cm'),
        ('m','m'),
    )
    UN2_OPT=(
        ('mm','mm'),
        ('cm','cm'),
        ('in','in'),
    )
    WIN_OPT=(
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8')
    )
    #Machine-------------------------------------------------------------------------
    date_time = models.DateTimeField(null=True)
    turn = models.CharField(max_length=3, choices = TRN_OPT, blank=False, null=True)
    
    printer = models.ForeignKey('essays.Printer', on_delete=models.RESTRICT, related_name='printer_pr', blank=False, null=True)
    machine_speed = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], null=True)
    check_crown_treatment = models.BooleanField(default=False)

    #Sustrate-------------------------------------------------------------------------
    s_index = models.IntegerField(default=0)
    provider = models.CharField(max_length=100, blank=True, null=True)
    sustrate_width = models.IntegerField(validators=[int_list_validator(allow_negative=False)], blank=True, null=True)
    crown_treatment_side = models.CharField(max_length=1, choices = CRW_OPT, blank=True, null=True)
    surface_tension = models.CharField(max_length=2, choices = DIN_OPT, blank=True, null=True)
   
    #Colors---------------------------------------------------------------------------
    sta_01 = models.CharField(max_length=20, blank=False, default='-')
    sta_02 = models.CharField(max_length=20, blank=False, default='-')
    sta_03 = models.CharField(max_length=20, blank=False, default='-')
    sta_04 = models.CharField(max_length=20, blank=False, default='-')
    sta_05 = models.CharField(max_length=20, blank=False, default='-')
    sta_06 = models.CharField(max_length=20, blank=False, default='-')
    sta_07 = models.CharField(max_length=20, blank=False, default='-')
    sta_08 = models.CharField(max_length=20, blank=False, default='-')
    sta_09 = models.CharField(max_length=20, blank=False, default='-')
    sta_10 = models.CharField(max_length=20, blank=False, default='-')

    #TestingSample--------------------------------------------------------------------
    SMP_OPT=(
        ('Si','Si'),
        ('No','No'),
        ('NA','No Aplica'),
    )
    standar = models.CharField(max_length=2, choices = SMP_OPT, blank=False, default='NA')
    art = models.CharField(max_length=2, choices = SMP_OPT, blank=False, default='NA')
    pre_print = models.CharField(max_length=2, choices = SMP_OPT, blank=False, default='NA')
    develop_folder = models.CharField(max_length=2, choices = SMP_OPT, blank=False, default='NA')

    #PrintControl---------------------------------------------------------------------
    STA_OPT=(
        ('No Aplica', 'No aplica'),
        ('Claro', 'Claro'),
        ('Estándar', 'Estándar'),
        ('Oscuro', 'Oscuro'),
    )
    CON_OPT_0=(
        ('na', 'No aplica'),
        ('ac', 'Aceptado'),
        ('de', 'Deficiente'),
        ('ad', 'Aceptado con desviación'),
    )
    CON_OPT_1=(
        ('na', 'No aplica'),
        ('ac', 'Aceptado'),
        ('de', 'Deficiente'),
    )
    CON_OPT_2=(
        ('ac', 'Aceptado'),
        ('de', 'Deficiente'),
    )

    register = models.CharField(max_length=2, choices = CON_OPT_0, blank=False, null=True)
    text = models.CharField(max_length=2, choices = CON_OPT_0, blank=False, null=True)
    dimensions = models.CharField(max_length=2, choices = CON_OPT_0, blank=False, null=True)
    cutting_guide = models.CharField(max_length=2, choices = CON_OPT_0, blank=False, null=True)
    photocell = models.CharField(max_length=2, choices = CON_OPT_0, blank=False, null=True)
    barcode = models.CharField(max_length=2, choices = CON_OPT_0, blank=False, null=True)
   
    develop = models.CharField(max_length=30, blank=True, null=True)
    develop_unit = models.CharField(max_length=3, choices=UN2_OPT, blank=True, null=True)
    develop_result = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], blank=True, null=True)

    cut_width_result = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], blank=True, null=True)
    design = models.CharField(max_length=30, blank=True, null=True)

    #Winding
    machine_winding = models.CharField(max_length=1, choices = WIN_OPT, blank=True, null=True)
    winding_description = models.CharField(max_length=100, blank=True, null=True)
    
    #Repetition
    r_left = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], blank=True, null=True)
    r_right = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], blank=True, null=True)
    r_center = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], blank=True, null=True)
    r_average = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], blank=True, null=True)

    color_standar = models.CharField(max_length=10, choices = STA_OPT, blank=False, null=True)

    #InkControl
    anchorage = models.CharField(max_length=2, choices = CON_OPT_2, blank=False, null=True)
    rub = models.CharField(max_length=2, choices = CON_OPT_2, blank=False, null=True)
    ther_resistance = models.CharField(max_length=2, choices = CON_OPT_1, blank=False, null=True)
    anchorage_resistance = models.CharField(max_length=2, choices = CON_OPT_1, blank=False, null=True)

    cut_diagram = models.BooleanField(default=False)

    observation = QuillField(blank=True, null=True)

    quality_analist = models.ForeignKey('essays.QualityAnalyst', related_name='quality_analist_pr', on_delete=models.SET_NULL, null=True)
    production_operator = models.ForeignKey('essays.ProductionOperator', related_name='production_operator_pr', on_delete=models.SET_NULL, null=True)

    history = HistoricalRecords()
    class Meta:
        verbose_name = 'Arranque de impresora'
        verbose_name_plural = 'Arranques de impresoras'

class LaminatorBoot(models.Model):
    production_order = models.ForeignKey('production.Order', on_delete=models.CASCADE, blank=True, null=True)
    origin = models.CharField(max_length=15, blank=True, default=None, null=True)

    TRN_OPT=(
        ('I', 'I'),
        ('II', 'II'),
        ('III', 'III'),
    )
    STP_OPT=(
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
    )
    APE_OPT=(
        ('AC','Aceptado'),
        ('DE','Deficiente'),
        ('NA','No Aplica'),
    )
    #Machine--------------------------------------------------------------------
    laminator = models.ForeignKey('essays.Laminator', related_name='laminator_pr', on_delete=models.RESTRICT, blank=True, null=True)
    
    date_time = models.DateTimeField(null=True)
    turn = models.CharField(max_length=3, choices = TRN_OPT, blank=False, null=True)

    machine_speed = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], null=True)
    crown_treatment_pri = models.BooleanField(default=None, null=True)
    crown_treatment_sec = models.BooleanField(default=None, null=True)
    #---------------------------------------------------------------------------

    #Structure------------------------------------------------------------------
    step = models.CharField(max_length=1, choices=STP_OPT, null=True)
    st_1 = models.CharField(max_length=25, blank=False, null=True)
    st_2 = models.CharField(max_length=25, blank=False, null=True)
    st_3 = models.CharField(max_length=25, blank=True, null=True)
    st_4 = models.CharField(max_length=25, blank=True, null=True)
    adhesive = models.ForeignKey('home.Material', related_name='adhesive_pr', on_delete=models.RESTRICT, blank=True, null=True)
    batch = models.CharField(max_length=20, blank=True, null=True)
    formula = models.CharField(max_length=7, blank=True, null=True)
    #---------------------------------------------------------------------------

    time = models.CharField(max_length=100, blank=True, null=True)
    temp = models.IntegerField(validators=[int_list_validator(allow_negative=False)], blank=True, null=True)
    observation = QuillField(blank=True, null=True)

    quality_analist = models.ForeignKey('essays.QualityAnalyst', related_name='quality_analist_pr_lm', on_delete=models.SET_NULL, null=True)
    production_operator = models.ForeignKey('essays.ProductionOperator', related_name='production_operator_pr_lm', on_delete=models.SET_NULL, null=True)

    history = HistoricalRecords()
    
    @property
    def joined_layers(self):
        layers = [layer for layer in [self.st_1, self.st_2, self.st_3, self.st_4] if layer and not layer.lower().startswith('adhe')]
        return ' + '.join(layers)

    class Meta:
        verbose_name = ("Arranque de Laminadora")
        verbose_name_plural = ("Arranques de Laminadora")

    def __str__(self):
        return f'{self.production_order} - {self.production_order} LAM paso: {self.step}'
    
class LaminationEssay(models.Model):

    laminator_boot = models.ForeignKey('production.LaminatorBoot', related_name='laminator_boot_pr', on_delete=models.CASCADE, blank=True, null=True)
    essay = models.ForeignKey('home.Essay', related_name='essay_pr', on_delete=models.RESTRICT, blank=False, null=True)

    result_t = models.CharField(max_length=100, blank=True, null=True)
    
    result_a = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], blank=True, null=True)
    check_a = models.BooleanField(default=False, blank=True)
    result_b = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], blank=True, null=True)
    check_b = models.BooleanField(default=False, blank=True)
    result_c = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], blank=True, null=True)
    check_c = models.BooleanField(default=False, blank=True)
    result_p = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], blank=True, null=True)
    check_p = models.BooleanField(default=False, blank=True)

    history = HistoricalRecords()
    class Meta:
        verbose_name = ("Análisis de Arranque de laminacion")
        verbose_name_plural = ("Análisis de Arranques de laminacion")

    def __str__(self):
        if self.essay.unit == None:#type:ignore
            return 'ME-' + self.essay.method + ' - ' + self.essay.name #type:ignore
        else:
            return 'ME-' + self.essay.method + ' - ' + self.essay.name + ' - ' + self.essay.unit.symbol #type:ignore

class CutterBoot(models.Model):
    TRN_OPT=(
        ('I', 'I'),
        ('II', 'II'),
        ('III', 'III'),
    )
    CLR_OPT=(
        ('Rojo', 'Rojo'),
        ('Negro', 'Negro'),
        ('Marrón', 'Marrón'),
        ('Transparente', 'Transparente'),
    )
    APE_OPT=(
        ('AC','Aceptado'),
        ('DE','Deficiente'),
        ('NA','No Aplica'),
    )
    DIA_OPT=(
        ('kg','kg'),
        ('mm','mm'),
        ('cm','cm'),
        ('m','m'),
    )
    COR_OPT=(
        ('3','3"'),
        ('6','6"')
    )
    production_order = models.ForeignKey('production.Order', on_delete=models.CASCADE, blank=True, null=True)#Comes from test request
    
    machine = models.ForeignKey('essays.Cutter', related_name='machine_pr', on_delete=models.RESTRICT, null=True)
    rewinder = models.ForeignKey('essays.Rewinder', related_name='rewinder_pr', on_delete=models.RESTRICT, blank=True, null=True)

    date_time = models.DateTimeField(null=True)
    turn = models.CharField(max_length=3, choices = TRN_OPT, blank=False, null=True)

    machine_speed = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], null=True)
    as_treatment = models.BooleanField(default=False)
    
    #Repetition spec from test request = models.
    r_a = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], blank=True, null=True)
    r_b = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], blank=True, null=True)
    r_c = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], blank=True, null=True)
    r_p = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], blank=True, null=True)

    #Width spec from test request = models.
    w_a = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], blank=True, null=True)
    w_b = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], blank=True, null=True)
    w_c = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], blank=True, null=True)
    w_p = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], blank=True, null=True)
    
    apearence = models.CharField(max_length=2, choices = APE_OPT, blank=False, null=True)
    apearence_observation = models.CharField(max_length=100, blank=True, null=True)
    core = models.CharField(max_length=2, choices = COR_OPT, blank=True, null=True)
    exterior_dia_bobbin = models.CharField(max_length=30, blank=True, null=True)
    exterior_dia_bobbin_unit = models.CharField(max_length=3, choices=DIA_OPT, blank=True, null=True)
    exterior_dia = models.CharField(max_length=60, blank=False, null=True)
    print_spec = models.CharField(max_length=60, blank=True, null=True)
    print = models.CharField(max_length=60, blank=True, null=True)
    winding_position = models.CharField(max_length=60, blank=True, null=True)
    dist_boder_cell_material = models.CharField(max_length=30, blank=True, null=True)
    dist_boder_material = models.CharField(max_length=60, blank=True, null=True)
    joint_color = models.CharField(max_length=60, choices = CLR_OPT, blank=True, null=True)
    joint_color_observation = models.CharField(max_length=100, blank=True, null=True)
    static_spec = models.CharField(max_length=60, blank=True, null=True)
    static = models.CharField(max_length=60, blank=True, null=True)
    packaging_spec = models.CharField(max_length=60, blank=True, null=True)
    packaging = models.CharField(max_length=60, blank=True, null=True)
    pallet_spec  = models.CharField(max_length=60, blank=True, null=True)
    pallet  = models.CharField(max_length=60, blank=True, null=True)
    n_litters_spec = models.CharField(max_length=60, blank=True, null=True)
    n_litters = models.CharField(max_length=60, blank=True, null=True)

    identification = models.CharField(max_length=50, blank=True, null=True)
    ex_tag = models.BooleanField(default=False)
    in_tag = models.BooleanField(default=False)

    observation = QuillField(blank=True, null=True)

    quality_analist = models.ForeignKey('essays.QualityAnalyst', related_name='quality_analist_pr_ct', on_delete=models.SET_NULL, null=True)
    production_operator = models.ForeignKey('essays.ProductionOperator', related_name='quality_analist_pr_ct', on_delete=models.SET_NULL, null=True)

    history = HistoricalRecords()
    class Meta:
        verbose_name = ("Arranque de cortadora")
        verbose_name_plural = ("Arranques de cortadoras")

    def __str__(self):
        return self.machine.name#type:ignore
    
class TestFile(models.Model):
    TRN_OPT=(
        ('I', 'I'),
        ('II', 'II'),
        ('III', 'III'),
    )
    TFT_OPT=(
        ('prt', 'prt'),
        ('lam', 'lam'),
    )
    FSH_OPT=(
        ('AC','Aceptado'),
        ('AD','Aceptado con Desviación'),
        ('DE','Deficiente'),
        ('NA','No Aplica'),
    )
    
    boot_p = models.ForeignKey("production.PrinterBoot", related_name='printer_boot_pr_rp', blank=True, on_delete=models.CASCADE, null=True)
    boot_l = models.ForeignKey("production.LaminatorBoot", related_name='laminator_boot_pr_rp', blank=True, on_delete=models.CASCADE, null=True)

    type = models.CharField(max_length=3, choices = TFT_OPT, blank=False, null=True)
    
    turn = models.CharField(max_length=3, choices = TRN_OPT, blank=False, null=True)
    date = models.DateField(null=True)
    
    quality_analist = models.ForeignKey('essays.QualityAnalyst', related_name='quality_analist_pr_rp', on_delete=models.SET_NULL, null=True)
    production_operator = models.ForeignKey('essays.ProductionOperator', related_name='production_operator_pr_rp', on_delete=models.SET_NULL, null=True)

    observation = QuillField(blank=True, null=True)

    supervisor = models.CharField(max_length=30, blank=True, null=True)
    boss = models.CharField(max_length=30, blank=True, null=True)
    
    date_created = models.DateTimeField(null=True, auto_now_add=True)
    history = HistoricalRecords()
    class Meta:
        verbose_name = ("Reporte de Control de Calidad")
        verbose_name_plural = ("Reportes de Control de Calidad")
        permissions = [
            (
                "boss_sign_testfile_pr",
                "Puede firmar un reporte de producción cómo revisado por jefe"
            ),
            (
                "supv_sign_testfile_pr",
                "Puede firmar un reporte cómo revisado por supervisor"
            ),
            (
                "idat_sign_testfile_pr",
                "Puede firmar un reporte de producción cómo revisado por IDAT"
            ),
        ]

    def __str__(self):

        name = 'report - ' + str(self.boot_l)
        if self.boot_p:
            name = 'report - ' + str(self.boot_p)
        return name
    
    def get_ordered_essays(self):
       all_essays = self.production_report.order_by('essay__priority')#type:ignore
       return all_essays
    
class TestFileEssay(models.Model):
    test_file = models.ForeignKey('production.TestFile', related_name='production_report', on_delete=models.CASCADE, null=True)

    essay = models.ForeignKey('home.Essay', related_name='essay_pr_rp', on_delete=models.RESTRICT, blank=False, null=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = ("Ensayos de Reporte de Control de Calidad")
        verbose_name_plural = ("Ensayos de Reportes de Control de Calidad")

    def get_plan(self):
        return self.test_file.boot_l.production_order.sale_order.plan if self.test_file.boot_l else self.test_file.boot_p.production_order.sale_order.plan#type: ignore
    
    @property
    def plan_spec(self):
        try:
            return self.get_plan().test_set.filter(essay__priority=self.essay.priority).first().spec#type: ignore
        except (Test.DoesNotExist, AttributeError):
            return None
        
    @property
    def plan_application(self):
        try:
            essay_name = self.get_plan().test_set.filter(essay__priority=self.essay.priority).first().essay.name#type: ignore
            if essay_name.startswith("Aplicación"):
                name_parts = essay_name.split("de")
                material = name_parts[1].strip()
                structures = self.get_plan().structure_set.filter(material_type__name__startswith=material)
                
                if structures.count() == 1:
                    structure = structures.first()
                    weight = truncate(structure.weight)
                    return f'{str(weight).replace(".", ",")} {self.plan_spec}'
                else:
                    weights = [f'{str(truncate(structure.weight)).replace(".", ",")} {self.plan_spec}' for structure in structures]
                    return ' / '.join(weights)
            else:
                return 'mo_match'
        except (Test.DoesNotExist, AttributeError) as e:
            return f'Exception: {type(e).__name__}, {str(e)}'
        
    @property
    def plan_weight(self):
        try:
            return self.get_plan().weight
        except (Test.DoesNotExist, AttributeError):
            return None
    @property
    def plan_thickness(self):
        try:
            return self.get_plan().thickness
        except (Test.DoesNotExist, AttributeError):
            return None
    @property
    def plan_weight_avg(self):
        try:
            return self.get_plan().weight_avg
        except (Test.DoesNotExist, AttributeError):
            return None
    @property
    def plan_thickness_avg(self):
        try:
            return self.get_plan().thickness_avg
        except (Test.DoesNotExist, AttributeError):
            return None
        
    @property
    def plan_delal(self):
        try:
            return self.get_plan().test_set.filter(essay__method='011').first().spec
        except (Test.DoesNotExist, AttributeError):
            return None
    @property
    def plan_cut(self):
        try:
            return self.get_plan().width_bobbin
        except (Test.DoesNotExist, AttributeError):
            return None

    @property
    def average(self):
        results = self.test_file_essay_pr.filter(Q(result_p__isnull=False)|Q(check_a=True)|Q(check_b=True)|Q(check_c=True)) #type:ignore
        average = results.aggregate(Avg('result_p'))['result_p__avg']

        checks = [result.check_p for result in results]
        valid_checks = [check for check, result in zip(checks, results) if result.result_p is not None]
        check_p = sum(valid_checks) / len(valid_checks) >= 0.5 if valid_checks else False

        if average is not None and average != 0:
            # Format average
            if self.essay.method in ['009', '003', '029', '005']: #type:ignore
                average_str = "{:.2f}".format(average)
            else:
                average_str = str(decimal.Decimal(average).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))

            # Append "-R" if check_p is True
            if check_p:
                average_str += "-R"
                if average == 0:
                    average_str = 'Rompe'
            return average_str
        
        else:
            return None
    
    @property
    def average_t(self):
        results = self.test_file_essay_pr.exclude(result_t__isnull=True) #type:ignore
        total_first = 0.0
        total_second = 0.0
        total_single = 0.0
        first_letter = None
        second_letter = None
        count = 0
        count_single = 0
        count_r_first = 0
        count_r_second = 0
        last_value = None
        for result in results:
            try:
                if '/' in result.result_t:
                    first_value, second_value = result.result_t.split('/')
                    if 'R' in first_value:
                        first_letter, first_number = first_value.split(':')
                        first_number = first_number.strip(' R').replace(',', '.')
                        count_r_first += 1
                    else:
                        first_letter, first_number = first_value.split(':')
                        first_number = first_number.replace(',', '.')
                    if 'R' in second_value:
                        second_letter, second_number = second_value.split(':')
                        second_number = second_number.strip(' R').replace(',', '.')
                        count_r_second += 1
                    else:
                        second_letter, second_number = second_value.split(':')
                        second_number = second_number.replace(',', '.')
                    total_first += float(first_number)
                    total_second += float(second_number)
                    count += 1
                else:
                    single_value = result.result_t.replace(',', '.')
                    if single_value.replace('.', '', 1).isdigit():
                        total_single += float(single_value)
                        count_single += 1
                    last_value = result.result_t
            except ValueError:
                continue  # Skip this result if it doesn't have the expected format
        if count > 0:
            avg_first = "{:.2f}".format(total_first/count).rstrip('0').rstrip('.')
            avg_second = "{:.2f}".format(total_second/count).rstrip('0').rstrip('.')
            if count_r_first/count >= 0.5:
                avg_first = str(avg_first) + ' R'
            if count_r_second/count >= 0.5:
                avg_second = str(avg_second) + ' R'
            return f"{first_letter}: {avg_first} / {second_letter}: {avg_second}"
        elif count_single > 0:
            avg_single = "{:.2f}".format(total_single/count_single).rstrip('0').rstrip('.')
            return avg_single
        elif last_value is not None:
            return last_value
        else:
            return None

        
    def __str__(self):
        return self.essay.name #type:ignore
        
class TestFileEssayResult(models.Model):

    essay = models.ForeignKey("production.TestFileEssay", related_name='test_file_essay_pr', on_delete=models.CASCADE, null=True)
    bobbin = models.ForeignKey("production.Bobbin", related_name='bobbin_pr', on_delete=models.CASCADE, blank=True, null=True)
 
    result_t = models.CharField(max_length=100, blank=True, null=True)
    result_a = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], blank=True, null=True)
    check_a = models.BooleanField(default=False, blank=True)
    result_b = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], blank=True, null=True)
    check_b = models.BooleanField(default=False, blank=True)
    result_c = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], blank=True, null=True)
    check_c = models.BooleanField(default=False, blank=True)
    result_p = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], blank=True, null=True)
    check_p = models.BooleanField(default=False, blank=True)

    class Meta:
        verbose_name = ("Resultados de ensayos de Reporte de Control de Calidad OP")
        verbose_name_plural = ("Resultados de ensayos de Reportes de Control de Calidad OP")

    def __str__(self):
        return str(self.pk)
    
class Bobbin(models.Model):
    #turn/fecha/analista
    TRN_OPT=(
        ('I', 'I'),
        ('II', 'II'),
        ('III', 'III'),
    )
    test_file = models.ForeignKey('production.TestFile', on_delete=models.CASCADE, null=True)
    turn = models.CharField(max_length=3, choices = TRN_OPT, blank=False, null=True)
    date = models.DateField(null=True)
    quality_analist = models.ForeignKey('essays.QualityAnalyst', related_name='quality_analist_pr_bb', on_delete=models.SET_NULL, null=True)
    production_operator = models.ForeignKey('essays.ProductionOperator', related_name='production_operator_pr_bb', on_delete=models.SET_NULL, null=True)
    class Meta:
        verbose_name = ("ID único para bobina OP")
        verbose_name_plural = ("ID único para bobinas OP")

    def __str__(self):
        return str(self.pk)

class TechnicalSpecs(models.Model):
    
    production_order = models.OneToOneField('production.Order', on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateField(null=True)
    
    observation = QuillField(blank=True, null=True)
    quality_analist = models.ForeignKey('essays.QualityAnalyst', related_name='quality_analist_pr_ts', on_delete=models.SET_NULL, null=True)
    boss = models.CharField(max_length=30, blank=True, null=True)
    
    history = HistoricalRecords()

    @property
    def dispatched_quantity(self):
        return self.dispatch_set.aggregate(sum_quantity=models.Sum('quantity'))['sum_quantity'] or 0 #type: ignore
    
class Dispatch(models.Model):
    technical_specs = models.ForeignKey("production.TechnicalSpecs", on_delete=models.CASCADE)
    f_date = models.DateField(null=True)
    e_date = models.DateField(null=True)
    batch_number = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(999999999)])
    quantity = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(99999999999)])
    
    class Meta:
        verbose_name = ("Despacho")
        verbose_name_plural = ("Despachos")

    def __str__(self):
        return self.f_date

