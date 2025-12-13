from django.db import models
from django.utils import timezone
from dairyapp.choices import MILK_CHOICES
import datetime

# Create your models here.

class Customer(models.Model):
    customer_id=models.AutoField(primary_key=True)
    customer_name=models.CharField(max_length=50)
    customer_address=models.CharField(max_length=100)
    customer_contact=models.CharField(max_length=10)


    def __str__(self):
        return self.customer_name


class Seller(models.Model):
    seller_id = models.AutoField(primary_key=True)
    seller_name = models.CharField(max_length=50, unique=True)
    seller_address = models.CharField(max_length=200, blank=True, null=True)
    seller_contact = models.CharField(max_length=20, blank=True, null=True)
    created_date = models.DateField(default=datetime.date.today)
    
    # Default rates for this seller (optional, can override per purchase)
    default_fat_rate_per_kg = models.FloatField(default=7.15, blank=True, null=True, help_text="Default Fat Rate per kg")
    default_snf_rate_per_kg = models.FloatField(default=4.55, blank=True, null=True, help_text="Default SNF Rate per kg")
    default_total_solids_per_kg = models.FloatField(default=10.0, blank=True, null=True, help_text="Default Total Solids per kg (%)")
    
    remarks = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.seller_name


class Buyer(models.Model):
    buyer_id = models.AutoField(primary_key=True)
    buyer_name = models.CharField(max_length=50, unique=True)
    buyer_address = models.CharField(max_length=200, blank=True, null=True)
    buyer_contact = models.CharField(max_length=20, blank=True, null=True)
    created_date = models.DateField(default=datetime.date.today)
    
    # Default rates for this buyer (optional, can override per sale)
    default_fat_rate_per_kg = models.FloatField(default=7.15, blank=True, null=True, help_text="Default Fat Rate per kg")
    default_snf_rate_per_kg = models.FloatField(default=4.55, blank=True, null=True, help_text="Default SNF Rate per kg")
    default_total_solids_per_kg = models.FloatField(default=10.0, blank=True, null=True, help_text="Default Total Solids per kg (%)")
    
    remarks = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.buyer_name
    
    class Meta:
        ordering = ['buyer_name']
    
    class Meta:
        ordering = ['buyer_name']


## Milk Product Units
class mProductUnit(models.Model):
    mProductUnit_id=models.AutoField(primary_key=True)
    mProductUnit_name=models.CharField(max_length=10)

    def __str__(self):
        return self.mProductUnit_name

## Milk Products
class mProduct(models.Model):
    # KILOGRAM='kg.'
    # LITER='ltr'
    # PACKET='pkt'
    #
    # MILK_PRODUCTS_UNIT_CHOICES=(
    #     (KILOGRAM,'Kilogram'),
    #     (LITER,'Liter'),
    #     (PACKET,'Packet'),
    # )

    mProduct_id=models.AutoField(primary_key=True)
    mProduct_name=models.CharField(max_length=50)
    mProduct_qtyunit = models.ForeignKey(mProductUnit,on_delete=models.CASCADE) #Product Unit has one to many relationship with mProduct
    mProduct_qty=models.FloatField(default=0) ##current stock
    #mProduct_qtyunit=models.CharField(max_length=3,choices=MILK_PRODUCTS_UNIT_CHOICES,default=LITER)  ##unit type eg. ltr, kg, ml



    def __str__(self):
        return self.mProduct_name


##milk purchase
class mPurchase(models.Model):

    mPurchase_id=models.AutoField(primary_key=True)
    seller=models.CharField(max_length=50)
    mPurchase_date=models.DateField(blank=True,null=True)
    mPurchase_product=models.CharField(max_length=15,choices=MILK_CHOICES)
    mPurchase_qty=models.FloatField(help_text="Quantity in Liters")
    
    # Summary rates (configurable, typically set per customer/month)
    fat_rate_per_kg=models.FloatField(default=7.15, help_text="Fat Rate per kg")
    snf_rate_per_kg=models.FloatField(default=4.55, help_text="SNF Rate per kg")
    total_solids_per_kg=models.FloatField(default=10.0, help_text="Total Solids per kg (%)")
    
    # Input fields
    fat=models.FloatField(null=True, blank=True, help_text="Fat percentage")
    snf=models.FloatField(null=True, blank=True, help_text="SNF percentage")
    ts=models.FloatField(null=True, blank=True, help_text="Total Solids")
    
    # Calculated fields
    fat_per_kg=models.FloatField(null=True, blank=True, help_text="Fat per kg (calculated)")
    snf_per_kg=models.FloatField(null=True, blank=True, help_text="SNF per kg (calculated)")
    rate=models.FloatField(null=True, blank=True, help_text="Rate (fat_per_kg + snf_per_kg)")
    ts_amount=models.FloatField(null=True, blank=True, help_text="TS Amount (ts * qty)")
    rate_per_ltr=models.FloatField(null=True, blank=True, help_text="Rate per liter (ts + rate)")
    
    # Legacy fields (keeping for backward compatibility)
    mPurchase_rate=models.FloatField(null=True, blank=True, help_text="Legacy rate field")
    mPurchase_total=models.FloatField(default=0, help_text="Total Amount (rate_per_ltr * qty)")
    
    # Advance tracking fields
    advance_amount=models.FloatField(default=0, help_text="Advance amount given to seller in this transaction")

    def __str__(self):
        return self.seller
    
    def save(self, *args, **kwargs):
        # Calculate all derived fields
        if self.fat is not None and self.fat_rate_per_kg is not None:
            self.fat_per_kg = self.fat * self.fat_rate_per_kg
        else:
            self.fat_per_kg = None
            
        if self.snf is not None and self.snf_rate_per_kg is not None:
            self.snf_per_kg = self.snf * self.snf_rate_per_kg
        else:
            self.snf_per_kg = None
        
        # Rate = fat_per_kg + snf_per_kg
        if self.fat_per_kg is not None and self.snf_per_kg is not None:
            self.rate = self.fat_per_kg + self.snf_per_kg
        else:
            self.rate = None
        
        # TS Amount = ts * qty
        if self.ts is not None and self.mPurchase_qty is not None:
            self.ts_amount = self.ts * self.mPurchase_qty
        else:
            self.ts_amount = None
        
        # Rate per liter = ts + rate
        if self.ts is not None and self.rate is not None:
            self.rate_per_ltr = self.ts + self.rate
        else:
            self.rate_per_ltr = None
        
        # Total Amount = rate_per_ltr * qty
        if self.rate_per_ltr is not None and self.mPurchase_qty is not None:
            self.mPurchase_total = self.rate_per_ltr * self.mPurchase_qty
        else:
            self.mPurchase_total = 0
        
        super().save(*args, **kwargs)

## Dairy Stock Add
class mStock(models.Model):
    mStock_id=models.AutoField(primary_key=True)
    mStock_date=models.DateTimeField(default=timezone.now)
    mStock_product=models.ForeignKey(mProduct,on_delete=models.CASCADE)
    mStock_qty=models.FloatField()

    # try to access unit using mProduct.mProduct_qtyunit
    ## not sure here if it works !!
    ## check and verify it later



## milk product sell
class mProductSell(models.Model):
    mProductSell_id = models.AutoField(primary_key=True)

    buyer_name=models.CharField(max_length=50,default='TBD')
    milk_product = models.ForeignKey(mProduct, on_delete=models.CASCADE)
    mProductSell_date=models.DateField(blank=True,null=True,default=datetime.date.today)
    mProductSell_qty=models.FloatField(help_text="Quantity in Liters")
    mProductSell_qtyunit=models.CharField(max_length=10,default='TBD')
    
    # Summary rates (configurable, typically set per customer/month)
    fat_rate_per_kg=models.FloatField(default=7.15, help_text="Fat Rate per kg")
    snf_rate_per_kg=models.FloatField(default=4.55, help_text="SNF Rate per kg")
    total_solids_per_kg=models.FloatField(default=10.0, help_text="Total Solids per kg (%)")
    
    # Input fields
    fat=models.FloatField(null=True, blank=True, help_text="Fat percentage")
    snf=models.FloatField(null=True, blank=True, help_text="SNF percentage")
    ts=models.FloatField(null=True, blank=True, help_text="Total Solids")
    
    # Calculated fields
    fat_per_kg=models.FloatField(null=True, blank=True, help_text="Fat per kg (calculated)")
    snf_per_kg=models.FloatField(null=True, blank=True, help_text="SNF per kg (calculated)")
    rate=models.FloatField(null=True, blank=True, help_text="Rate (fat_per_kg + snf_per_kg)")
    ts_amount=models.FloatField(null=True, blank=True, help_text="TS Amount (ts * qty)")
    rate_per_ltr=models.FloatField(null=True, blank=True, help_text="Rate per liter (ts + rate)")
    
    # Legacy fields (keeping for backward compatibility)
    mProductSell_rate=models.FloatField(null=True, blank=True, help_text="Legacy rate field")
    mProductSell_amount=models.FloatField(default=0, help_text="Total Amount (rate_per_ltr * qty)")
    
    # Advance tracking fields
    advance_amount=models.FloatField(default=0, help_text="Advance amount received from buyer")

    def __str__(self):
        return self.buyer_name
    
    def save(self, *args, **kwargs):
        # Calculate all derived fields
        if self.fat is not None and self.fat_rate_per_kg is not None:
            self.fat_per_kg = self.fat * self.fat_rate_per_kg
        else:
            self.fat_per_kg = None
            
        if self.snf is not None and self.snf_rate_per_kg is not None:
            self.snf_per_kg = self.snf * self.snf_rate_per_kg
        else:
            self.snf_per_kg = None
        
        # Rate = fat_per_kg + snf_per_kg
        if self.fat_per_kg is not None and self.snf_per_kg is not None:
            self.rate = self.fat_per_kg + self.snf_per_kg
        else:
            self.rate = None
        
        # TS Amount = ts * qty
        if self.ts is not None and self.mProductSell_qty is not None:
            self.ts_amount = self.ts * self.mProductSell_qty
        else:
            self.ts_amount = None
        
        # Rate per liter = ts + rate
        if self.ts is not None and self.rate is not None:
            self.rate_per_ltr = self.ts + self.rate
        else:
            self.rate_per_ltr = None
        
        # Total Amount = rate_per_ltr * qty
        if self.rate_per_ltr is not None and self.mProductSell_qty is not None:
            self.mProductSell_amount = self.rate_per_ltr * self.mProductSell_qty
        else:
            self.mProductSell_amount = 0
        
        super().save(*args, **kwargs)


class operationCost(models.Model):
    operationCost_id=models.AutoField(primary_key=True)
    particular=models.CharField(max_length=80)
    date=models.DateField(blank=True,null=True,default=datetime.date.today)
    qty=models.FloatField()
    rate=models.FloatField()
    amount=models.FloatField()

    def __str__(self):
        return self.particular


class test(models.Model):
    test_id=models.AutoField(primary_key=True)
    name=models.CharField(max_length=50)
    date=models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class Due(models.Model):
    CUSTOMER_DUE = 'customer'
    SUPPLIER_DUE = 'supplier'
    
    DUE_TYPE_CHOICES = (
        (CUSTOMER_DUE, 'Customer Due'),
        (SUPPLIER_DUE, 'Supplier Due'),
    )
    
    due_id = models.AutoField(primary_key=True)
    due_type = models.CharField(max_length=10, choices=DUE_TYPE_CHOICES, default=CUSTOMER_DUE)
    person_name = models.CharField(max_length=100)
    date = models.DateField(blank=True, null=True, default=datetime.date.today)
    particular = models.CharField(max_length=200, help_text="Description or reason for due")
    total_amount = models.FloatField(default=0)
    paid_amount = models.FloatField(default=0)
    balance_amount = models.FloatField(default=0)
    remarks = models.TextField(max_length=500, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        self.balance_amount = self.total_amount - self.paid_amount
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.person_name} - {self.balance_amount}"

    @property
    def is_paid(self):
        return self.balance_amount <= 0