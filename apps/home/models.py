# -*- encoding: utf-8 -*-
#Copyright (c) 2022 - present, Daniel Escalona

import datetime, re, decimal
from xmlrpc.client import Boolean
from django.db import models
from email.policy import default
from django.forms import IntegerField, ModelForm
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.validators import *
from django.core.exceptions import ValidationError
from simple_history.models import HistoricalRecords
class Plan (models.Model):

    pc = models.CharField(max_length=9, validators=[RegexValidator(r'^[A-Z]\d{2}\.\d{2}(-\d{1,2})?|0{8}$'), MinLengthValidator(6)], null=True)
    revission = models.IntegerField(validators=[int_list_validator(allow_negative=False)], null=True)
    rev_date = models.DateField(null=True)

    #format = models.ForeignKey('Format', on_delete=models.RESTRICT, default=get_default_format, null=True)

    client = models.ForeignKey('Client', on_delete=models.RESTRICT, null=True)
    product = models.CharField(max_length=1000, null=True)

    gp_code = models.CharField(max_length=13, validators=[MinLengthValidator(13)], null=True)
    code = models.CharField(max_length=13,  validators=[MinLengthValidator(13)], null=True)

    continuation = models.TextField(null=True)
    dispatch_conditions = models.TextField(null=True)

    elaborator = models.CharField(max_length=100, null=True)
    reviewer = models.CharField(max_length=100, blank=True, null=True)
    s_index = models.IntegerField(default=0)
    surface_selector = models.BooleanField(default=False)
    reverse_selector = models.BooleanField(default=True)

    observation = models.TextField(default='', blank=True, null=True)
    date_created = models.DateField(null=True, auto_now_add=True)

    disincorporated = models.BooleanField(default=False)
    disicomop_by = models.CharField(max_length=30, blank=True, null=True)
    disicomop_reason = models.TextField(default='', blank=True, null=True)
    disicomop_time = models.DateTimeField(blank=True, null=True)

    archived = models.BooleanField(default=False)
    deleted_by = models.CharField(max_length=30, blank=True, null=True)
    deleted_reason = models.TextField(default='', blank=True, null=True)
    delete_time = models.DateTimeField(blank=True, null=True)

    history = HistoricalRecords()
    
    class Meta:
        verbose_name = 'Plan de Calidad'
        verbose_name_plural = 'Planes de Calidad'
        permissions = [
            (
                "sign_plan",
                "Puede firmar un plan cómo revisado"
            ),
            (
                "view_disincorporate_plan",
                "Puede ver planes de calidad desincorporados"
            ),
            (
                "disincorporate_plan",
                "Puede desincorporar un plan de calidad"
            ),
            (
                "view_archive_plan",
                "Puede ver el archivo de planes de calidad"
            ),
            (
                "archive_plan",
                "Puede archivar un plan de calidad"
            ),
            (
                "delete_archive_plan",
                "Puede eliminar un plan de calidad permanentemente"
            ),
        ]
    
    def save_no_history(self, *args, **kwargs):
        self.skip_history_when_saving = True
        try:
            ret = self.save(*args, **kwargs)
        finally:
            del self.skip_history_when_saving
        return ret

    def __str__(self):
        return str(self.product)

    @property
    def new_p(self):
        return (datetime.date.today() - self.date_created).days < 1 #type:ignore

    @property
    def company(self):
        if self.gp_code and self.gp_code.startswith("TM"):
            return "mcl"
        else:
            return "crx"
        
    def calculate_totals(self):
        wcount = 0
        tcount = 0
        if hasattr(self, '_history'):
            structure_list = Structure.history.as_of(self._history.history_date).filter(plan_id=self.id)#type: ignore
        else:
            structure_list = self.structure_set.all() #type:ignore

        wcount = sum(obj.weight for obj in structure_list if obj.w_counts)
        tcount = sum(obj.thickness for obj in structure_list if obj.t_counts)
        
        return wcount, tcount

    def calculate_average(self, count):
        return decimal.Decimal(count*0.05).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP)

    @property
    def weight_avg(self):
        wcount, _ = self.calculate_totals()
        return self.calculate_average(wcount)

    @property
    def thickness_avg(self):
        _, tcount = self.calculate_totals()
        return self.calculate_average(tcount)

    @property
    def weight(self):
        wcount, _ = self.calculate_totals()
        return wcount

    @property
    def thickness(self):
        _, tcount = self.calculate_totals()
        return tcount

    @property#unused property 
    def materials(self):
        structure_list = self.structure_set.all()#type:ignore
        materials = {
            'Tintas': {'count': 0, 'weights': []},
            'Adhesivo': {'count': 0, 'weights': []},
            'Resina': {'count': 0, 'weights': []},
            'Silicona': {'count': 0, 'weights': []},
            'Laca': {'count': 0, 'weights': []},
            'Parafina': {'count': 0, 'weights': []},
            'Barniz': {'count': 0, 'weights': []},
            'Primer': {'count': 0, 'weights': []},
            'Cera': {'count': 0, 'weights': []},
        }
        for n in structure_list:
            for material_type in materials.keys():
                if n.material_type.name.startswith(material_type): 
                    materials[material_type]['weights'].append(n.weight)
                    materials[material_type]['count'] += 1
        return materials
    
    @property
    def repetition(self):
        if hasattr(self, '_history'):
            test = Test.history.as_of(self._history.history_date).filter(Q(plan_id=self.id)&Q(essay__method="026")).first() #type: ignore
        else:
            test = Test.objects.filter(Q(plan_id=self.id)&Q(essay__method="026")).first() #type: ignore
        if test:
            return f'{test.spec}mm'
        return None
    
    @property
    def width_bobbin(self):
        if hasattr(self, '_history'):
            test = Test.history.as_of(self._history.history_date).filter(Q(plan_id=self.id)&Q(essay__method="012")).first() #type: ignore
        else:
            test = Test.objects.filter(Q(plan_id=self.id)&Q(essay__method="012")).first() #type: ignore
        if test:
            return f'{test.spec}mm'
        return None
    
    @property
    def core_dia_bobbin(self):
        if not self.dispatch_conditions:
            return None
        # Remove punctuation and split into words
        words = re.sub(r'\W+', ' ', self.dispatch_conditions).split()
        try:
            core_index = next(i for i, word in enumerate(words) if word.lower() == 'core')
        except StopIteration:
            return None
        for word in words[core_index:]:
            if word.startswith('3') or word.startswith('6'):
                return f'{int(word[0])}"'
        return "Skrt"
        
    @property
    def winding_literal(self):
        if hasattr(self, '_history'):
            test = Test.history.as_of(self._history.history_date).filter(Q(plan_id=self.id)&Q(essay__method="031")).first() #type: ignore
        else:
            test = Test.objects.filter(Q(plan_id=self.id)&Q(essay__method="031")).first() #type: ignore
        if test:
            return f'{test.spec}'
        return None

    @property
    def winding(self):
        return self.get_winding_or_description('winding')

    @property
    def winding_description(self):
        return self.get_winding_or_description('description')

    @property
    def printers(self):
        return self.get_printers(self.continuation)

    @property
    def laminators(self):
        return self.get_printers(self.continuation)
    
    @staticmethod
    def get_printers(text):
        # The names to look for
        names = ["novoflex", "olympia", "olimpia", "olimpya"]
        # This will hold the found names
        found_names = []
        # Look for each name in the text
        for name in names:
            # The pattern looks for the name (case insensitive)
            pattern = re.compile(name, re.IGNORECASE)
            match = pattern.search(text)
            if match:
                if name.lower() in ["olimpia", "olympia", "olimpya"]:
                    found_names.append("OLYMPIA")
                else:
                    found_names.append(name.upper())
        # Return the list of found names
        return found_names
    
    @staticmethod
    def get_laminators(text):
        # The names to look for
        names = ["laminex", "varicoater"]
        # This will hold the found names
        found_names = []
        # Look for each name in the text
        for name in names:
            # The pattern looks for the name (case insensitive)
            pattern = re.compile(name, re.IGNORECASE)
            match = pattern.search(text)
            if match:
                if name.lower() in ["varicoater"]:
                    found_names.append("VARICOATER LF")
                else:    
                    found_names.append(name.upper())
        # Return the list of found names
        return found_names

    def get_winding_or_description(self, return_type):
        # Get the related Test that has an Essay with method == "031"
        if hasattr(self, '_history'):
            test = Test.history.as_of(self._history.history_date).filter(Q(plan_id=self.id)&Q(essay__method="031")).first() #type: ignore
        else:
            test = Test.objects.filter(Q(plan_id=self.id)&Q(essay__method="031")).first() #type: ignore
        if test:
            # Use regular expressions to find the number and the text
            number = re.search(r'\d+', test.spec) #type: ignore
            text = re.sub(r'\d+', '', test.spec) #type: ignore

            # If a number is found, convert it to an integer
            if number:
                number = int(number.group())

            if return_type == 'winding':
                return number
            elif return_type == 'description':
                return text.strip()

        return None  # Return None if no related Test is found

class Client (models.Model):
    RIF_OPT=(
        ('MC', 'MC'),
        ('J', 'J'),
        ('V', 'V'),
        ('P', 'P'),
        ('E', 'E'),
        ('G', 'G'),
        ('C', 'C'),
    )
    name =  models.CharField(max_length=100, unique=True, blank=False, null=True)
    rif_type = models.CharField(max_length=3, choices=RIF_OPT, blank=False, null=True)
    rif_num = models.CharField(max_length=10, validators=[RegexValidator(r'^[0-9]{8}-[0-9]+$')], blank=False, null=True)
    #avatar = models.ImageField(upload_to='', height_field=None, width_field=None, blank=True, null=True, validators=[validate_image_file_extension])
    
    history = HistoricalRecords()

    @property
    def plan_count(self):
        return self.plan_set.filter(archived=False).exclude(pc='00000000').count()#type: ignore
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        unique_together = ('rif_type', 'rif_num')

    def __str__(self):
        return self.name    
class Provider (models.Model):

    name = models.CharField(max_length=100, unique=True, null=True)
    
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'

    def __str__(self):
        return self.name

class Material (models.Model):
       
    material_type = models.ForeignKey('MaterialType', on_delete=models.RESTRICT, null=True)
    provider = models.ForeignKey('Provider', on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100, blank=False, null=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Material'
        verbose_name_plural = 'Materiales'
        ordering = ['name']

    def __str__(self):
        if not self.name == self.material_type.name:#type:ignore
            return  f'{self.name} - {self.provider.name}'#type:ignore
        return self.provider.name #type:ignore

class MaterialType (models.Model):
    name = models.CharField(max_length=100, unique=True, null=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Tipo de material'
        verbose_name_plural = 'Tipos de materiales'
    def __str__(self):
        return str(self.name)

class Structure (models.Model):
    
    plan = models.ForeignKey('Plan', on_delete=models.CASCADE, null=True)
    material_type = models.ForeignKey('MaterialType', on_delete=models.RESTRICT, null=True)
    weight =  models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], null=True)
    w_counts = models.BooleanField(default=True)
    thickness = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(9999.0)], null=True)
    t_counts = models.BooleanField(default=True)
    material = models.ManyToManyField(Material)

    history = HistoricalRecords(m2m_fields=[material])

    class Meta:
        verbose_name = 'Estrucura'
        verbose_name_plural = 'Estructura'

    def __str__(self):
        return str(self.material_type)

class Essay (models.Model):
    name = models.CharField(max_length=100, null=True)
    detail = models.CharField(max_length=100, blank=True, null=True)
    method = models.CharField(max_length=3, validators=[MinLengthValidator(3), RegexValidator(r'([\d][\d][\d])')], null=True)
    unit = models.ForeignKey('home.Unit', on_delete=models.RESTRICT, blank=True, null=True)
    priority = models.CharField(max_length=4, default='9999', blank=True, null=True)
    confidential = models.BooleanField(default=False, null=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Ensayo'
        verbose_name_plural = 'Ensayos'

    def __str__(self):
        if self.unit == None:        
            return 'ME-' + self.method + ' - ' + self.name #type:ignore
        else:
            return 'ME-' + self.method + ' - ' + self.name + ' - ' + self.unit.symbol #type:ignore

class Unit (models.Model):
    
    name = models.CharField(max_length=50, null=True)
    symbol = models.CharField(max_length=20, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Unidad'
        verbose_name_plural = 'Unidades'

    def __str__(self):
        if self.name != self.symbol:
            return self.name + ' - ' + self.symbol #type:ignore
        return self.symbol

class Test (models.Model):    
    
    plan = models.ForeignKey('Plan', on_delete=models.CASCADE, null=True)
    essay = models.ForeignKey(Essay, related_name='essay', on_delete=models.RESTRICT,blank=False, null=True)
    critic = models.BooleanField(default=None)
    spec = models.CharField(max_length=50, blank=True, null=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Ensayos Realizados'
        verbose_name_plural = 'Ensayos Realizados'

    def __str__(self):
        return self.essay.name #type:ignore

class DeincorporateRequest(models.Model):

    rejected = models.BooleanField(default=False)
    review = models.ForeignKey("sales.SaleOrderReview", on_delete=models.CASCADE, null=True)
    plan = models.ForeignKey("home.Plan", related_name='deincorporate_request', on_delete=models.CASCADE)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Solicitud de Desincorporación de Plan de Calidad'
        verbose_name_plural = 'Solicitudes de Desincorpor ación de Planes de Calidad'

    def __str__(self):
        return str(self.plan.pc)