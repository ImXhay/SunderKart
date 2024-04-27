from django.shortcuts import render
from . models import Product
from django.core.paginator import Paginator

        #homepage 
def index(request):
    feature_products=Product.objects.order_by('priority')[:4]
    latest_product=Product.objects.order_by('-id')[:4]
    context={
        'feature_products':feature_products,
        'latest_product':latest_product
        }

    return render(request, 'home/index.html', context)
        #homepage ends

 #returns product list page
def list_products(request):

    page=1
    if request.GET:
        page=request.GET.get('page',1)

    product_list=Product.objects.order_by('-priority')
    product_pagnator=Paginator(product_list,8)
    product_list=product_pagnator.get_page(page)
    context={'Product': product_list}

    return render(request, 'products/products.html', context)

def detail_product(request,pk):

    product=Product.objects.get(pk=pk)
    context={'product':product}

    return render(request, 'products/product_detail.html', context)