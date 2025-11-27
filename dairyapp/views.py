from .forms import mPurchaseForm,mStockForm,mProductSellForm, operationCostForm,testForm,dateForm, addProductForm,addProductUnitForm,DueForm
from .models import mPurchase,mProduct,mStock, mProductSell, mProduct, mProductUnit,test,Due
from .models import operationCost as operationCostModel
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.urls import reverse_lazy
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from bootstrap_modal_forms.mixins import PassRequestMixin


@login_required
def index(request):
    title='DAIRY'
    context={
        'title':title
    }
    return render(request,'dairyapp/index.html',context)

@login_required
def milkPurchase(request):
    title='Buy Milk'
    milk_list = mPurchase.objects.all().order_by('-mPurchase_id')

    if request.method=='POST':
        form=mPurchaseForm(request.POST)
        if form.is_valid():
            m=form.save(commit=False)
            ## gives object bound to form
            ## commit = False means it gives object that has not been saved in db yet
            ##m.mPurchase_date=timezone.now()
            m.mPurchase_total=m.mPurchase_qty*m.mPurchase_rate
            m.save()
            return redirect('/milkpurchase')

    else:
        form=mPurchaseForm()

    ## Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(milk_list, 10)

    try:
        milk = paginator.page(pageff)
    except PageNotAnInteger:
        milk = paginator.page(1)
    except EmptyPage:
        milk = paginator.page(paginator.num_pages)

    context = {
        'title': title,
        'form': form,
        'milk': milk

    }

    return render(request,'dairyapp/milk-purchase.html',context)

@login_required
def milkPurchaseDelete(request,id):
    mPurchase.objects.get(mPurchase_id=id).delete()
    return redirect('/milkpurchase')


@login_required
def addMilkProducts(request):
    title='Add Milk Products'
    product=mProduct.objects.all().order_by('-mProduct_name')

    if request.method=='POST':
        form=mStockForm(request.POST)
        if form.is_valid():
            m=form.save(commit=False)
            ## gives object bound to form
            ## commit = False means it gives object that has not been saved in db yet
            mProduct_name=form.cleaned_data.get('mStock_product')
            ##m.mStock_date=timezone.now()
            p=get_object_or_404(mProduct,mProduct_name=mProduct_name)
            qty=form.cleaned_data.get('mStock_qty')
            p.mProduct_qty=p.mProduct_qty+qty  ##update stock

            p.save()
            m.save()
            messages.info(request, 'Product Successfully Added to Stock')

            return redirect('/addmilkproducts')

    else:
        form=mStockForm()
    context={
        'title':title,
        'product':product,
        'form':form,
    }
    return render(request,'dairyapp/add-milk-products.html',context)

@login_required
def mStockDetailView(request,id):
    model=mStock
    m=get_object_or_404(mProduct,mProduct_id=id)
    stock_list=mStock.objects.filter(mStock_product=m.mProduct_id).order_by('-mStock_date')
    ## Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(stock_list, 10)

    try:
        stock = paginator.page(page)
    except PageNotAnInteger:
        stock = paginator.page(1)
    except EmptyPage:
        stock = paginator.page(paginator.num_pages)

    context={
        'm':m,
        'stock':stock,
    }

    return render(request,'dairyapp/stock-details.html',context)

# ## Delete stock logs
# def mStockRecordDelete(request,id):
#     mStock.objects.get(mStock_id=id).delete()
#     # m = get_object_or_404(mProduct, mProduct_id=mid)
#     # stock = mStock.objects.filter(mStock_id=id)
#     # m.mProduct_qty=m.mProduct_qty-stock.mStock_qty
#     # m.save()
#
#     # context = {
#     #     'm': m,
#     #     'stock': stock,
#     # }
#     # if not stock:
#     return redirect('/addmilkproducts')

    #return render(request, 'dairyapp/stock-details.html', context)

@login_required
def sellMilkProducts(request):
    title='Sell Milk Products'
    sales_list=mProductSell.objects.all().order_by('-mProductSell_date')
    if request.method=='POST':
        form=mProductSellForm(request.POST)
        if form.is_valid():
            m=form.save(commit=False)
            ## gives object bound to form
            ## commit = False means it gives object that has not been saved in db yet
            milk_product = form.cleaned_data.get('milk_product')
            ##m.mProductSell_date=timezone.now()
            p=get_object_or_404(mProduct,mProduct_name=milk_product)
            qty=form.cleaned_data.get('mProductSell_qty')
            rate=form.cleaned_data.get('mProductSell_rate')
            m.mProductSell_amount=qty*rate

            ## update only if stock is available
            if (p.mProduct_qty>=qty):
                p.mProduct_qty=p.mProduct_qty-qty  ##update stock
                m.mProductSell_qtyunit=p.mProduct_qtyunit
                p.save()
                m.save()
                messages.info(request, 'Product Successfully sold')
                return redirect('/sellmilkproducts')
            else:
                messages.warning(request,'Product Quantity not available in stock')


    else:
        form=mProductSellForm()

    ## Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(sales_list, 10)

    try:
        sales = paginator.page(page)
    except PageNotAnInteger:
        sales = paginator.page(1)
    except EmptyPage:
        sales = paginator.page(paginator.num_pages)

    context={
        'title':title,
        'form':form,
        'sales':sales,
    }
    return render(request,'dairyapp/sell-milk-products.html',context)


@login_required
def mProductSellDelete(request,id):

    sale=mProductSell.objects.get(mProductSell_id=id)
    p = get_object_or_404(mProduct, mProduct_name=sale.milk_product)
    p.mProduct_qty=p.mProduct_qty+sale.mProductSell_qty
    p.save()  ##Update product stock while deleting sale record
    sale.delete()
    ##Deletes the sales instance from database

    return redirect('/sellmilkproducts')

@login_required
def operationCost(request):
    title='Operation Cost'
    operations_list=operationCostModel.objects.all().order_by('-date')

    if request.method=='POST':
        form=operationCostForm(request.POST)
        if form.is_valid():
            m=form.save(commit=False)
            ## gives object bound to form
            ## commit = False means it gives object that has not been saved in db yet
            #m.date=timezone.now()
            qty=form.cleaned_data.get('qty')
            rate=form.cleaned_data.get('rate')
            m.amount=qty*rate
            m.save()
            messages.info(request, 'Record Successfully Added')
            return redirect('/operationcost')

    else:
        form=operationCostForm()

    ## Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(operations_list, 10)

    try:
        operations = paginator.page(page)
    except PageNotAnInteger:
        operations = paginator.page(1)
    except EmptyPage:
        operations = paginator.page(paginator.num_pages)

    context={
        'title':title,
        'form': form,
        'operations':operations,


    }
    return render(request,'dairyapp/operationcost.html',context)

@login_required
def deleteOperationCost(request,id):
    operationCostModel.objects.get(operationCost_id=id).delete()
    return redirect('/operationcost')

@login_required
def due(request):
    title='Due (बाँकी)'
    dues_list = Due.objects.all().order_by('-date')
    
    if request.method == 'POST':
        form = DueForm(request.POST)
        if form.is_valid():
            due_obj = form.save(commit=False)
            due_obj.balance_amount = due_obj.total_amount - due_obj.paid_amount
            due_obj.save()
            messages.success(request, 'Due record added successfully.')
            return redirect('/due/')
    else:
        form = DueForm()
    
    page = request.GET.get('page', 1)
    paginator = Paginator(dues_list, 10)
    
    try:
        dues = paginator.page(page)
    except PageNotAnInteger:
        dues = paginator.page(1)
    except EmptyPage:
        dues = paginator.page(paginator.num_pages)
    
    customer_dues = Due.objects.filter(due_type='customer')
    supplier_dues = Due.objects.filter(due_type='supplier')
    total_customer_due = sum([d.balance_amount for d in customer_dues if d.balance_amount > 0])
    total_supplier_due = sum([d.balance_amount for d in supplier_dues if d.balance_amount > 0])
    net_receivable = total_customer_due - total_supplier_due
    
    context = {
        'title': title,
        'form': form,
        'dues': dues,
        'total_customer_due': total_customer_due,
        'total_supplier_due': total_supplier_due,
        'net_receivable': net_receivable,
    }
    return render(request,'dairyapp/due.html',context)

@login_required
def dueDelete(request, id):
    Due.objects.get(due_id=id).delete()
    messages.success(request, 'Due record deleted successfully.')
    return redirect('/due/')

@login_required
def dueUpdate(request, id):
    due_obj = get_object_or_404(Due, due_id=id)
    
    if request.method == 'POST':
        form = DueForm(request.POST, instance=due_obj)
        if form.is_valid():
            due_obj = form.save(commit=False)
            due_obj.balance_amount = due_obj.total_amount - due_obj.paid_amount
            due_obj.save()
            messages.success(request, 'Due record updated successfully.')
            return redirect('/due/')
    else:
        form = DueForm(instance=due_obj)
    
    context = {
        'title': 'Update Due',
        'form': form,
        'due': due_obj,
    }
    return render(request, 'dairyapp/due-update.html', context)

@login_required
def report(request):
    title='REPORT'
    context={
        'title':title
    }
    return render(request,'dairyapp/report.html',context)

@login_required
def purchaseReport(request):
    title='Purchase Report'
    milk=mPurchase.objects.all().order_by('-mPurchase_id')[:10]

    if request.method=='POST':
        form=dateForm(request.POST)

        if form.is_valid():
            f=form.cleaned_data
            ## now f is a dictionary
            dateFrom=f.get('fromdate')
            dateTo=f.get('todate')
            ## filter by start and stop date
            milk=mPurchase.objects.filter(mPurchase_date__gte=dateFrom,
                                          mPurchase_date__lte=dateTo).order_by('-mPurchase_id')

            if not milk:
                messages.info(request, 'No Records Found')


    else:
        form = dateForm()

    context = {
        'title': title,
        'form': form,
        'milk': milk,
    }
    return render(request,'dairyapp/purchase-report.html',context)

@login_required
def stockReport(request):
    title='Stock Report'
    stock = mStock.objects.all().order_by('-mStock_date')[:10]

    if request.method == 'POST':
        form = dateForm(request.POST)

        if form.is_valid():
            f = form.cleaned_data
            ## now f is a dictionary
            dateFrom = f.get('fromdate')
            dateTo = f.get('todate')
            ## filter by start and stop date
            stock = mStock.objects.filter(mStock_date__gte=dateFrom,
                                            mStock_date__lte=dateTo).order_by('-mStock_date')

            if not stock:
                messages.info(request, 'No Records Found')


    else:
        form = dateForm()

    context = {
        'title': title,
        'form': form,
        'stock': stock,
    }
    return render(request, 'dairyapp/stock-report.html',context)

@login_required
def salesReport(request):
    title='Sales Report'

    sales = mProductSell.objects.all().order_by('-mProductSell_date')[:10]

    if request.method == 'POST':
        form = dateForm(request.POST)

        if form.is_valid():
            f = form.cleaned_data
            ## now f is a dictionary
            dateFrom = f.get('fromdate')
            dateTo = f.get('todate')
            ## filter by start and stop date
            sales = mProductSell.objects.filter(mProductSell_date__gte=dateFrom,
                                          mProductSell_date__lte=dateTo).order_by('-mProductSell_date')

            ## if no records found
            if not sales:
                messages.info(request, 'No Records Found')


    else:
        form = dateForm()

    context = {
        'title': title,
        'form': form,
        'sales': sales,
    }
    return render(request,'dairyapp/sales-report.html',context)


@login_required
def operationCostReport(request):
    title='Operation Cost Report'
    operations = operationCostModel.objects.all().order_by('-date')[:10]

    if request.method == 'POST':
        form = dateForm(request.POST)

        if form.is_valid():
            f = form.cleaned_data
            ## now f is a dictionary
            dateFrom = f.get('fromdate')
            dateTo = f.get('todate')
            ## filter by start and stop date
            operations = operationCostModel.objects.filter(date__gte=dateFrom,
                                            date__lte=dateTo).order_by('-date')

            if not operations:
                messages.info(request, 'No Records Found')


    else:
        form = dateForm()

    context = {
        'title': title,
        'form': form,
        'operations': operations,
    }
    return render(request,'dairyapp/operationcost-report.html',context)

@login_required
def settings(request):
    title='Settings'

    products=mProduct.objects.all()
    units=mProductUnit.objects.all()

    context={
        'title':title,
        'products':products,
        'units':units,
    }

    return  render(request,'dairyapp/settings/index.html',context)

## create/add new product name view
class newProductCreateView(LoginRequiredMixin, PassRequestMixin, SuccessMessageMixin,
                     generic.CreateView):
    template_name = 'dairyapp/settings/add-product.html'
    form_class = addProductForm
    success_message = 'Success: Product was created.'
    success_url = '/settings/'

@login_required
def newProductUnitCreate(request):
    title='Create New Product Unit'

    if request.method == 'POST':
        form = addProductUnitForm(request.POST)

        if form.is_valid():
            f = form.save(commit=False)
            f.save()
            return redirect('/settings')

    else:
        form = addProductUnitForm()

    context = {
        'title': title,
        'form':form
    }

    return render(request,'dairyapp/settings/add-unit.html',context)

@login_required
def test(request):
    title='TEST'

    if request.method=='POST':
        form=testForm(request.POST)
        if form.is_valid():
            m=form.save(commit=False)
            ## gives object bound to form
            ## commit = False means it gives object that has not been saved in db yet

            date=form.cleaned_data.get('data')
            m.save()
            return redirect('/test')

    else:
        form=testForm()
    context={
        'title':title,
        'form':form,
    }
    return render(request,'dairyapp/test.html',context)