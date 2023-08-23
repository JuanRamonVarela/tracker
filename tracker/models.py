from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Categories(models.Model):
    category=models.CharField(max_length=70)
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    date=models.DateField(auto_now=True)
    active=models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('id', 'category')

    def __str__(self):
        return self.category
    
class Books(models.Model):
    book_code=models.IntegerField()
    title=models.CharField(max_length=255)
    subtitle=models.CharField(max_length=255, null=True)
    author=models.CharField(max_length=255)
    publishing_date=models.DateField()
    publisher=models.CharField(max_length=255)
    category=models.ForeignKey(Categories, on_delete=models.CASCADE)
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_reg')
    date=models.DateField(auto_now=True)
    distribution_expense=models.DecimalField(max_digits=6, decimal_places=2)
    active=models.BooleanField(default=True)