from django.db import models

# Create your models here.

class tbl_admin(models.Model):
    
    login_id = models.AutoField(primary_key=True)
    login_name = models.CharField(max_length=50)
    login_email = models.EmailField()
    login_pass = models.CharField(max_length=50)