from django.db import models
from django.forms import DateTimeField
from django_quill.fields import QuillField
from simple_history.models import HistoricalRecords


class PrePrint(models.Model):

    sale_order = models.OneToOneField("sales.SaleOrder", related_name='pre_print', on_delete=models.CASCADE, null=True)

    pdf = models.BooleanField(default=False, null=True)
    pdf_date = models.DateTimeField(blank=True, null=True)

    pdf_approval = models.BooleanField(default=False, null=True)
    pdf_approval_date = models.DateTimeField(blank=True, null=True)

    pc = models.BooleanField(default=False, null=True)
    pc_date = models.DateTimeField(blank=True, null=True)

    pc_approval = models.BooleanField(default=False, null=True)
    pc_approval_date = models.DateTimeField(blank=True, null=True)

    plates = models.BooleanField(default=False, null=True)
    plates_date = models.DateTimeField(blank=True, null=True)

    @property
    def status(self):
        
        if self.sale_order.origin in ['upd', 'new']: #type:ignore
            if not self.pdf:
                statuses = {'code':'pp_pdf_check', 'message':'Pendiente por desarrollo de PDF', 'icon':'file-pdf', 'set':'fas', 'color':'danger', 'mcr':True}
            elif not self.pdf_approval:
                statuses = {'code':'pp_pdf_approval', 'message':'PDF pendiente por aprobación del cliente', 'icon':'file-pdf', 'set':'fas', 'color':'warning', 'mcr':True}
            elif not self.pc:
                statuses = {'code':'pp_pc_check', 'message':'Pendiente por desarrollo de Prueba de Color', 'icon':'palette', 'set':'gmi', 'color':'danger'}
            elif not self.pc_approval:
                statuses = {'code':'pp_pc_approval', 'message':'Prueba de Color pendiente por aprobación del cliente', 'icon':'palette', 'set':'gmi', 'color':'warning'}
            elif not self.plates:
                statuses = {'code':'pp_plate', 'message':'Pendiente por desarrollo de planchas', 'icon':'sheet-plastic', 'set':'fas', 'color':'danger'}
            else:
                statuses = {'code':'error', 'message':'Error, comuniquese con soporte', 'icon':'bug', 'set':'fas', 'color':'danger'}
        elif self.sale_order.origin == 'pro':#type:ignore
            if not self.plates:
                statuses = {'code':'plate_verify', 'message':'Pendiente por Verificación de Planchas', 'icon':'sheet-plastic', 'set':'fas', 'color':'warning'}
            else:
                statuses = {'code':'error', 'message':'Error, comuniquese con soporte', 'icon':'bug', 'set':'fas', 'color':'danger'}
        else:
            statuses = {'code':'error', 'message':'Error, comuniquese con soporte', 'icon':'bug', 'set':'fas', 'color':'danger'}
        return statuses

    @property
    def pc_rejects(self):
        return self.pc_rejects.all()#type: ignore
    @property
    def pc_reject_count(self):
        return self.pc_rejects.all().count()#type: ignore
    
    @property
    def pdf_rejects(self):
        return self.pdf_rejects.all()#type: ignore
    @property
    def pdf_reject_count(self):
        return self.pdf_rejects.all().count()#type: ignore

    class Meta:
        verbose_name = ("Estado de Pre Prensa")
        verbose_name_plural = ("Estados de Pre Prensa")
        permissions = [
            (
                "pp_pdf_check",
                "Puede enviar PDF para aprobar"
            ),
            (
                "pp_pdf_approval",
                "Puede aprobar o rechazar PDF"
            ),
            (
                "pp_pc_check",
                "Puede enviar PC para aprobar"
            ),
            (
                "pp_pc_approval",
                "Puede aprobar o rechazar PC"
            ),
            (
                "pp_plate",
                "Puede verificar Planchas"
            ),
        ]

    def __str__(self):
        return str(self.plates)

class PdfRejects(models.Model):

    status = models.ForeignKey("graphics.PrePrint", related_name="pdf_rejects", on_delete=models.CASCADE)
    date = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = ("Rechazo de PDF")
        verbose_name_plural = ("Rechazos de PDF")

    def __str__(self):
        return str(self.date)

class PCRejects(models.Model):

    status = models.ForeignKey("graphics.PrePrint", related_name="pc_rejects", on_delete=models.CASCADE)
    date = models.DateTimeField(null=True)

    class Meta:
        verbose_name = ("Rechazo de Prueba de Color")
        verbose_name_plural = ("Rechazos de Prueba de Color")

    def __str__(self):
        return str(self.date)