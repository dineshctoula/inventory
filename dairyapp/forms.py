from django import forms
from .models import mProduct,mProductUnit,mPurchase, mStock, mProductSell, operationCost,test,Due,Seller,Buyer
from dairyapp.choices import MILK_CHOICES
import datetime
from bootstrap_modal_forms.mixins import PopRequestMixin, CreateUpdateAjaxMixin


class mPurchaseForm(forms.ModelForm):
    """
        This form is for milk purchase
    """

    seller=forms.ModelChoiceField(
        label='Seller Name',
        queryset=Seller.objects.all().order_by('seller_name'),
        required=True,
        help_text="Select seller from list",
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="-- Select Seller --"
    )
    
    def clean_seller(self):
        seller = self.cleaned_data.get('seller')
        if seller:
            return seller.seller_name  # Return name string for backward compatibility
        return seller

    mPurchase_date=forms.DateField(
        label='Date',
        #input_formats=['%Y-%m-%d'],
    )


    mPurchase_qty=forms.FloatField(
        label='Qty (Liters)',
        help_text="The quantity must be in numeric format",
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0'})
    )

    # Summary rates (configurable)
    fat_rate_per_kg=forms.FloatField(
        label='Fat Rate/kg',
        initial=7.15,
        help_text="Fat rate per kg",
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0'})
    )
    
    snf_rate_per_kg=forms.FloatField(
        label='SNF Rate/Kgs',
        initial=4.55,
        help_text="SNF rate per kg",
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0'})
    )
    
    total_solids_per_kg=forms.FloatField(
        label='Total Solids/Kgs (%)',
        initial=10.0,
        help_text="Total solids per kg percentage",
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0'})
    )

    # Input fields
    fat=forms.FloatField(
        label='Fat (%)',
        required=False,
        help_text="Fat percentage",
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '10'})
    )

    snf=forms.FloatField(
        label='SNF (%)',
        required=False,
        help_text="Solid Not Fat percentage",
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '10'})
    )
    
    ts=forms.FloatField(
        label='TS (Total Solids)',
        required=False,
        help_text="Total Solids",
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0'})
    )
    
    advance_amount=forms.FloatField(
        label='Advance Amount (NRs)',
        required=False,
        initial=0,
        help_text="Advance amount given to seller (optional)",
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0'})
    )
    
    remarks=forms.CharField(
        label='Remarks (Optional)',
        required=False,
        max_length=500,
        help_text="Additional notes or remarks",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    def __init__(self, *args, **kwargs):
        super(mPurchaseForm, self).__init__(*args, **kwargs)
        self.fields['mPurchase_date'].widget.attrs['id'] = 'nepalicalendar'
        # Set initial seller if it matches an existing seller name
        if self.instance and self.instance.pk and self.instance.seller:
            try:
                seller_obj = Seller.objects.get(seller_name=self.instance.seller)
                self.fields['seller'].initial = seller_obj
            except Seller.DoesNotExist:
                pass

    class Meta:
        model=mPurchase
        fields=('seller','mPurchase_date','mPurchase_qty',
                'fat_rate_per_kg','snf_rate_per_kg','total_solids_per_kg',
                'fat','snf','ts','advance_amount','remarks',)

    ## Negative Value Validations
    def clean(self):
        super(mPurchaseForm,self).clean()
        mPurchase_date = self.cleaned_data.get('mPurchase_date')
        mPurchase_qty = self.cleaned_data.get('mPurchase_qty')

        try:
            datetime.datetime.strptime(str(mPurchase_date), '%Y-%m-%d')
        except ValueError:
            self._errors['mPurchase_date'] = self.error_class(["Date should be in YYYY-mm-dd format"])

        if mPurchase_qty is not None and mPurchase_qty < 0:
            self._errors['mPurchase_qty']=self.error_class(["Negative value not allowed"])

        # Validate new fields
        fat = self.cleaned_data.get('fat')
        if fat is not None and fat < 0:
            self._errors['fat'] = self.error_class(["Fat value cannot be negative"])
        
        snf = self.cleaned_data.get('snf')
        if snf is not None and snf < 0:
            self._errors['snf'] = self.error_class(["SNF value cannot be negative"])
        
        ts = self.cleaned_data.get('ts')
        if ts is not None and ts < 0:
            self._errors['ts'] = self.error_class(["TS value cannot be negative"])
        
        fat_rate_per_kg = self.cleaned_data.get('fat_rate_per_kg')
        if fat_rate_per_kg is not None and fat_rate_per_kg < 0:
            self._errors['fat_rate_per_kg'] = self.error_class(["Fat rate cannot be negative"])
        
        snf_rate_per_kg = self.cleaned_data.get('snf_rate_per_kg')
        if snf_rate_per_kg is not None and snf_rate_per_kg < 0:
            self._errors['snf_rate_per_kg'] = self.error_class(["SNF rate cannot be negative"])
        
        total_solids_per_kg = self.cleaned_data.get('total_solids_per_kg')
        if total_solids_per_kg is not None and total_solids_per_kg < 0:
            self._errors['total_solids_per_kg'] = self.error_class(["Total solids rate cannot be negative"])
        
        advance_amount = self.cleaned_data.get('advance_amount')
        if advance_amount is not None and advance_amount < 0:
            self._errors['advance_amount'] = self.error_class(["Advance amount cannot be negative"])
        if advance_amount is None:
            self.cleaned_data['advance_amount'] = 0

        # Set default milk type if not provided
        if 'mPurchase_product' not in self.cleaned_data:
            from dairyapp.choices import Cow
            self.cleaned_data['mPurchase_product'] = Cow

        return self.cleaned_data


class mStockForm(forms.ModelForm):
    """
        This form is for adding milk product stock
    """

    mStock_product = forms.ModelChoiceField(
        queryset=mProduct.objects.filter(),
        label='Select Milk Product',
        help_text="Choose from the list of milk products",
        required=True,

    )
    mStock_date=forms.DateField(
        label='Date',
        required=True,
    )
    mStock_qty = forms.FloatField(
        label='Quantity',
        help_text='Enter stock quantity',
        required=True,

    )

    def __init__(self, *args, **kwargs):
        super(mStockForm, self).__init__(*args, **kwargs)
        self.fields['mStock_date'].widget.attrs['id'] = 'nepalicalendar'


    def clean(self):
        super(mStockForm, self).clean()
        mStock_date=self.cleaned_data.get('mStock_date')
        mStock_qty = self.cleaned_data.get('mStock_qty')

        try:
            datetime.datetime.strptime(str(mStock_date), '%Y-%m-%d')
        except ValueError:
            self._errors['mStock_date'] = self.error_class(["Date should be in YYYY-mm-dd format"])


        ## Negative Value Validations
        if (mStock_qty < 0):
            self._errors['mStock_qty'] = self.error_class(["Negative value not allowed"])

        return self.cleaned_data

    class Meta:
        model=mStock
        fields=('mStock_product','mStock_date','mStock_qty',)





class mProductSellForm(forms.ModelForm):
    """
        This form is for selling products
    """

    buyer_name=forms.ModelChoiceField(
        label='Buyer Name',
        queryset=Buyer.objects.all().order_by('buyer_name'),
        required=True,
        help_text="Select buyer from list",
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="-- Select Buyer --"
    )
    
    def clean_buyer_name(self):
        buyer = self.cleaned_data.get('buyer_name')
        if buyer:
            return buyer.buyer_name  # Return name string for backward compatibility
        return buyer

    milk_product=forms.ModelChoiceField(
        queryset=mProduct.objects.filter(),
        label='Select Milk Product',
        help_text="Choose from the list of milk products",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="-- Select Product --"
    )

    mProductSell_date=forms.DateField(
        label='Date',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'nepalicalendar_sell'})
    )

    mProductSell_qty = forms.FloatField(
        label='Quantity (Liters)',
        help_text='Enter product quantity in liters',
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'})
    )

    fat_rate_per_kg=forms.FloatField(
        label='Fat Rate/kg',
        required=True,
        initial=7.15,
        help_text="Fat Rate per kg",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'})
    )
    
    snf_rate_per_kg=forms.FloatField(
        label='SNF Rate/Kgs',
        required=True,
        initial=4.55,
        help_text="SNF Rate per kg",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'})
    )
    
    total_solids_per_kg=forms.FloatField(
        label='Total Solids/Kgs (%)',
        required=True,
        initial=10.0,
        help_text="Total Solids per kg (%)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'})
    )
    
    fat=forms.FloatField(
        label='Fat (%)',
        required=False,
        help_text="Fat percentage",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'})
    )
    
    snf=forms.FloatField(
        label='SNF (%)',
        required=False,
        help_text="SNF percentage",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'})
    )
    
    ts=forms.FloatField(
        label='TS (Total Solids)',
        required=False,
        help_text="Total Solids",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'})
    )
    
    advance_amount=forms.FloatField(
        label='Advance Amount',
        required=False,
        initial=0,
        help_text="Advance amount received from buyer (optional)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'})
    )
    
    remarks=forms.CharField(
        label='Remarks (Optional)',
        required=False,
        max_length=500,
        help_text="Additional notes or remarks",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    def __init__(self, *args, **kwargs):
        super(mProductSellForm, self).__init__(*args, **kwargs)

    def clean(self):
        super(mProductSellForm, self).clean()
        mProductSell_date=self.cleaned_data.get('mProductSell_date')
        mProductSell_qty = self.cleaned_data.get('mProductSell_qty')

        try:
            datetime.datetime.strptime(str(mProductSell_date), '%Y-%m-%d')
        except ValueError:
            self._errors['mProductSell_date'] = self.error_class(["Date should be in YYYY-mm-dd format"])

        if mProductSell_qty is not None and mProductSell_qty < 0:
            self._errors['mProductSell_qty'] = self.error_class(["Quantity cannot be negative"])

        fat = self.cleaned_data.get('fat')
        if fat is not None and fat < 0:
            self._errors['fat'] = self.error_class(["Fat value cannot be negative"])
        
        snf = self.cleaned_data.get('snf')
        if snf is not None and snf < 0:
            self._errors['snf'] = self.error_class(["SNF value cannot be negative"])
        
        ts = self.cleaned_data.get('ts')
        if ts is not None and ts < 0:
            self._errors['ts'] = self.error_class(["TS value cannot be negative"])
        
        fat_rate_per_kg = self.cleaned_data.get('fat_rate_per_kg')
        if fat_rate_per_kg is not None and fat_rate_per_kg < 0:
            self._errors['fat_rate_per_kg'] = self.error_class(["Fat rate cannot be negative"])
        
        snf_rate_per_kg = self.cleaned_data.get('snf_rate_per_kg')
        if snf_rate_per_kg is not None and snf_rate_per_kg < 0:
            self._errors['snf_rate_per_kg'] = self.error_class(["SNF rate cannot be negative"])
        
        total_solids_per_kg = self.cleaned_data.get('total_solids_per_kg')
        if total_solids_per_kg is not None and total_solids_per_kg < 0:
            self._errors['total_solids_per_kg'] = self.error_class(["Total solids rate cannot be negative"])
        
        advance_amount = self.cleaned_data.get('advance_amount')
        if advance_amount is not None and advance_amount < 0:
            self._errors['advance_amount'] = self.error_class(["Advance amount cannot be negative"])
        if advance_amount is None:
            self.cleaned_data['advance_amount'] = 0

        return self.cleaned_data

    class Meta:
        model=mProductSell
        fields=('buyer_name','milk_product','mProductSell_date','mProductSell_qty',
                'fat_rate_per_kg','snf_rate_per_kg','total_solids_per_kg',
                'fat','snf','ts','advance_amount','remarks',)


## operation cost form
class operationCostForm(forms.ModelForm):
    """
        This form is for operational costs!
    """

    particular=forms.CharField(
        label='Particular',
        required=True,
    )
    date=forms.DateField(
        label='Date',
        required=True,
    )

    qty=forms.FloatField(
        label='Quantity',
        help_text='Enter Quantity',
        required=True,
    )

    rate=forms.FloatField(
        label='Rate',
        help_text='Enter Rate',
        required=True,
    )

    class Meta:
        model=operationCost
        fields=('particular','date','qty','rate')

    def __init__(self, *args, **kwargs):
        super(operationCostForm, self).__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['id'] = 'nepalicalendar'

    def clean(self):
        super(operationCostForm,self).clean()
        date=self.cleaned_data.get('date')
        qty = self.cleaned_data.get('qty')
        rate=self.cleaned_data.get('rate')

        ##date validation
        try:
            datetime.datetime.strptime(str(date), '%Y-%m-%d')
        except ValueError:
            self._errors['date'] = self.error_class(["Date should be in YYYY-mm-dd format"])

        ## Negative Value Validation
        if(qty<0):
            self._errors['qty']=self.error_class(["Negative value not allowed"])

        if(rate<0):
            self._errors['rate'] = self.error_class(["Negative value not allowed"])

        return self.cleaned_data



##nepali date selection form
class dateForm(forms.Form):

    fromdate=forms.DateField(
        label='FROM',

    )

    todate=forms.DateField(
        label='TO',
    )

    def __init__(self, *args, **kwargs):
        super(dateForm, self).__init__(*args, **kwargs)
        self.fields['fromdate'].widget.attrs['id'] = 'nepalicalendar'
        self.fields['todate'].widget.attrs['id'] = 'nepalicalendar2'

    ## validate and clean entered date value
    def clean(self):
        super(dateForm,self).clean()
        fromdate=self.cleaned_data.get('fromdate')
        todate=self.cleaned_data.get('todate')

        try:
            datetime.datetime.strptime(str(fromdate),'%Y-%m-%d')
        except ValueError:
            self._errors['fromdate'] = self.error_class(["Date should be in YYYY-mm-dd format"])

        try:
            datetime.datetime.strptime(str(todate), '%Y-%m-%d')
        except ValueError:
            self._errors['todate'] = self.error_class(["Date should be in YYYY-mm-dd format"])


    class Meta:
        fields=('fromdate','todate')


##popup forms for settings

class addProductForm(PopRequestMixin, CreateUpdateAjaxMixin, forms.ModelForm):
    mProduct_name=forms.CharField(
        label='Product Name'
    )

    mProduct_qtyunit=forms.ModelChoiceField(
        label='Select Unit Type',
        queryset=mProductUnit.objects.filter(),
    )
    class Meta:
        model = mProduct
        fields = ['mProduct_name', 'mProduct_qtyunit']

## add /create product unit form
class addProductUnitForm(forms.ModelForm):
    mProductUnit_name=forms.CharField(
        label='Product Unit Name'
    )

    class Meta:
        model = mProductUnit
        fields = ['mProductUnit_name']


### test form
class testForm(forms.ModelForm):
    name=forms.CharField(
        label='name'
    )
    date=forms.DateTimeField(
        label='date'
    )

    def __init__(self, *args, **kwargs):
        super(testForm, self).__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['id'] = 'nepalicalendar'

    ## validate and clean entered date value
    def clean(self):
        super(testForm,self).clean()
        date=self.cleaned_data.get('date')



    class Meta:
        model=test
        fields=('name','date',)


class MonthlyReportForm(forms.Form):
    REPORT_TYPE_CHOICES = (
        ('purchase', 'Purchase Report (Sellers)'),
        ('sales', 'Sales Report (Buyers)'),
    )
    
    report_type = forms.ChoiceField(
        label='Report Type',
        choices=REPORT_TYPE_CHOICES,
        required=True,
        initial='purchase',
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'report_type'}),
        help_text="Select report type"
    )
    
    seller = forms.ModelChoiceField(
        label='Seller Name',
        queryset=Seller.objects.all().order_by('seller_name'),
        required=False,
        help_text="Select seller from list",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'seller_field'}),
        empty_label="-- Select Seller --"
    )
    
    buyer = forms.ModelChoiceField(
        label='Buyer Name',
        queryset=Buyer.objects.all().order_by('buyer_name'),
        required=False,
        help_text="Select buyer from list",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'buyer_field'}),
        empty_label="-- Select Buyer --"
    )
    
    def clean_seller(self):
        seller = self.cleaned_data.get('seller')
        if seller:
            return seller.seller_name  # Return name string for backward compatibility
        return seller
    
    def clean_buyer(self):
        buyer = self.cleaned_data.get('buyer')
        if buyer:
            return buyer.buyer_name  # Return name string for backward compatibility
        return buyer
    
    def clean(self):
        cleaned_data = super(MonthlyReportForm, self).clean()
        report_type = cleaned_data.get('report_type')
        seller = cleaned_data.get('seller')
        buyer = cleaned_data.get('buyer')
        
        if report_type == 'purchase' and not seller:
            self.add_error('seller', 'Please select a seller for purchase report')
        
        if report_type == 'sales' and not buyer:
            self.add_error('buyer', 'Please select a buyer for sales report')
        
        return cleaned_data
    
    report_date = forms.DateField(
        label='Select Date (Any date in the month)',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'nepalicalendar_monthly'}),
        help_text="Select any date within the month you want to generate report for"
    )
    
    def __init__(self, *args, **kwargs):
        super(MonthlyReportForm, self).__init__(*args, **kwargs)


class SellerForm(forms.ModelForm):
    seller_name = forms.CharField(
        label='Seller Name',
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Enter seller name (must be unique)"
    )
    
    seller_address = forms.CharField(
        label='Address',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Seller address (optional)"
    )
    
    seller_contact = forms.CharField(
        label='Contact',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Contact number (optional)"
    )
    
    default_fat_rate_per_kg = forms.FloatField(
        label='Default Fat Rate/kg',
        required=False,
        initial=7.15,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        help_text="Default fat rate per kg (optional)"
    )
    
    default_snf_rate_per_kg = forms.FloatField(
        label='Default SNF Rate/Kgs',
        required=False,
        initial=4.55,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        help_text="Default SNF rate per kg (optional)"
    )
    
    default_total_solids_per_kg = forms.FloatField(
        label='Default Total Solids/Kgs (%)',
        required=False,
        initial=10.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        help_text="Default total solids per kg percentage (optional)"
    )
    
    remarks = forms.CharField(
        label='Remarks',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        help_text="Additional notes about the seller (optional)"
    )
    
    class Meta:
        model = Seller
        fields = ('seller_name', 'seller_address', 'seller_contact', 
                  'default_fat_rate_per_kg', 'default_snf_rate_per_kg', 
                  'default_total_solids_per_kg', 'remarks')


class BuyerForm(forms.ModelForm):
    buyer_name = forms.CharField(
        label='Buyer Name',
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Enter buyer name (must be unique)"
    )
    
    buyer_address = forms.CharField(
        label='Address',
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Buyer address (optional)"
    )
    
    buyer_contact = forms.CharField(
        label='Contact',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Contact number (optional)"
    )
    
    default_fat_rate_per_kg = forms.FloatField(
        label='Default Fat Rate/kg',
        required=False,
        initial=7.15,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        help_text="Default fat rate per kg (optional)"
    )
    
    default_snf_rate_per_kg = forms.FloatField(
        label='Default SNF Rate/Kgs',
        required=False,
        initial=4.55,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        help_text="Default SNF rate per kg (optional)"
    )
    
    default_total_solids_per_kg = forms.FloatField(
        label='Default Total Solids/Kgs (%)',
        required=False,
        initial=10.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        help_text="Default total solids per kg percentage (optional)"
    )
    
    remarks = forms.CharField(
        label='Remarks',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        help_text="Additional notes about the buyer (optional)"
    )
    
    class Meta:
        model = Buyer
        fields = ('buyer_name', 'buyer_address', 'buyer_contact', 
                  'default_fat_rate_per_kg', 'default_snf_rate_per_kg', 
                  'default_total_solids_per_kg', 'remarks')


class DueForm(forms.ModelForm):
    due_type = forms.ChoiceField(
        choices=Due.DUE_TYPE_CHOICES,
        label='Due Type',
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    
    person_name = forms.CharField(
        label='Person Name',
        max_length=100,
        help_text="Enter customer or supplier name",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )
    
    contact_number = forms.CharField(
        label='Contact Number',
        max_length=20,
        help_text="Enter contact phone number (optional)",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    
    address = forms.CharField(
        label='Address',
        max_length=200,
        help_text="Enter address (optional)",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    
    date = forms.DateField(
        label='Date',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'nepalicalendar'})
    )
    
    particular = forms.CharField(
        label='Particular / Description',
        max_length=200,
        help_text="Enter description or reason for due",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )
    
    total_amount = forms.FloatField(
        label='Total Amount (NRs)',
        help_text="Enter total amount",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        required=True
    )
    
    paid_amount = forms.FloatField(
        label='Paid Amount (NRs)',
        help_text="Enter paid amount (if any)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        required=False,
        initial=0
    )
    
    remarks = forms.CharField(
        label='Remarks (Optional)',
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    
    def clean(self):
        cleaned_data = super(DueForm, self).clean()
        total_amount = cleaned_data.get('total_amount')
        paid_amount = cleaned_data.get('paid_amount') or 0
        
        if total_amount is not None and total_amount < 0:
            self.add_error('total_amount', 'Amount cannot be negative')
        
        if paid_amount is not None and paid_amount < 0:
            self.add_error('paid_amount', 'Paid amount cannot be negative')
        
        if total_amount is not None and paid_amount is not None and paid_amount > total_amount:
            self.add_error('paid_amount', 'Paid amount cannot exceed total amount')
        
        return cleaned_data
    
    class Meta:
        model = Due
        fields = ('due_type', 'person_name', 'contact_number', 'address', 'date', 'particular', 'total_amount', 'paid_amount', 'remarks')



