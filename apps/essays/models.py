# -*- encoding: utf-8 -*-
#Copyright (c) 2023 - present, Daniel Escalona

#import datetime
import decimal
from django.db import models
from django.utils import timezone
from django.db.models import Avg, Q
from django_quill.fields import QuillField
from simple_history.models import HistoricalRecords
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator, int_list_validator, MinValueValidator, MaxValueValidator, MinLengthValidator
from simple_history import register
from django.contrib.auth.models import User
import test
from documents.models import Document

register(User)

class Format (models.Model):#Unused model
    name = models.CharField(max_length=9, validators=[MinLengthValidator(9)], null=True)
    revission = models.IntegerField(validators=[int_list_validator(allow_negative=False)], null=True)
    rev_date = models.DateField(null=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Formato'
        verbose_name_plural = 'Formatos'

    def __str__(self):
        name = self.name + ' - REV:' + str(self.revission) #type:ignore
        return (name) 

class Printer (models.Model):
    name = models.CharField(max_length=20, null=True)
    
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Máquina Impresora'
        verbose_name_plural = 'Máquinas Impresoras'
    
    def __str__(self):
        return (self.name) 

class Laminator (models.Model):
    name = models.CharField(max_length=20, null=True)
    
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Máquina Laminadora'
        verbose_name_plural = 'Máquinas Laminadoras'
    
    def __str__(self):
        return (self.name) 

class Cutter (models.Model):
    name = models.CharField(max_length=20, null=True)
    
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Máquina Cortadora'
        verbose_name_plural = 'Máquinas Cortadoras'
    
    def __str__(self):
        return (self.name) 
    
class Rewinder (models.Model):
    name = models.CharField(max_length=20, null=True)
    
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Máquina Rebobinadora'
        verbose_name_plural = 'Máquinas Rebobinadoras'
    
    def __str__(self):
        return (self.name) 
class EntryElement(models.Model):
    #main data
    check_test_client = models.BooleanField(default=False)
    test_client = models.CharField(max_length=100, blank=True, null=True)
    client = models.ForeignKey("home.Client", verbose_name=("Clientes"), related_name="ee_client", blank=True, on_delete=models.RESTRICT, null=True)
    date = models.DateField(null=True)
    #External elements---------------------------------->
    #1.Client requirement
    product = models.CharField(max_length=100, blank=False, null=True)
    design = models.CharField(max_length=100, blank=True, null=True)
    #2.Client suplied elements
    samples = models.BooleanField(default=False)
    mechanichal_plans = models.BooleanField(default=False)
    technical_specs = models.BooleanField(default=False)
    art = models.BooleanField(default=False)
    ee_other = models.BooleanField(default=False)
    ee_other_description = models.CharField(max_length=200, blank=True, null=True)
    #3.Product Performance and requirements
    product_performance = QuillField(blank=True, null=True)
    #4.Service requirements
    service_requirements = models.CharField(max_length=100, blank=True, null=True)
    #5.Legal Requirements 
    cpe = models.BooleanField(default=False)
    barcode = models.BooleanField(default=False)
    nutrituonal_table = models.BooleanField(default=False)
    net_content = models.BooleanField(default=False)
    sanitary_reg = models.BooleanField(default=False)
    not_applicable = models.BooleanField(default=False)
    lr_other = models.BooleanField(default=False)
    lr_other_description = models.CharField(max_length=200, blank=True, null=True)
    #6.Service COnditions
    delivery_date = models.BooleanField(default=False)
    quantity = models.BooleanField(default=False)
    technical_assistance = models.BooleanField(default=False)
    post_sale_service = models.BooleanField(default=False)
    sc_other = models.BooleanField(default=False)
    sc_other_description = models.CharField(max_length=200, blank=True, null=True)
    #7.Specific storing, manipulation or transport Condition
    ssmtc = models.BooleanField(default=False)
    ssmtc_description = models.CharField(max_length=200, blank=True, null=True)
    #8.New materials or providers
    nmp = models.BooleanField(default=False)
    nmp_description = models.CharField(max_length=200, blank=True, null=True)
    #9.National/International norms
    norms = models.BooleanField(default=False)
    iso = models.BooleanField(default=False)
    gazette = models.BooleanField(default=False)
    norms_other = models.BooleanField(default=False) #change to False
    norms_description = models.CharField(max_length=200, blank=True, null=True)
    #Internal elements---------------------------------->
    #1.Involved Process
    mounting = models.BooleanField(default=False)
    printing = models.BooleanField(default=False)
    lamination = models.BooleanField(default=False)
    covering = models.BooleanField(default=False)
    cutting = models.BooleanField(default=False)
    reaming = models.BooleanField(default=False)
    bagging = models.BooleanField(default=False)
    #2.Tech Inversion Requirement
    tech_inv = models.BooleanField(default=False)
    tech_inv_description = models.CharField(max_length=200, blank=True, null=True)
    #3.Human Resource Requirement
    hr = models.BooleanField(default=False)
    hr_description = models.CharField(max_length=200, blank=True, null=True)
    #4.similar products
    similar_products = models.BooleanField(default=False)
    op = models.CharField(max_length=9, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    product_client = models.ForeignKey("home.Client", verbose_name=("Clientes"), related_name="product_client", blank=True, on_delete=models.RESTRICT, null=True)
    #Product Preservation Elements---------------------------------->
    #1.Ambiental conditions
    ambiental = models.BooleanField(default=False)
    ambiental_description = models.CharField(max_length=200, blank=True, null=True)
    #2.Potential Failure
    failure = models.BooleanField(default=False)
    failure_description = models.CharField(max_length=200, blank=True, null=True)
    #3.Fail consequence
    fail_consequence = models.CharField(max_length=200, blank=True, null=True)
    #end
    observation = QuillField(blank=True, null=True)

    sales_test_request = models.OneToOneField('sales.SalesTestRequest', on_delete=models.SET_NULL, null=True, blank=True)

    elaborator = models.CharField(max_length=100, blank=False, null=True)
    reviewer = models.CharField(max_length=100, blank=True, null=True)
    
    documents = models.ManyToManyField(Document, blank=True)

    def delete(self, *args, **kwargs):
        # Delete all related Document objects
        for document in self.documents.all():
            document.delete()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = ("Elementos de entrada para el diseño y desarrollo")
        verbose_name_plural = ("Elementos de entrada para diseños y desarrollos")

    def __str__(self):
        return f'{self.product} - {self.date}'
    @property
    def test_request(self):
        return TestRequest.objects.get(entry_element=self) #type:ignore
    
    @property
    def has_test_request(self):
        return TestRequest.objects.filter(entry_element=self).exists()
    
class ExitElement(models.Model):
    ACC_OPT=(
        ('apr', 'Aprobado'),
        ('reg', 'Regular'),
        ('def', 'Deficiente'),
        ('noc', 'No cumple'),
        ('noa', 'No aplica'),
    )

    EVA_OPT = ACC_OPT + (('eva', 'En evaluacion'),)

    test_request = models.OneToOneField("essays.TestRequest", verbose_name=("Solicitud de prueba"), related_name="exit_element", blank=True, on_delete=models.RESTRICT, null=True)
    #client comes from TestRequest
    #PR comes from TestRequest production_order
    #product comes from TestRequest

    #acomplished entry elements
    dimensions = models.BooleanField(default=False)
    technical_specs = models.BooleanField(default=False)
    delivery_time = models.BooleanField(default=False)
    ae_other = models.BooleanField(default=False)
    ae_other_description = models.CharField(max_length=200, blank=True, null=True)

    functionallity_and_performance = models.TextField(default='', blank=True, null=True)

    replicavility = models.BooleanField(default=False)
    replicavility_description = models.CharField(max_length=200, blank=True, null=True)

    #accept criteria
    lab_analysis = models.CharField(max_length=3, choices=ACC_OPT, blank=False, null=True)
    machinability = models.CharField(max_length=3, choices=ACC_OPT, blank=False, null=True)
    handling = models.CharField(max_length=3, choices=ACC_OPT, blank=False, null=True)
    shelf_life = models.CharField(max_length=3, choices=EVA_OPT, blank=False, null=True)
    shelf_life_date = models.DateField(null=True, blank=True)
    delivery = models.CharField(max_length=3, choices=ACC_OPT, blank=False, null=True)
    storage = models.CharField(max_length=3, choices=ACC_OPT, blank=False, null=True)
    technical_assistance = models.CharField(max_length=3, choices=ACC_OPT, blank=False, null=True)
    after_sales_service = models.CharField(max_length=3, choices=ACC_OPT, blank=False, null=True)
    
    failure = models.BooleanField(default=False)
    failure_description = models.CharField(max_length=200, blank=True, null=True)
    failure_consequence = models.CharField(max_length=200, blank=True, null=True)

    guarantee = models.BooleanField(default=False)
    guarantee_description = models.CharField(max_length=200, blank=True, null=True)

    elaborator = models.CharField(max_length=100, blank=False, null=True)
    reviewer = models.CharField(max_length=100, blank=True, null=True)

    observation = QuillField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)

    documents = models.ManyToManyField(Document, blank=True)

    def delete(self, *args, **kwargs):
        # Delete all related Document objects
        for document in self.documents.all():
            document.delete()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = ("Elementos de salida del diseño y desarrollo")
        verbose_name_plural = ("Elementos de salida del diseño y desarrollo")
    
class TestRequest (models.Model):
    ORG_OPT=(
        ('new', 'Nueva Estructura'),
        ('upd', 'Cambio de Estructura'),
        ('int', 'Prueba Interna'),
        ('mat', 'Evaluación de Materia Prima / Proveedor'),
    )
    CPN_OPT=(
        ('mcl', 'Morrocel'),
        ('crx', 'Curex'),
    )    
    COR_OPT=(
        ('3','3"'),
        ('6','6"')
    )
    UNT_OPT=(
        ('mm','mm'),
        ('cm','cm'),
        ('in','in'),
        ('m','m'),
    )
    UN2_OPT=(
        ('kg','kg'),
        ('m','m'),
        ('m²','m²'),
    )
    UN3_OPT=(
        ('mm','mm'),
        ('cm','cm'),
        ('in','in'),
    )
    DIA_OPT=(
        ('kg','kg'),
        ('mm','mm'),
        ('cm','cm'),
        ('m','m'),
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
    PTC_OPT=(
        ('l', 'Fotocelda lado izquierdo'),
        ('r', 'Fotocelda lado derecho'),
        ('b', 'Fotocelda ambos lados'),
    )

    entry_element = models.OneToOneField('essays.EntryElement', related_name='entry_element', blank=True, on_delete=models.CASCADE, null=True)

    touched = models.BooleanField(default=False)

    number = models.CharField(max_length=9, validators=[RegexValidator(r'^[0-9]{2}[-][0-9]{6}$')], blank=True, null=True)#request
    date = models.DateField(null=True, blank=True)

    production_order = models.CharField(max_length=7, blank=True, null=True)

    company = models.CharField(max_length=3, choices = CPN_OPT, blank=True, null=True)
    origin = models.CharField(max_length=3, choices = ORG_OPT, blank=False, null=True)
    
    check_test_client = models.BooleanField(default=False)
    test_client = models.CharField(max_length=100, blank=True, null=True)
    client = models.ForeignKey("home.Client", verbose_name=("Clientes"), blank=True, on_delete=models.RESTRICT, null=True)

    art_number = models.CharField(max_length=8, blank=True, null=True)
    art_date = models.DateField(blank=True, null=True)

    product = models.CharField(max_length=100, blank=False, null=True)
    design = models.CharField(max_length=100, blank=True, null=True)
    
    #_TestStructure

    print_selector = models.BooleanField(default=False)

    lamination_process = QuillField(blank=False, null=True)
    
    printer = models.ForeignKey('essays.Printer', on_delete=models.RESTRICT, blank=True, null=True)

    surface_selector = models.BooleanField(default=False)
    reverse_selector = models.BooleanField(default=True)
    sindex = models.IntegerField(default=-2)
    sustrate_width = models.IntegerField(validators=[int_list_validator(allow_negative=False)], blank=True, null=True)
    print_width = models.CharField(max_length=30, blank=True, null=True)
    print_width_unit = models.CharField(max_length=3, choices=UN3_OPT, blank=True, null=True)

    colors =  models.CharField(max_length=200, blank=True, null=True)

    #lamination_selector = models.BooleanField(default=False)
    #_Lamination

    #dimensions
    dist_boder_cell_material = models.CharField(max_length=30, blank=True, null=True)
    repetition = models.CharField(max_length=30, blank=True, null=True)
    repetition_unit = models.CharField(max_length=3, choices=UN3_OPT, blank=True, null=True)
    width_photo = models.IntegerField(validators=[int_list_validator(allow_negative=False)], blank=True, null=True)
    lenght_photo = models.IntegerField(validators=[int_list_validator(allow_negative=False)], blank=True, null=True)
    unit_photo = models.CharField(max_length=3, choices=UN3_OPT, blank=True, null=True)

    #bobbin
    check_bobbin = models.BooleanField(default=False)	
    width_bobbin = models.CharField(max_length=30, blank=True, null=True)#cut_width
    width_bobbin_unit = models.CharField(max_length=3, choices=UN3_OPT, blank=True, null=True)
    develop = models.CharField(max_length=30, blank=True, null=True)
    develop_unit = models.CharField(max_length=3, choices=UN3_OPT, blank=True, null=True)
    core_dia_bobbin = models.CharField(max_length=1, choices = COR_OPT, blank=True, null=True)
    exterior_dia_bobbin = models.CharField(max_length=30, blank=True, null=True)
    exterior_dia_bobbin_unit = models.CharField(max_length=3, choices=DIA_OPT, blank=True, null=True)
    winding = models.CharField(max_length=1, choices = WIN_OPT, blank=True, null=True)#client_winding
    photocell_side = models.CharField(max_length=1, choices = PTC_OPT, blank=True, null=True)#client_winding
    winding_description = models.CharField(max_length=100, blank=True, null=True)

    #ream
    check_ream = models.BooleanField(default=False)	
    width_ream = models.CharField(max_length=30, blank=True, null=True)
    lenght_ream = models.CharField(max_length=30, blank=True, null=True)
    weight_ream = models.CharField(max_length=30, blank=True, null=True)

    #production
    quantity = models.IntegerField(validators=[int_list_validator(allow_negative=False)], null=True)
    unit = models.CharField(max_length=3, choices=UN2_OPT, blank=False, null=True)
    tolerance = models.IntegerField(validators=[MinValueValidator(0.0), MaxValueValidator(100.0)], default=10, null=True)

    observation = QuillField(blank=True, null=True)

    packaging = models.CharField(max_length=100, blank=True, null=True)
    tie_color = models.CharField(max_length=100, blank=True, null=True)

    elaborator = models.CharField(max_length=100, blank=False, null=True)
    applicant = models.CharField(max_length=100, blank=True, null=True)
    reviewer = models.CharField(max_length=100, blank=True, null=True)

    #checks
    pre_print = models.BooleanField(default=False)		
    colorimetry = models.BooleanField(default=False)	
    plan_crx = models.BooleanField(default=False)		
    plan_mcl = models.BooleanField(default=False)		
    logistics = models.BooleanField(default=False)		
    quality = models.BooleanField(default=False)

    archived = models.BooleanField(default=False)
    archived_time = models.DateTimeField(blank=True, null=True)

    closed = models.BooleanField(default=False)
    closed_time = models.DateTimeField(blank=True, null=True)

    deleted = models.BooleanField(default=False, blank=True, null=True)
    deleted_by = models.CharField(max_length=30, blank=True, null=True)
    deleted_time = models.DateTimeField(blank=True, null=True)
    deleted_reason = models.TextField(default='', blank=True, null=True)

    history = HistoricalRecords()
    
    def get_technicalspecs(self):
        try:
            return self.technicalspecs #type: ignore
        except ObjectDoesNotExist:
            return None

    @property
    def signed_techspecs(self):
        if self.get_technicalspecs():
            return bool(self.technicalspecs.boss)#type:ignore
        return False
    
    @property
    def status(self):
        statuses = {}
        printer_boot = PrinterBoot.objects.filter(test_request__pk=self.id).last()#type:ignore
        laminator_boot = LaminatorBoot.objects.filter(test_request__pk=self.id).last()#type:ignore
        cutter_boot = CutterBoot.objects.filter(test_request__pk=self.id).last()#type:ignore

        latest_boot = laminator_boot or printer_boot
        if not self.reviewer:
            statuses['code'] = 'not_reviewed'
            statuses['message'] = 'Pendiente por revisión de IDAT'
            statuses['color'] = 'danger'
            statuses['icon'] = 'draw'
            statuses['set'] = 'gmi'
        elif latest_boot:
            
            if laminator_boot:
                reports = TestFile.objects.filter(boot_l__id=latest_boot.pk)
            else:
                reports = TestFile.objects.filter(boot_p__id=latest_boot.pk)
            latest_report = reports.last()

            if latest_report:
                if not latest_report.boss or not latest_report.idat:
                    
                    reviewer = 'IDAT' if not latest_report.idat else 'ASCA'
                    code = 'last_report_one_review'
                    color = 'warning'
                    if not latest_report.boss and not latest_report.idat:
                        reviewer = 'IDAT y ASCA'
                        color = 'danger'
                        code = 'last_report_not_reviewed'
                    statuses['code'] = code
                    statuses['message'] = f'Último reporte pendiente por revisión de {reviewer}'
                    statuses['color'] = color
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
                        statuses['message'] = 'Especificacioens técnicas pendientes por revisión'
                        statuses['icon'] = 'unknown_document'
                        statuses['set'] = 'gmi'
                else:
                    statuses['code'] = 'not_signed_techspecs'
                    statuses['message'] = 'Especificacioens técnicas pendientes por revisión'
                    statuses['icon'] = 'unknown_document'
                    statuses['set'] = 'gmi'
            else:
                statuses['code'] = 'no_last_report'
                statuses['message'] = 'Último arranque sin reporte'
                statuses['icon'] = 'file-medical'
                statuses['set'] = 'fas'
        else:
            if self.touched:
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
        verbose_name = 'Solicitud de Prueba'
        verbose_name_plural = 'Solicitudes de Prueba'
        permissions = [
            (
                "view_working_testrequest",
                "Puede firmar una solicitud de prueba cómo revisada"
            ),
            (
                "sign_testrequest",
                "Puede firmar una solicitud de prueba cómo revisada"
            ),
            (
                "view_archived_testrequest",
                "Puede ver el archivo de solicitudes de prueba"
            ),
            (
                "archive_testrequest",
                "Puede archivar una solicitud de prueba"
            ),
            (
                "unarchive_testrequest",
                "Puede desarchivar una solicitud de prueba"
            ),
            (
                "view_deleted_testrequest",
                "Puede ver la papelera de solicitudes de prueba"
            ),
            (
                "delete_true_testrequest",
                "Puede eliminar permanentemenete una solicitud de prueba"
            ),
            (
                "restore_testrequest",
                "Puede restaurar una solicitud de prueba de la papelera"
            ),
            (
                "close_testrequest",
                "Puede Cerrar Un expediente de Pruebas y enviar a IDAT"
            ),
            (
                "open_testrequest",
                "Puede Abrir Un expediente de Pruebas y enviar a IDAT"
            ),
        ]

    def __str__(self):
        return (self.product) 

class TestStructure (models.Model):
    
    test_request = models.ForeignKey('essays.TestRequest', on_delete=models.CASCADE, null=True)

    material_type = models.ForeignKey('home.MaterialType', on_delete=models.RESTRICT, blank=False, null=True)
    provider = models.ForeignKey('home.Provider', on_delete=models.RESTRICT, blank=False, null=True)
    code = models.CharField(max_length=11, blank=True, null=True)
    weight = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], null=True)
    w_counts = models.BooleanField(default=True)
    thickness = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], null=True)
    t_counts = models.BooleanField(default=True)
    description = models.CharField(max_length=100, blank=True, null=True)

    from_production = models.CharField(max_length=100, blank=True, null=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Estructura'
        verbose_name_plural = 'Estructuras'

    def __str__(self):
        return str(self.material_type)
class ArtStructure (models.Model):

    art_request = models.ForeignKey('essays.ArtRequest', on_delete=models.CASCADE, null=True)

    material_type = models.ForeignKey('home.MaterialType', on_delete=models.RESTRICT, blank=False, null=True)
    provider = models.ForeignKey('home.Provider', on_delete=models.RESTRICT, blank=False, null=True)
    code = models.CharField(max_length=11, blank=True, null=True)
    weight = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], null=True)
    w_counts = models.BooleanField(default=True)
    thickness = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], null=True)
    t_counts = models.BooleanField(default=True)
    description = models.CharField(max_length=100, blank=True, null=True)

    from_production = models.CharField(max_length=100, blank=True, null=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Estructura'
        verbose_name_plural = 'Estructuras'

    def __str__(self):
        return str(self.material_type)

class PrinterBoot (models.Model):
    #Parent----------------------------------------------
    test_request = models.ForeignKey('essays.TestRequest', on_delete=models.CASCADE, blank=True, null=True)
    art_request = models.ForeignKey('essays.ArtRequest', on_delete=models.CASCADE, blank=True, null=True)
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

    printer = models.ForeignKey('essays.Printer', on_delete=models.RESTRICT, blank=False, null=True)
    machine_speed = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], null=True)
    check_crown_treatment = models.BooleanField(default=False)

    #Sustrate-------------------------------------------------------------------------
    #s_index = models.IntegerField(default=0)
    #provider = models.CharField(max_length=100, blank=True, null=True)
    #sustrate_width = models.IntegerField(validators=[int_list_validator(allow_negative=False)], blank=True, null=True)
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
    PTC_OPT=(
        ('l', 'Fotocelda lado izquierdo'),
        ('r', 'Fotocelda lado derecho')
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
    photocell_side = models.CharField(max_length=1, choices = PTC_OPT, blank=True, null=True)
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

    quality_analist = models.ForeignKey('essays.QualityAnalyst', on_delete=models.SET_NULL, null=True)
    production_operator = models.ForeignKey('essays.ProductionOperator', on_delete=models.SET_NULL, null=True)

    history = HistoricalRecords()
    class Meta:
        verbose_name = 'Arranque de impresora Pruebas'
        verbose_name_plural = 'Arranques de impresoras'

class LaminatorBoot(models.Model):
    test_request = models.ForeignKey('essays.TestRequest', on_delete=models.CASCADE, blank=True, null=True)
    art_request = models.ForeignKey('essays.ArtRequest', on_delete=models.CASCADE, blank=True, null=True)
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
    laminator = models.ForeignKey('essays.Laminator', on_delete=models.RESTRICT, blank=True, null=True)
    
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
    adhesive = models.ForeignKey('home.Material', on_delete=models.RESTRICT, blank=True, null=True)
    batch = models.CharField(max_length=20, blank=True, null=True)
    formula = models.CharField(max_length=7, blank=True, null=True)
    #---------------------------------------------------------------------------

    time = models.CharField(max_length=100, blank=True, null=True)
    temp = models.IntegerField(validators=[int_list_validator(allow_negative=False)], blank=True, null=True)
    observation = QuillField(blank=True, null=True)

    quality_analist = models.ForeignKey('essays.QualityAnalyst', on_delete=models.SET_NULL, null=True)
    production_operator = models.ForeignKey('essays.ProductionOperator', on_delete=models.SET_NULL, null=True)

    history = HistoricalRecords()

    @property
    def joined_layers(self):
        layers = [layer for layer in [self.st_1, self.st_2, self.st_3, self.st_4] if layer and not layer.lower().startswith('adhe')]
        return ' + '.join(layers)

    class Meta:
        verbose_name = ("Arranque de Laminadora")
        verbose_name_plural = ("Arranques de Laminadora")

    def __str__(self):
        if self.test_request:
            return f'PR-{self.test_request.production_order} {self.test_request} - LAM paso: {self.step}'#type:ignore
        elif self.art_request:
            return f'AR-{self.art_request.production_order} {self.art_request} - LAM paso: {self.step}'#type:ignore
        else:
            return f'LAM paso: {self.step}'
    
class LaminationEssay(models.Model):

    laminator_boot = models.ForeignKey('essays.LaminatorBoot', on_delete=models.CASCADE, blank=True, null=True)
    essay = models.ForeignKey('home.Essay', on_delete=models.RESTRICT, blank=False, null=True)

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
        verbose_name = ("Análisis de laminacion")
        verbose_name_plural = ("Análisis de laminacion")

    def __str__(self):
        if self.essay.unit == None:#type:ignore
            return f'ME-{self.essay.method} - {self.essay.name}' #type:ignore
        else:
            return f'ME-{self.essay.method} - {self.essay.name} - {self.essay.unit.symbol}' #type:ignore

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
    COR_OPT=(
        ('3','3"'),
        ('6','6"')
    )
    test_request = models.ForeignKey('essays.TestRequest', on_delete=models.CASCADE, blank=True, null=True)
    art_request = models.ForeignKey('essays.ArtRequest', on_delete=models.CASCADE, blank=True, null=True)
    #format = models.ForeignKey('home.Format', on_delete=models.RESTRICT, blank=True, null=True)
    
    machine = models.ForeignKey('essays.Cutter', on_delete=models.RESTRICT, null=True)
    rewinder = models.ForeignKey('essays.Rewinder', on_delete=models.RESTRICT, blank=True, null=True)

    date_time = models.DateTimeField(null=True)
    turn = models.CharField(max_length=3, choices = TRN_OPT, blank=False, null=True)

    production_order = models.CharField(max_length=7, blank=True, null=True)
    #Product = models
    #Client = models
    #gp_code = models.CharField(max_length=13, validators=[MinLengthValidator(2)], null=True)
    #Gramaje = models
    #Request = models
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
    #Spec Core core_dia_bobbin from TR
    core = models.CharField(max_length=2, choices = COR_OPT, blank=True, null=True)
    #Spec Dia. Ext. exterior_dia_bobbin from TR
    exterior_dia = models.CharField(max_length=60, blank=False, null=True)
    print_spec = models.CharField(max_length=60, blank=True, null=True)
    print = models.CharField(max_length=60, blank=True, null=True)
    #Spec winding from TR
    #Spec winding_description from TR
    winding_position = models.CharField(max_length=60, blank=True, null=True)
    #Spec dist_boder_cell_material from TR
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

    quality_analist = models.ForeignKey('essays.QualityAnalyst', on_delete=models.SET_NULL, null=True)
    production_operator = models.ForeignKey('essays.ProductionOperator', on_delete=models.SET_NULL, null=True)

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
    
    boot_p = models.ForeignKey("essays.PrinterBoot", blank=True, on_delete=models.CASCADE, null=True)
    boot_l = models.ForeignKey("essays.LaminatorBoot", blank=True, on_delete=models.CASCADE, null=True)
    boot_c = models.ForeignKey("essays.CutterBoot", blank=True, on_delete=models.CASCADE, null=True)

    type = models.CharField(max_length=3, choices = TFT_OPT, blank=False, null=True)
    
    turn = models.CharField(max_length=3, choices = TRN_OPT, blank=False, null=True)
    date = models.DateField(null=True)
    
    quality_analist = models.ForeignKey('essays.QualityAnalyst', on_delete=models.SET_NULL, null=True)
    production_operator = models.ForeignKey('essays.ProductionOperator', on_delete=models.SET_NULL, null=True)

    observation = QuillField(blank=True, null=True)

    supervisor = models.CharField(max_length=30, blank=True, null=True)
    boss = models.CharField(max_length=30, blank=True, null=True)
    idat = models.CharField(max_length=30, blank=True, null=True)
    
    date_created = models.DateTimeField(null=True, auto_now_add=True)
    history = HistoricalRecords()
    class Meta:
        verbose_name = ("Reporte de Control de Calidad")
        verbose_name_plural = ("Reportes de Control de Calidad")
        permissions = [
            (
                "boss_sign_testfile",
                "Puede firmar un reporte cómo revisado por jefe"
            ),
            (
                "supv_sign_testfile",
                "Puede firmar un reporte cómo revisado por supervisor"
            ),
            (
                "idat_sign_testfile",
                "Puede firmar un reporte cómo revisado por IDAT"
            ),
            (
                "export_boot",
                "Puede exportar un arranque"
            ),
        ]

    def __str__(self):

        name = f'report - {self.boot_l}'
        if self.boot_p:
            name = f'report - {self.boot_p}'
        return name
    
    def get_ordered_essays(self):
       return self.testfileessay_set.order_by('essay__priority')#type:ignore
    
    @property
    def boot(self):
        boot = self.boot_l
        if self.boot_p:
            boot = self.boot_p
        return boot
    
class TestFileEssay(models.Model):
    test_file = models.ForeignKey('essays.TestFile', on_delete=models.CASCADE, null=True)

    essay = models.ForeignKey('home.Essay', on_delete=models.RESTRICT, blank=False, null=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = ("Ensayos de Reporte de Control de Calidad")
        verbose_name_plural = ("Ensayos de Reportes de Control de Calidad")

    @property
    def average(self):
        results = self.testfileessayresult_set.filter(Q(result_p__isnull=False)|Q(check_a=True)|Q(check_b=True)|Q(check_c=True)) #type:ignore
        average = results.aggregate(Avg('result_p'))['result_p__avg']

        checks = [result.check_p for result in results]
        valid_checks = [check for check, result in zip(checks, results) if result.result_p is not None]
        check_p = sum(valid_checks) / len(valid_checks) >= 0.5 if valid_checks else False

        if average is not None or average == 0:
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
        results = self.testfileessayresult_set.exclude(result_t__isnull=True) #type:ignore
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

    essay = models.ForeignKey("essays.TestFileEssay", on_delete=models.CASCADE, null=True)
    bobbin = models.ForeignKey("essays.Bobbin", on_delete=models.CASCADE, blank=True, null=True)
 
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
        verbose_name = ("Resultados de ensayos de Reporte de Control de Calidad PR")
        verbose_name_plural = ("Resultados de ensayos de Reportes de Control de Calidad PR")

    def __str__(self):
        return str(self.pk)

class Bobbin(models.Model):
    #turn/fecha/analista
    TRN_OPT=(
        ('I', 'I'),
        ('II', 'II'),
        ('III', 'III'),
    )
    test_file = models.ForeignKey('essays.TestFile', on_delete=models.CASCADE, null=True)
    turn = models.CharField(max_length=3, choices = TRN_OPT, blank=False, null=True)
    date = models.DateField(null=True)
    quality_analist = models.ForeignKey('essays.QualityAnalyst', on_delete=models.SET_NULL, null=True)
    production_operator = models.ForeignKey('essays.ProductionOperator', on_delete=models.SET_NULL, null=True)
    
    @property
    def test_request(self):
        return self.test_file.boot.test_request #type:ignore
    class Meta:
        verbose_name = ("ID único para bobina PR")
        verbose_name_plural = ("ID único para bobinas PR")

    def __str__(self):
        return str(self.pk)

class TechnicalSpecs(models.Model):
    
    test_request = models.OneToOneField('essays.TestRequest', on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateField(null=True)
    
    observation = QuillField(blank=True, null=True)
    quality_analist = models.ForeignKey('essays.QualityAnalyst', blank=False, on_delete=models.SET_NULL, null=True)
    boss = models.CharField(max_length=30, blank=True, null=True)
    
    history = HistoricalRecords()

class ArtTechnicalSpecs(models.Model):
    
    art_request = models.OneToOneField('essays.ArtRequest', on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateField(null=True)
    
    observation = QuillField(blank=True, null=True)
    quality_analist = models.ForeignKey('essays.QualityAnalyst', blank=False, on_delete=models.SET_NULL, null=True)
    boss = models.CharField(max_length=30, blank=True, null=True)
    
   
class Annex(models.Model):
    art_request = models.ForeignKey('essays.ArtRequest', on_delete=models.CASCADE, blank=True, null=True)
    test_request = models.ForeignKey('essays.TestRequest', on_delete=models.CASCADE, blank=True, null=True)
    production_order = models.ForeignKey("production.Order", on_delete=models.CASCADE, blank=True, null=True)
    image = models.ImageField(upload_to="annex", null=True)
    identification = models.TextField(blank=False, null=True)

    class Meta:
        verbose_name = ("Anexo")
        verbose_name_plural = ("Anexos")

    def __str__(self):
        return self.image.url


class QualityAnalyst (models.Model):
    name = models.CharField(max_length=30, unique=True, null=True)
    active = models.BooleanField(default=True)
    #Add a fired Filter
    history = HistoricalRecords()
    class Meta:
        verbose_name = 'Analista ASCA'
        verbose_name_plural = 'Analistas ASCA'
        permissions = [
            (
                "view_personal",
                "Can view personal"
            ),
            (
                "add_personal",
                "Can add personal"
            ),
            (
                "change_personal",
                "Can edit personal"
            ),
            (
                "delete_personal",
                "Can delete personal"
            ),
        ]
    
    def __str__(self):
        return (self.name)

class ProductionOperator (models.Model):
    name = models.CharField(max_length=30, unique=True, null=True)
    active = models.BooleanField(default=True)
    #Add a fired Filter
    history = HistoricalRecords()
    class Meta:
        verbose_name = 'Operador de producción'
        verbose_name_plural = 'Operadores de producción'
    
    def __str__(self):
        return (self.name)

# Modelos De Arte
class ArtEntryElement(models.Model):
    #main data
    check_test_client = models.BooleanField(default=False)
    test_client = models.CharField(max_length=100, blank=True, null=True)
    client = models.ForeignKey("home.Client", verbose_name=("Clientes"), related_name="art_ee_client", blank=True, on_delete=models.RESTRICT, null=True)
    date = models.DateField(null=True)
    #External elements---------------------------------->
    #1.Client requirement
    product = models.CharField(max_length=100, blank=False, null=True)
    design = models.CharField(max_length=100, blank=True, null=True)
    #2.Client suplied elements
    samples = models.BooleanField(default=False)
    mechanichal_plans = models.BooleanField(default=False)
    technical_specs = models.BooleanField(default=False)
    art = models.BooleanField(default=False)
    ee_other = models.BooleanField(default=False)
    ee_other_description = models.CharField(max_length=200, blank=True, null=True)
    #3.Product Performance and requirements
    product_performance = QuillField(blank=True, null=True)
    #4.Service requirements
    service_requirements = models.CharField(max_length=100, blank=True, null=True)
    #5.Legal Requirements 
    cpe = models.BooleanField(default=False)
    barcode = models.BooleanField(default=False)
    nutrituonal_table = models.BooleanField(default=False)
    net_content = models.BooleanField(default=False)
    sanitary_reg = models.BooleanField(default=False)
    not_applicable = models.BooleanField(default=False)
    lr_other = models.BooleanField(default=False)
    lr_other_description = models.CharField(max_length=200, blank=True, null=True)
    #6.Service COnditions
    delivery_date = models.BooleanField(default=False)
    quantity = models.BooleanField(default=False)
    technical_assistance = models.BooleanField(default=False)
    post_sale_service = models.BooleanField(default=False)
    sc_other = models.BooleanField(default=False)
    sc_other_description = models.CharField(max_length=200, blank=True, null=True)
    #7.Specific storing, manipulation or transport Condition
    ssmtc = models.BooleanField(default=False)
    ssmtc_description = models.CharField(max_length=200, blank=True, null=True)
    #8.New materials or providers
    nmp = models.BooleanField(default=False)
    nmp_description = models.CharField(max_length=200, blank=True, null=True)
    #9.National/International norms
    norms = models.BooleanField(default=False)
    iso = models.BooleanField(default=False)
    gazette = models.BooleanField(default=False)
    norms_other = models.BooleanField(default=False) #change to False
    norms_description = models.CharField(max_length=200, blank=True, null=True)
    #Internal elements---------------------------------->
    #1.Involved Process
    mounting = models.BooleanField(default=False)
    printing = models.BooleanField(default=False)
    lamination = models.BooleanField(default=False)
    covering = models.BooleanField(default=False)
    cutting = models.BooleanField(default=False)
    reaming = models.BooleanField(default=False)
    bagging = models.BooleanField(default=False)
    #2.Tech Inversion Requirement
    tech_inv = models.BooleanField(default=False)
    tech_inv_description = models.CharField(max_length=200, blank=True, null=True)
    #3.Human Resource Requirement
    hr = models.BooleanField(default=False)
    hr_description = models.CharField(max_length=200, blank=True, null=True)
    #4.similar products
    similar_products = models.BooleanField(default=False)
    op = models.CharField(max_length=9, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    product_client = models.ForeignKey("home.Client", verbose_name=("Clientes"), related_name="art_product_client", blank=True, on_delete=models.RESTRICT, null=True)
    #Product Preservation Elements---------------------------------->
    #1.Ambiental conditions
    ambiental = models.BooleanField(default=False)
    ambiental_description = models.CharField(max_length=200, blank=True, null=True)
    #2.Potential Failure
    failure = models.BooleanField(default=False)
    failure_description = models.CharField(max_length=200, blank=True, null=True)
    #3.Fail consequence
    fail_consequence = models.CharField(max_length=200, blank=True, null=True)
    #end
    observation = QuillField(blank=True, null=True)

    sales_test_request = models.OneToOneField('sales.SalesTestRequest', on_delete=models.SET_NULL, null=True, blank=True)

    elaborator = models.CharField(max_length=100, blank=False, null=True)
    reviewer = models.CharField(max_length=100, blank=True, null=True)
    
    documents = models.ManyToManyField(Document, blank=True)

    def delete(self, *args, **kwargs):
        # Delete all related Document objects
        for document in self.documents.all():
            document.delete()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = ("Elementos de entrada para el diseño y desarrollo de arte")
        verbose_name_plural = ("Elementos de entrada para diseños y desarrollos de arte")

    def __str__(self):
        return f'{self.product} - {self.date}'

    @property
    def art_request(self):
        from .models import ArtRequest
        return ArtRequest.objects.get(entry_element=self) #type:ignore

    @property
    def has_art_request(self):
        from .models import ArtRequest
        return ArtRequest.objects.filter(entry_element=self).exists()

class ArtRequest(models.Model):
    ORG_OPT = TestRequest.ORG_OPT
    CPN_OPT = TestRequest.CPN_OPT
    COR_OPT = TestRequest.COR_OPT
    UNT_OPT = TestRequest.UNT_OPT
    UN2_OPT = TestRequest.UN2_OPT
    UN3_OPT = TestRequest.UN3_OPT
    DIA_OPT = TestRequest.DIA_OPT
    WIN_OPT = TestRequest.WIN_OPT
    PTC_OPT = TestRequest.PTC_OPT

    entry_element = models.OneToOneField('essays.ArtEntryElement', related_name='art_entry_element', blank=True, on_delete=models.CASCADE, null=True)

    touched = models.BooleanField(default=False)

    number = models.CharField(max_length=9, validators=[RegexValidator(r'^[0-9]{2}[-][0-9]{6}$')], blank=True, null=True)
    date = models.DateField(null=True, blank=True)

    production_order = models.CharField(max_length=7, blank=True, null=True)

    company = models.CharField(max_length=3, choices=CPN_OPT, blank=True, null=True)
    origin = models.CharField(max_length=3, choices=ORG_OPT, blank=False, null=True)

    check_test_client = models.BooleanField(default=False)
    test_client = models.CharField(max_length=100, blank=True, null=True)
    client = models.ForeignKey("home.Client", verbose_name=("Clientes"), blank=True, on_delete=models.RESTRICT, null=True)

    art_number = models.CharField(max_length=8, blank=True, null=True)
    art_date = models.DateField(blank=True, null=True)

    product = models.CharField(max_length=100, blank=False, null=True)
    design = models.CharField(max_length=100, blank=True, null=True)

    print_selector = models.BooleanField(default=False)
    lamination_process = QuillField(blank=False, null=True)

    printer = models.ForeignKey('essays.Printer', on_delete=models.RESTRICT, blank=True, null=True)

    surface_selector = models.BooleanField(default=False)
    reverse_selector = models.BooleanField(default=True)
    sindex = models.IntegerField(default=-2)
    sustrate_width = models.IntegerField(validators=[int_list_validator(allow_negative=False)], blank=True, null=True)
    print_width = models.CharField(max_length=30, blank=True, null=True)
    print_width_unit = models.CharField(max_length=3, choices=UN3_OPT, blank=True, null=True)

    colors = models.CharField(max_length=200, blank=True, null=True)

    dist_boder_cell_material = models.CharField(max_length=30, blank=True, null=True)
    repetition = models.CharField(max_length=30, blank=True, null=True)
    repetition_unit = models.CharField(max_length=3, choices=UN3_OPT, blank=True, null=True)
    width_photo = models.IntegerField(validators=[int_list_validator(allow_negative=False)], blank=True, null=True)
    lenght_photo = models.IntegerField(validators=[int_list_validator(allow_negative=False)], blank=True, null=True)
    unit_photo = models.CharField(max_length=3, choices=UN3_OPT, blank=True, null=True)

    check_bobbin = models.BooleanField(default=False)	
    width_bobbin = models.CharField(max_length=30, blank=True, null=True)#cut_width
    width_bobbin_unit = models.CharField(max_length=3, choices=UN3_OPT, blank=True, null=True)
    develop = models.CharField(max_length=30, blank=True, null=True)
    develop_unit = models.CharField(max_length=3, choices=UN3_OPT, blank=True, null=True)
    core_dia_bobbin = models.CharField(max_length=1, choices = COR_OPT, blank=True, null=True)
    exterior_dia_bobbin = models.CharField(max_length=30, blank=True, null=True)
    exterior_dia_bobbin_unit = models.CharField(max_length=3, choices=DIA_OPT, blank=True, null=True)
    winding = models.CharField(max_length=1, choices = WIN_OPT, blank=True, null=True)
    photocell_side = models.CharField(max_length=1, choices = PTC_OPT, blank=True, null=True)
    winding_description = models.CharField(max_length=100, blank=True, null=True)

    check_ream = models.BooleanField(default=False)	
    width_ream = models.CharField(max_length=30, blank=True, null=True)
    lenght_ream = models.CharField(max_length=30, blank=True, null=True)
    weight_ream = models.CharField(max_length=30, blank=True, null=True)

    quantity = models.IntegerField(validators=[int_list_validator(allow_negative=False)], null=True)
    unit = models.CharField(max_length=3, choices=UN2_OPT, blank=False, null=True)
    tolerance = models.IntegerField(validators=[MinValueValidator(0.0), MaxValueValidator(100.0)], default=10, null=True)

    observation = QuillField(blank=True, null=True)

    packaging = models.CharField(max_length=100, blank=True, null=True)
    tie_color = models.CharField(max_length=100, blank=True, null=True)

    elaborator = models.CharField(max_length=100, blank=False, null=True)
    applicant = models.CharField(max_length=100, blank=True, null=True)
    reviewer = models.CharField(max_length=100, blank=True, null=True)

    #checks
    pre_print = models.BooleanField(default=False)		
    colorimetry = models.BooleanField(default=False)	
    plan_crx = models.BooleanField(default=False)		
    plan_mcl = models.BooleanField(default=False)		
    logistics = models.BooleanField(default=False)		
    quality = models.BooleanField(default=False)

    archived = models.BooleanField(default=False)
    archived_time = models.DateTimeField(blank=True, null=True)

    closed = models.BooleanField(default=False)
    closed_time = models.DateTimeField(blank=True, null=True)

    deleted = models.BooleanField(default=False, blank=True, null=True)
    deleted_by = models.CharField(max_length=30, blank=True, null=True)
    deleted_time = models.DateTimeField(blank=True, null=True)
    deleted_reason = models.TextField(default='', blank=True, null=True)

    history = HistoricalRecords()

    def get_technicalspecs(self):
        try:
            return self.arttechnicalspecs #type: ignore
        except ObjectDoesNotExist:
            return None

    @property
    def signed_techspecs(self):
        if self.get_technicalspecs():
            return bool(self.arttechnicalspecs.boss)#type:ignore
        return False

    @property
    def status(self):
        statuses = {}
        printer_boot = PrinterBoot.objects.filter(art_request__pk=self.id).last()
        laminator_boot = LaminatorBoot.objects.filter(art_request__pk=self.id).last()
        cutter_boot = CutterBoot.objects.filter(art_request__pk=self.id).last()

        latest_boot = laminator_boot or printer_boot
        if not self.reviewer:
            statuses['code'] = 'not_reviewed'
            statuses['message'] = 'Pendiente por revisión de IDAT'
            statuses['color'] = 'danger'
            statuses['icon'] = 'draw'
            statuses['set'] = 'gmi'
        elif latest_boot:
            
            if laminator_boot:
                reports = TestFile.objects.filter(boot_l__id=latest_boot.pk)
            else:
                reports = TestFile.objects.filter(boot_p__id=latest_boot.pk)
            latest_report = reports.last()

            if latest_report:
                if not latest_report.boss or not latest_report.idat:
                    
                    reviewer = 'IDAT' if not latest_report.idat else 'ASCA'
                    code = 'last_report_one_review'
                    color = 'warning'
                    if not latest_report.boss and not latest_report.idat:
                        reviewer = 'IDAT y ASCA'
                        color = 'danger'
                        code = 'last_report_not_reviewed'
                    statuses['code'] = code
                    statuses['message'] = f'Último reporte pendiente por revisión de {reviewer}'
                    statuses['color'] = color
                    statuses['icon'] = 'edit_document'
                    statuses['set'] = 'gmi'
                elif self.get_technicalspecs(): # type: ignore
                    if self.arttechnicalspecs.boss:  # type: ignore
                        statuses['code'] = 'closed'
                        statuses['message'] = 'Expediente Completo'
                        statuses['color'] = 'success'
                        statuses['icon'] = 'checklist'
                        statuses['set'] = 'gmi'
                    else:
                        statuses['code'] = 'no_techspecs'
                        statuses['message'] = 'Especificacioens técnicas pendientes por revisión'
                        statuses['icon'] = 'unknown_document'
                        statuses['set'] = 'gmi'
                else:
                    statuses['code'] = 'not_signed_techspecs'
                    statuses['message'] = 'Especificacioens técnicas pendientes por revisión'
                    statuses['icon'] = 'unknown_document'
                    statuses['set'] = 'gmi'
            else:
                statuses['code'] = 'no_last_report'
                statuses['message'] = 'Último arranque sin reporte'
                statuses['icon'] = 'file-medical'
                statuses['set'] = 'fas'
        else:
            if self.touched:
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
        verbose_name = 'Solicitud de Arte'
        verbose_name_plural = 'Solicitudes de Arte'
        permissions = [
            (
                "view_working_artrequest",
                "Puede firmar una solicitud de arte cómo revisada"
            ),
            (
                "sign_artrequest",
                "Puede firmar una solicitud de arte cómo revisada"
            ),
            (
                "view_archived_artrequest",
                "Puede ver el archivo de solicitudes de arte"
            ),
            (
                "archive_artrequest",
                "Puede archivar una solicitud de arte"
            ),
            (
                "unarchive_artrequest",
                "Puede desarchivar una solicitud de arte"
            ),
            (
                "view_deleted_artrequest",
                "Puede ver la papelera de solicitudes de arte"
            ),
            (
                "delete_true_artrequest",
                "Puede eliminar permanentemenete una solicitud de arte"
            ),
            (
                "restore_artrequest",
                "Puede restaurar una solicitud de arte de la papelera"
            ),
            (
                "close_artrequest",
                "Puede Cerrar Un expediente de Arte y enviar a IDAT"
            ),
            (
                "open_artrequest",
                "Puede Abrir Un expediente de Arte y enviar a IDAT"
            ),
        ]

    def __str__(self):
        return (self.product)

class ArtExitElement(models.Model):
    ACC_OPT = (
        ('apr', 'Aprobado'),
        ('reg', 'Regular'),
        ('def', 'Deficiente'),
        ('noc', 'No cumple'),
        ('noa', 'No aplica'),
    )

    EVA_OPT = ACC_OPT + (('eva', 'En evaluación'),)

    art_request = models.OneToOneField(
        "essays.ArtRequest",
        verbose_name="Solicitud de arte",
        related_name="art_exit_element",
        blank=True,
        on_delete=models.RESTRICT,
        null=True
    )
    #client comes from ArtRequest
    #PR comes from ArtRequest production_order
    #product comes from ArtRequest

    #accomplished entry elements
    dimensions = models.BooleanField(default=False)
    technical_specs = models.BooleanField(default=False)
    delivery_time = models.BooleanField(default=False)
    ae_other = models.BooleanField(default=False)
    ae_other_description = models.CharField(max_length=200, blank=True, null=True)

    functionallity_and_performance = models.TextField(default='', blank=True, null=True)

    replicavility = models.BooleanField(default=False)
    replicavility_description = models.CharField(max_length=200, blank=True, null=True)

    #accept criteria
    lab_analysis = models.CharField(max_length=3, choices=ACC_OPT, blank=False, null=True)
    machinability = models.CharField(max_length=3, choices=ACC_OPT, blank=False, null=True)
    handling = models.CharField(max_length=3, choices=ACC_OPT, blank=False, null=True)
    shelf_life = models.CharField(max_length=3, choices=EVA_OPT, blank=False, null=True)
    shelf_life_date = models.DateField(null=True, blank=True)
    delivery = models.CharField(max_length=3, choices=ACC_OPT, blank=False, null=True)
    storage = models.CharField(max_length=3, choices=ACC_OPT, blank=False, null=True)
    technical_assistance = models.CharField(max_length=3, choices=ACC_OPT, blank=False, null=True)
    after_sales_service = models.CharField(max_length=3, choices=ACC_OPT, blank=False, null=True)

    failure = models.BooleanField(default=False)
    failure_description = models.CharField(max_length=200, blank=True, null=True)
    failure_consequence = models.CharField(max_length=200, blank=True, null=True)

    guarantee = models.BooleanField(default=False)
    guarantee_description = models.CharField(max_length=200, blank=True, null=True)

    elaborator = models.CharField(max_length=100, blank=False, null=True)
    reviewer = models.CharField(max_length=100, blank=True, null=True)

    observation = QuillField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)

    documents = models.ManyToManyField(Document, blank=True)

    def delete(self, *args, **kwargs):
        # Delete all related Document objects
        for document in self.documents.all():
            document.delete()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = "Elementos de salida del diseño y desarrollo de arte"
        verbose_name_plural = "Elementos de salida del diseño y desarrollo de arte"

    def __str__(self):
        return f'{self.art_request} - {self.elaborator}'