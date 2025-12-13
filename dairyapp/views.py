from .forms import mPurchaseForm,mStockForm,mProductSellForm, operationCostForm,testForm,dateForm, addProductForm,addProductUnitForm,DueForm,MonthlyReportForm,SellerForm,BuyerForm
from .models import mPurchase,mProduct,mStock, mProductSell, mProduct, mProductUnit,test,Due,Seller,Buyer
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
from django.db.models import Sum, Count, Q
import datetime
import calendar


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
            m.save()
            messages.success(request, 'Purchase record added successfully.')
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

    totals = {
        'total_qty': sum([p.mPurchase_qty for p in milk if p.mPurchase_qty]),
        'total_ts_amount': sum([p.ts_amount for p in milk if p.ts_amount]),
        'total_amount': sum([p.mPurchase_total for p in milk if p.mPurchase_total]),
        'total_advance': sum([p.advance_amount for p in milk if p.advance_amount]),
    }
    
    seller_advance_info = {}
    all_purchases = mPurchase.objects.all()
    for purchase in all_purchases:
        seller = purchase.seller
        if seller not in seller_advance_info:
            seller_advance_info[seller] = {
                'total_advance': 0,
                'total_purchase': 0,
                'remaining_balance': 0,
            }
        seller_advance_info[seller]['total_advance'] += purchase.advance_amount or 0
        seller_advance_info[seller]['total_purchase'] += purchase.mPurchase_total or 0
    
    for seller in seller_advance_info:
        seller_advance_info[seller]['remaining_balance'] = (
            seller_advance_info[seller]['total_purchase'] - 
            seller_advance_info[seller]['total_advance']
        )
    
    for purchase in milk:
        seller = purchase.seller
        if seller in seller_advance_info:
            purchase.remaining_balance = seller_advance_info[seller]['remaining_balance']
        else:
            purchase.remaining_balance = 0

    context = {
        'title': title,
        'form': form,
        'milk': milk,
        'totals': totals,
        'seller_advance_info': seller_advance_info,
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
            mProduct_name=form.cleaned_data.get('mStock_product')
            p=get_object_or_404(mProduct,mProduct_name=mProduct_name)
            qty=form.cleaned_data.get('mStock_qty')
            p.mProduct_qty=p.mProduct_qty+qty

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

@login_required
def sellMilkProducts(request):
    title='Sell Milk Products'
    sales_list=mProductSell.objects.all().order_by('-mProductSell_id')

    if request.method=='POST':
        form=mProductSellForm(request.POST)
        if form.is_valid():
            m=form.save(commit=False)
            milk_product = form.cleaned_data.get('milk_product')
            p=get_object_or_404(mProduct,mProduct_name=milk_product)
            qty=form.cleaned_data.get('mProductSell_qty')

            if (p.mProduct_qty>=qty):
                p.mProduct_qty=p.mProduct_qty-qty
                m.mProductSell_qtyunit=p.mProduct_qtyunit
                p.save()
                m.save()
                messages.success(request, 'Product Successfully sold')
                return redirect('/sellmilkproducts')
            else:
                messages.warning(request,'Product Quantity not available in stock')
    else:
        form=mProductSellForm()

    page = request.GET.get('page', 1)
    paginator = Paginator(sales_list, 10)

    try:
        sales = paginator.page(page)
    except PageNotAnInteger:
        sales = paginator.page(1)
    except EmptyPage:
        sales = paginator.page(paginator.num_pages)

    totals = {
        'total_qty': sum([s.mProductSell_qty for s in sales if s.mProductSell_qty]),
        'total_ts_amount': sum([s.ts_amount for s in sales if s.ts_amount]),
        'total_amount': sum([s.mProductSell_amount for s in sales if s.mProductSell_amount]),
        'total_advance': sum([s.advance_amount for s in sales if s.advance_amount]),
    }
    
    buyer_advance_info = {}
    all_sales = mProductSell.objects.all()
    for sale in all_sales:
        buyer = sale.buyer_name
        if buyer not in buyer_advance_info:
            buyer_advance_info[buyer] = {
                'total_advance': 0,
                'total_sale': 0,
                'remaining_balance': 0,
            }
        buyer_advance_info[buyer]['total_advance'] += sale.advance_amount or 0
        buyer_advance_info[buyer]['total_sale'] += sale.mProductSell_amount or 0
    
    for buyer in buyer_advance_info:
        buyer_advance_info[buyer]['remaining_balance'] = (
            buyer_advance_info[buyer]['total_sale'] - 
            buyer_advance_info[buyer]['total_advance']
        )
    
    for sale in sales:
        buyer = sale.buyer_name
        if buyer in buyer_advance_info:
            sale.remaining_balance = buyer_advance_info[buyer]['remaining_balance']
        else:
            sale.remaining_balance = 0

    context={
        'title':title,
        'form':form,
        'sales':sales,
        'totals': totals,
        'buyer_advance_info': buyer_advance_info,
    }
    return render(request,'dairyapp/sell-milk-products.html',context)


@login_required
def mProductSellDelete(request,id):

    sale=mProductSell.objects.get(mProductSell_id=id)
    p = get_object_or_404(mProduct, mProduct_name=sale.milk_product)
    p.mProduct_qty=p.mProduct_qty+sale.mProductSell_qty
    p.save()
    sale.delete()
    return redirect('/sellmilkproducts')

@login_required
def operationCost(request):
    title='Operation Cost'
    operations_list=operationCostModel.objects.all().order_by('-date')

    if request.method=='POST':
        form=operationCostForm(request.POST)
        if form.is_valid():
            m=form.save(commit=False)
            qty=form.cleaned_data.get('qty')
            rate=form.cleaned_data.get('rate')
            m.amount=qty*rate
            m.save()
            messages.info(request, 'Record Successfully Added')
            return redirect('/operationcost')

    else:
        form=operationCostForm()

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
def monthlyReport(request):
    title='Monthly Report'
    
    purchases = None
    sales = None
    purchases_list = None
    sales_list = None
    seller_name = None
    buyer_name = None
    report_type = 'purchase'
    month = None
    year = None
    report_date = None
    totals = None
    summary_rates = None
    
    seller_id = request.GET.get('seller')
    buyer_id = request.GET.get('buyer')
    date_str = request.GET.get('date')
    report_type_param = request.GET.get('type', 'purchase')
    
    if request.method == 'POST':
        form = MonthlyReportForm(request.POST)
        if form.is_valid():
            report_type = form.cleaned_data.get('report_type')
            seller_name = form.cleaned_data.get('seller')
            buyer_name = form.cleaned_data.get('buyer')
            report_date = form.cleaned_data.get('report_date')
    else:
        form = MonthlyReportForm(initial={'report_type': report_type_param})
        if seller_id and date_str:
            try:
                seller_obj = Seller.objects.get(seller_id=seller_id)
                form.fields['seller'].initial = seller_obj
                form.fields['report_type'].initial = 'purchase'
                seller_name = seller_obj.seller_name
                report_type = 'purchase'
                try:
                    report_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                    form.fields['report_date'].initial = report_date
                except ValueError:
                    report_date = None
            except (Seller.DoesNotExist, ValueError):
                pass
        elif buyer_id and date_str:
            try:
                buyer_obj = Buyer.objects.get(buyer_id=buyer_id)
                form.fields['buyer'].initial = buyer_obj
                form.fields['report_type'].initial = 'sales'
                buyer_name = buyer_obj.buyer_name
                report_type = 'sales'
                try:
                    report_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                    form.fields['report_date'].initial = report_date
                except ValueError:
                    report_date = None
            except (Buyer.DoesNotExist, ValueError):
                pass
    
    selected_seller = seller_name
    selected_buyer = buyer_name
    if not selected_seller and seller_id:
        try:
            seller_obj = Seller.objects.get(seller_id=seller_id)
            selected_seller = seller_obj.seller_name
        except (Seller.DoesNotExist, ValueError):
            pass
    
    if not selected_buyer and buyer_id:
        try:
            buyer_obj = Buyer.objects.get(buyer_id=buyer_id)
            selected_buyer = buyer_obj.buyer_name
        except (Buyer.DoesNotExist, ValueError):
            pass
    
    if report_date:
        month = report_date.month
        year = report_date.year
        
        last_day = calendar.monthrange(year, month)[1]
        start_date = datetime.date(year, month, 1)
        end_date = datetime.date(year, month, last_day)
        
        if report_type == 'purchase' and seller_name:
            purchases_query = mPurchase.objects.filter(
                seller=seller_name,
                mPurchase_date__gte=start_date,
                mPurchase_date__lte=end_date
            ).order_by('-mPurchase_date', '-mPurchase_id')
            
            purchases_list = list(purchases_query[:100])
            
            seller_all_purchases = mPurchase.objects.filter(seller=seller_name).order_by('mPurchase_date', 'mPurchase_id')
            seller_advance_info = {}
            for purchase in seller_all_purchases:
                if purchase.seller not in seller_advance_info:
                    seller_advance_info[purchase.seller] = {
                        'total_advance': 0,
                        'total_purchase': 0
                    }
                seller_advance_info[purchase.seller]['total_advance'] += purchase.advance_amount or 0
                seller_advance_info[purchase.seller]['total_purchase'] += purchase.mPurchase_total or 0
            
            for purchase in purchases_list:
                total_advance = seller_advance_info.get(purchase.seller, {}).get('total_advance', 0)
                total_purchase = seller_advance_info.get(purchase.seller, {}).get('total_purchase', 0)
                purchase.remaining_balance = total_purchase - total_advance
            
            page = request.GET.get('page', 1)
            paginator = Paginator(purchases_list, 20)
            
            try:
                purchases = paginator.page(page)
            except PageNotAnInteger:
                purchases = paginator.page(1)
            except EmptyPage:
                purchases = paginator.page(paginator.num_pages)
            
            totals = {
                'total_qty': sum([p.mPurchase_qty for p in purchases if p.mPurchase_qty]),
                'total_ts_amount': sum([p.ts_amount for p in purchases if p.ts_amount]),
                'total_amount': sum([p.mPurchase_total for p in purchases if p.mPurchase_total]),
                'total_advance': sum([p.advance_amount for p in purchases if p.advance_amount]),
            }
            
            if purchases_list:
                first_purchase = purchases_list[0]
                summary_rates = {
                    'fat_rate_per_kg': first_purchase.fat_rate_per_kg or 7.15,
                    'snf_rate_per_kg': first_purchase.snf_rate_per_kg or 4.55,
                    'total_solids_per_kg': first_purchase.total_solids_per_kg or 10.0,
                }
            else:
                summary_rates = {
                    'fat_rate_per_kg': 7.15,
                    'snf_rate_per_kg': 4.55,
                    'total_solids_per_kg': 10.0,
                }
        
        elif report_type == 'sales' and buyer_name:
            sales_query = mProductSell.objects.filter(
                buyer_name=buyer_name,
                mProductSell_date__gte=start_date,
                mProductSell_date__lte=end_date
            ).order_by('-mProductSell_date', '-mProductSell_id')
            
            sales_list = list(sales_query[:100])
            
            buyer_all_sales = mProductSell.objects.filter(buyer_name=buyer_name).order_by('mProductSell_date', 'mProductSell_id')
            buyer_advance_info = {}
            for sale in buyer_all_sales:
                if sale.buyer_name not in buyer_advance_info:
                    buyer_advance_info[sale.buyer_name] = {
                        'total_advance': 0,
                        'total_sale': 0
                    }
                buyer_advance_info[sale.buyer_name]['total_advance'] += sale.advance_amount or 0
                buyer_advance_info[sale.buyer_name]['total_sale'] += sale.mProductSell_amount or 0
            
            for sale in sales_list:
                total_advance = buyer_advance_info.get(sale.buyer_name, {}).get('total_advance', 0)
                total_sale = buyer_advance_info.get(sale.buyer_name, {}).get('total_sale', 0)
                sale.remaining_balance = total_sale - total_advance
            
            page = request.GET.get('page', 1)
            paginator = Paginator(sales_list, 20)
            
            try:
                sales = paginator.page(page)
            except PageNotAnInteger:
                sales = paginator.page(1)
            except EmptyPage:
                sales = paginator.page(paginator.num_pages)
            
            totals = {
                'total_qty': sum([s.mProductSell_qty for s in sales if s.mProductSell_qty]),
                'total_ts_amount': sum([s.ts_amount for s in sales if s.ts_amount]),
                'total_amount': sum([s.mProductSell_amount for s in sales if s.mProductSell_amount]),
                'total_advance': sum([s.advance_amount for s in sales if s.advance_amount]),
            }
            
            if sales_list:
                first_sale = sales_list[0]
                summary_rates = {
                    'fat_rate_per_kg': first_sale.fat_rate_per_kg or 7.15,
                    'snf_rate_per_kg': first_sale.snf_rate_per_kg or 4.55,
                    'total_solids_per_kg': first_sale.total_solids_per_kg or 10.0,
                }
            else:
                summary_rates = {
                    'fat_rate_per_kg': 7.15,
                    'snf_rate_per_kg': 4.55,
                    'total_solids_per_kg': 10.0,
                }
    
    nepali_month_name = None
    nepali_year = None
    if month and year:
        try:
            from bikram import samwat
            ad_date = datetime.date(year, month, 1)
            bs_date = samwat.from_ad(ad_date)
            nepali_year = bs_date.year
            
            nepali_months = {
                1: 'बैशाख', 2: 'जेष्ठ', 3: 'आषाढ', 4: 'श्रावण', 5: 'भाद्र', 6: 'आश्विन',
                7: 'कार्तिक', 8: 'मंसिर', 9: 'पौष', 10: 'माघ', 11: 'फाल्गुन', 12: 'चैत्र'
            }
            nepali_month_name = nepali_months.get(bs_date.month, '')
        except Exception:
            nepali_month_name = None
            nepali_year = None
    
    context = {
        'title': title,
        'form': form,
        'purchases': purchases,
        'sales': sales,
        'report_type': report_type,
        'seller_name': seller_name or selected_seller,
        'buyer_name': buyer_name or selected_buyer,
        'month': month,
        'year': year,
        'report_date': report_date,
        'totals': totals,
        'summary_rates': summary_rates,
        'nepali_month_name': nepali_month_name,
        'nepali_year': nepali_year,
    }
    
    if month:
        context['month_name'] = calendar.month_name[month]
    
    return render(request, 'dairyapp/monthly-report.html', context)

@login_required
def purchaseReport(request):
    title='Purchase Report'
    milk=mPurchase.objects.all().order_by('-mPurchase_id')[:10]

    if request.method=='POST':
        form=dateForm(request.POST)

        if form.is_valid():
            f=form.cleaned_data
            dateFrom=f.get('fromdate')
            dateTo=f.get('todate')
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
            dateFrom = f.get('fromdate')
            dateTo = f.get('todate')
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
            dateFrom = f.get('fromdate')
            dateTo = f.get('todate')
            sales = mProductSell.objects.filter(mProductSell_date__gte=dateFrom,
                                          mProductSell_date__lte=dateTo).order_by('-mProductSell_date')

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
            dateFrom = f.get('fromdate')
            dateTo = f.get('todate')
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
def sellers(request):
    title='Buyers & Sellers Management (क्रेता र विक्रेता व्यवस्थापन)'
    sellers_list = Seller.objects.all().order_by('seller_name')
    buyers_list = Buyer.objects.all().order_by('buyer_name')
    
    # Handle seller form submission
    if request.method == 'POST' and 'seller_form' in request.POST:
        form = SellerForm(request.POST)
        buyer_form = BuyerForm()
        if form.is_valid():
            form.save()
            messages.success(request, 'Seller added successfully.')
            return redirect('/sellers/')
    # Handle buyer form submission
    elif request.method == 'POST' and 'buyer_form' in request.POST:
        buyer_form = BuyerForm(request.POST)
        form = SellerForm()
        if buyer_form.is_valid():
            buyer_form.save()
            messages.success(request, 'Buyer added successfully.')
            return redirect('/sellers/')
    else:
        form = SellerForm()
        buyer_form = BuyerForm()
    
    context = {
        'title': title,
        'form': form,
        'buyer_form': buyer_form,
        'sellers': sellers_list,
        'buyers': buyers_list,
    }
    return render(request, 'dairyapp/sellers.html', context)

@login_required
def sellerDelete(request, id):
    seller = get_object_or_404(Seller, seller_id=id)
    seller_name = seller.seller_name
    seller.delete()
    messages.success(request, f'Seller "{seller_name}" deleted successfully.')
    return redirect('/sellers/')

@login_required
def sellerUpdate(request, id):
    seller = get_object_or_404(Seller, seller_id=id)
    
    if request.method == 'POST':
        form = SellerForm(request.POST, instance=seller)
        if form.is_valid():
            form.save()
            messages.success(request, 'Seller updated successfully.')
            return redirect('/sellers/')
    else:
        form = SellerForm(instance=seller)
    
    context = {
        'title': 'Update Seller',
        'form': form,
        'seller': seller,
    }
    return render(request, 'dairyapp/seller-update.html', context)

@login_required
def buyerDelete(request, id):
    buyer = get_object_or_404(Buyer, buyer_id=id)
    buyer_name = buyer.buyer_name
    buyer.delete()
    messages.success(request, f'Buyer "{buyer_name}" deleted successfully.')
    return redirect('/sellers/')

@login_required
def buyerUpdate(request, id):
    buyer = get_object_or_404(Buyer, buyer_id=id)
    
    if request.method == 'POST':
        form = BuyerForm(request.POST, instance=buyer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Buyer updated successfully.')
            return redirect('/sellers/')
    else:
        form = BuyerForm(instance=buyer)
    
    context = {
        'title': 'Update Buyer',
        'form': form,
        'buyer': buyer,
    }
    return render(request, 'dairyapp/buyer-update.html', context)

@login_required
def test(request):
    title='TEST'

    if request.method=='POST':
        form=testForm(request.POST)
        if form.is_valid():
            m=form.save(commit=False)
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