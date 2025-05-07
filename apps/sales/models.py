# -*- encoding: utf-8 -*-
#Copyright (c) 2024 - present, Daniel Escalona

from ctypes import addressof
from decimal import Decimal
from http import client
from django.db import models
from django.forms import CharField
from django_quill.fields import QuillField
from simple_history.models import HistoricalRecords
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator, int_list_validator, MinValueValidator, MaxValueValidator, MinLengthValidator
from documents.models import Document

class SalesTestRequest(models.Model):
    DSG_OPT=(
        ('yim', 'Impreso'),
        ('nim', 'Sin Impresión'),
    )    
    CPN_OPT=(
        ('mcl', 'Morrocel'),
        ('crx', 'Curex'),
    )    
    PTY_OPT=(
        ('rev', 'Impreso Reverso'),
        ('sfc', 'Impreso Superficie'),
        ('lam', 'Laminado'),
        ('mon', 'Monocapa'),
    )    
    date = models.DateField(null=True)
    client = models.ForeignKey("home.Client", on_delete=models.RESTRICT, blank=True, null=True)
    company = models.CharField(max_length=3, choices = CPN_OPT, blank=True, null=True)
    product = models.CharField(max_length=100, blank=False, null=True)

    #client provided elements
    printed_sample = models.BooleanField(default=False, blank=True, null=True)
    mechanical_plan = models.BooleanField(default=False, blank=True, null=True)
    technichal_specs = models.BooleanField(default=False, blank=True, null=True)
    arts = models.BooleanField(default=False, blank=True, null=True)

    design = models.CharField(max_length=3, choices = DSG_OPT, blank=True, null=True)
    product_type = models.CharField(max_length=3, choices = PTY_OPT, blank=True, null=True)
    
    documents = models.ManyToManyField(Document, blank=True)

    observation = QuillField(blank=True, null=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = ("Solicitudes de Pruebas")
        verbose_name_plural = ("Solicitudes de Pruebas")

    def delete(self, *args, **kwargs):
        # Delete all related Document objects
        for document in self.documents.all():
            document.delete()
        super().delete(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.product} - {self.date}'
    
class SalesStructure(models.Model):
    
    s_test_request = models.ForeignKey('sales.SalesTestRequest', on_delete=models.CASCADE, null=True)
    material_type = models.ForeignKey('home.MaterialType', on_delete=models.RESTRICT, null=True)
    weight =  models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], null=True)
    #w_counts = models.BooleanField(default=True)
    thickness = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], null=True)
    #t_counts = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Estrucura'
        verbose_name_plural = 'Estructura'

    def __str__(self):
        return str(self.material_type)

class SaleOrder(models.Model):#PurchaseOrder - Pedido de Compra

    ORG_OPT=(        
        #('tst', 'Prueba'),
        ('pro', 'Producción'),
        ('upd', 'Cambio de Arte'),
        ('new', 'Nuevo Arte'),
    )
    
    CPN_OPT=(
        ('crx', 'Curex'),
        ('mcl', 'Morrocel'),
    )
    
    UN2_OPT=(
        ('kg','kg'),
        ('m','m'),
        ('m²','m²'),
        ('ud','ud'),
    )
    CRC_OPT=(
        ('Bs.','Bs.'),
        ('$','$'),
    )

    UN3_OPT=(
        ('mm','mm'),
        ('cm','cm'),
        ('in','in'),
    )
    BOR_OPT=(
        ('Bobina','Bobina'),
        ('Resma','Resma'),
    )

    plan = models.ForeignKey("home.Plan", on_delete=models.RESTRICT, blank=True, null=True)
    reference_date = models.DateTimeField(null=True, auto_now_add=True)
    date_created = models.DateTimeField(null=True, auto_now_add=True)

    request = models.IntegerField(validators=[int_list_validator(allow_negative=False), MinValueValidator(0), MaxValueValidator(99999999)], blank=True, null=True)#request
    number = models.CharField(max_length=15, blank=False, null=True)#request
    
    request_date = models.DateField(null=True)
    number_date = models.DateField(null=True)

    #company = models.CharField(max_length=3, choices = CPN_OPT, blank=True, null=True)
    origin = models.CharField(max_length=3, choices = ORG_OPT, blank=False, null=True)

    printer = models.ForeignKey('essays.Printer', on_delete=models.RESTRICT, blank=True, null=True)

    bob_or_ream = models.CharField(max_length=10, choices=BOR_OPT, null=True)

    width_photo = models.IntegerField(validators=[int_list_validator(allow_negative=False)], blank=True, null=True)
    lenght_photo = models.IntegerField(validators=[int_list_validator(allow_negative=False)], blank=True, null=True)
    unit_photo = models.CharField(max_length=3, choices=UN3_OPT, blank=True, null=True)

    delivery_address = models.ForeignKey('sales.DeliveryAddress', on_delete=models.RESTRICT, null=True)

    price = models.CharField(max_length=30, null=True)
    currency = models.CharField(max_length=3, choices=CRC_OPT, blank=False, null=True)
    quantity = models.IntegerField(validators=[int_list_validator(allow_negative=False)], null=True)
    unit = models.CharField(max_length=3, choices=UN2_OPT, blank=False, null=True)
    tolerance = models.IntegerField(validators=[int_list_validator(allow_negative=False)], default=10, null=True)

    observation = QuillField(blank=True, null=True)

    representative = models.ForeignKey("sales.Representative", on_delete=models.RESTRICT, null=True)
    approver = models.CharField(max_length=50, blank=True, null=True)
    elaborator = models.CharField(max_length=50, blank=True, null=True)

    pre_print_ready = models.BooleanField(default=False, blank=True, null=True)
    archived = models.BooleanField(default=False, blank=True, null=True)

    deleted = models.BooleanField(default=False, blank=True, null=True)
    deleted_by = models.CharField(max_length=30, blank=True, null=True)
    deleted_time = models.DateTimeField(blank=True, null=True)

    history = HistoricalRecords()
    
    def get_pre_print(self):
        try:
            return self.pre_print# type: ignore
        except ObjectDoesNotExist:
            return None
    @property
    def treviewed(self):
        try:
            return self.treview.approved# type: ignore
        except ObjectDoesNotExist:
            return None
        
    @property
    def pre_print(self):
        if self.get_pre_print():
            return self.pre_print
        else:
            pass
    @property
    def status(self):
        statuses = {}
        if self.pre_print_ready:
            if self.has_order:#type: ignore
                order = self.production_order.filter(deleted=False).last()#type: ignore
                statuses = order.status
                
            else:
                statuses['code'] = 'no_production_order'
                statuses['message'] = 'Sin Orden de Producción asignada'
                statuses['icon'] = 'other_admission'
        elif self.get_pre_print():#type: ignore
            statuses = self.pre_print.status#type: ignore
        else:
            statuses['set'] = 'fas'
            if self.origin in ['upd', 'new']:
                statuses['message'] = 'Pendiente por desarrollo de PDF'
                statuses['color'] = 'danger'
                statuses['code'] = 'pp_pdf_check'
                statuses['icon'] = 'file-pdf'
                statuses['mcr'] = True
            else:
                statuses['message'] = 'Pendiente por Verificación de Planchas'
                statuses['code'] = 'pp_plate'
                statuses['color'] = 'warning'
                statuses['icon'] = 'sheet-plastic'

        return statuses

    @property
    def has_order(self):
        if self.production_order.filter(deleted=False).all():#type: ignore
            return True 
        return False 
    
    @property
    def dispatched_quantity(self):
        latest_order = self.production_order.order_by('-id').first()#type: ignore
        if latest_order and hasattr(latest_order, 'technicalspecs'):
            return latest_order.technicalspecs.dispatched_quantity
        else:
            return 0

    @property
    def request_number(self):
        return f'{str(self.representative.number).zfill(2)}-{str(self.request).zfill(7)}'#type: ignore
    
    class Meta:
        verbose_name = ("Órden de Compra")
        verbose_name_plural = ("Órdenes de Compra")
        permissions = [
            (
                "view_sale_order_confidential",
                "Puede ver detalles específicos de Pedidos de compra"
            ),
            (
                "approve_sale_order",
                "Puede firmar una pedido de compra cómo aprobada"
            ),
            (
                "review_sale_order",
                "Puede firmar una pedido de compra cómo revisado"
            ),
            (
                "archive_sale_order",
                "Puede archivar una pedido de compra"
            ),
            (
                "view_archive_sale_order",
                "Puede ver el archivo pedido de compra"
            ),
            (
                "delete_deleted_sale_order",
                "Puede ver la papelera de pedidos de compra"
            ),
            (
                "restore_deleted_sale_order",
                "Puede ver la papelera de pedidos de compra"
            ),
            (
                "view_deleted_sale_order",
                "Puede ver la papelera de pedidos de compra"
            ),
        ]
    
    def __str__(self):
        return f'{self.representative}-{str(self.request).zfill(7)}'

class DeliveryDate(models.Model):
    
    sale_order = models.ForeignKey("sales.SaleOrder", on_delete=models.CASCADE, null=True)

    quantity = models.IntegerField(validators=[int_list_validator(allow_negative=False)], null=True)
    delivery_date = models.DateField(null=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = ("Quiantity")
        verbose_name_plural = ("Quiantities")
        
    def __str__(self):
        return str(self.delivery_date)
    
class Representative(models.Model):

    number = models.IntegerField(validators=[int_list_validator(allow_negative=False)], blank=False, null=True)
    name =models.CharField(max_length=20, null=True)
    
    history = HistoricalRecords()

    class Meta:
        verbose_name = ("Representate de Venta")
        verbose_name_plural = ("Representates de Ventas")

    def __str__(self):
        return str(self.number)

class DeliveryAddress(models.Model):
    client = models.ForeignKey("home.Client", on_delete=models.CASCADE)
    address = models.CharField(max_length=150, null=True)

    history = HistoricalRecords()
    
    class Meta:
        verbose_name = ("Dirección de Entrega")
        verbose_name_plural = ("Direcciones de Entrega")

    def __str__(self):
        return self.address

class SaleOrderReview(models.Model):

    sale_order = models.OneToOneField("sales.SaleOrder", related_name='treview', on_delete=models.SET_NULL, null=True)
    sale_order_name = models.CharField(max_length=100, blank=True, null=True)
    sale_order_number = models.CharField(max_length=100, blank=True, null=True)
    sale_order_date = models.CharField(max_length=100, blank=True, null=True)

    approved = models.BooleanField(default=False)
    suggested_replace = models.ForeignKey('home.Plan', on_delete=models.CASCADE, blank=True, null=True)
    deincorporate_request = models.BooleanField(default=False)
    by = models.CharField(max_length=50, null=True, blank=True)
    observation = models.TextField(max_length=500, blank=True, null=True)

    datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = ("Revisión de pedido")
        verbose_name_plural = ("Revisiones de pedidos")

    def save(self, *args, **kwargs):
        if self.sale_order:
            self.sale_order_name = f'Pedido de {self.sale_order.plan.product}'
            self.sale_order_number = f'{self.sale_order.representative}-{self.sale_order.request:07}'
            self.sale_order_date = self.sale_order.request_date
        super().save(*args, **kwargs)

    def __str__(self):
        return self.sale_order_name or 'sss'