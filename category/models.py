from django.db import models

# Create your models here.

class Category(models.Model):
    
    category_name = models.CharField(max_length=60)
    category_desc = models.CharField(max_length=50)
    category_image = models.ImageField() 
    def __str__(self):
        return self.category_name

    