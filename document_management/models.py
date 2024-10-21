from django.db import models
from construction.models import Loan 
from users.models import User

class DocumentType(models.Model):
    id = models.AutoField(primary_key=True)
    project_type = models.CharField(max_length=100,null=True)
    document_type = models.CharField(max_length=300, null=True)
 
 
class DocumentDetail(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=800,null=True)
    type = models.CharField(max_length=150,null=True)
    document_type = models.ForeignKey(DocumentType,on_delete=models.CASCADE,null=True)
 
    def __str__(self):
        return f"{self.name} ({self.type})"
    
class Document(models.Model):
    id = models.AutoField(primary_key=True)
    loan = models.ForeignKey(Loan, on_delete= models.CASCADE)
    document_detail = models.ForeignKey(DocumentDetail,on_delete=models.CASCADE,null=True)
    document_comment = models.CharField(max_length=300,null=True)
    file_id = models.CharField(max_length=255,null=True)
    uploaded_at = models.DateTimeField(null=True)
    status = models.CharField(max_length=100,null=True,default='Not Uploaded')
    file_name = models.CharField(max_length=100,null=True)


class Feedback(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    Document = models.ForeignKey(Document,on_delete=models.CASCADE,null=True) 
    created_at = models.DateTimeField(null=True,blank=True)