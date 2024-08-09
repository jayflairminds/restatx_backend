from django.db import models
from construction.models import Loan

class Document(models.Model):
    id = models.AutoField(primary_key=True)
    loan = models.ForeignKey(Loan, on_delete= models.CASCADE)
    document_name = models.CharField(max_length=255)
    document_type = models.CharField(max_length=150)
    document_comment = models.CharField(max_length=300,null=True)
    file_id = models.CharField(max_length=255,null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)