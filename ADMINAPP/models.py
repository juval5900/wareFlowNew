# models.py
from django.db import models
from USERAPP.models import UserRole 

class Warehouse(models.Model):
    warehouse_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    num_sectors = models.PositiveIntegerField()
    manager = models.ForeignKey(UserRole, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_warehouses')
    controller = models.ForeignKey(UserRole, on_delete=models.SET_NULL, null=True, blank=True, related_name='controlled_warehouses')

    def __str__(self):
        return self.warehouse_name