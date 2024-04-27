
from django.shortcuts import render,redirect
import os
from . models import Order,OrderedItem
from products.models import Product
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from razorpay import Client
import hmac
import hashlib
from django.conf import settings
from django.http import JsonResponse
from .models import Order
from django.http import JsonResponse, HttpResponseNotAllowed



def show_cart(request):
    user=request.user
    customer=user.customer_profile
    cart_obj,created=Order.objects.get_or_create(
            owner=customer,
            order_status=Order.CART_STAGE
            )
    context={'cart':cart_obj}
    return render(request, 'cart/cart.html', context)

@login_required(login_url='account')
def add_to_cart(request):

    if request.POST:
        user=request.user
        customer=user.customer_profile
        quantity=int(request.POST.get('quantity'))
        product_id=request.POST.get('product_id')
        cart_obj,created=Order.objects.get_or_create(
            owner=customer,
            order_status=Order.CART_STAGE
            )
        product=Product.objects.get(pk=product_id)
        ordered_item,created=OrderedItem.objects.get_or_create(
            product=product,
            owner=cart_obj
            )
        if created:
            ordered_item.quantity=quantity
            ordered_item.save()
        else:
            ordered_item.quantity=ordered_item.quantity+quantity
            ordered_item.save()
                
    return redirect ('cart')

def remove_item_from_cart(request,pk):
    item=OrderedItem.objects.get(pk=pk)
    if item:
        item.delete()
    return redirect('cart')



@login_required
def checkout_cart(request): 

    if request.POST:
        try:
            
            user = request.user
            customer = user.customer_profile
            total = float(request.POST.get('total'))
            order_obj, created = Order.objects.get_or_create(
                owner=customer,
                order_status=Order.CART_STAGE
                )
          
            if order_obj:
                
                client = Client(auth=(os.getenv('RAZORPAY_KEY_ID'), os.getenv('RAZORPAY_KEY_SECRET')))
                
                # Calculate amount in paisa (multiply by 100)
                amount = int(total * 100)
                
                # Create Razorpay order
                data = {
                    'amount': amount,
                    'currency': 'INR',
                }
                order = client.order.create(data=data)
                
                # Update context with Razorpay options
                options = {
                    'key': os.getenv('RAZORPAY_KEY_ID'),
                    'amount': order['amount'],
                    'currency': order['currency'],
                    'name': 'SUNDER KART',
                    'description': 'Product Order',
                    'order_id': order['id'],
                    'handler': 'payment_success',  # JS function for success
                    'total' : total
                }                
                return render(request, 'cart/payment.html', context=options)
            else:
                status_message = "Unable to process. Add item to cart."
                messages.error(request, status_message)
                return redirect('cart')

        except Exception as e:
            print(f'Checkout exception: {e}')
            status_message = "Unable to process your order. Please try again."
            messages.error(request, status_message)
            return redirect('cart')

    return redirect('cart')

def process_payment(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    if request.method == 'POST':
        # Retrieve parameters from POST request
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        # Construct signature to verify
        signature = hmac.new(
            settings.RAZORPAY_KEY_SECRET.encode(),
            f'{razorpay_order_id}|{razorpay_payment_id}'.encode(),
            hashlib.sha256
        ).hexdigest()

        # Compare generated signature with received signature
        if signature == razorpay_signature:
            try:
                user = request.user
                customer = user.customer_profile
                total = float(request.POST.get('total'))
                order_obj= Order.objects.get(
                owner=customer,
                order_status=Order.CART_STAGE
                )
                if order_obj:
                    order_obj.order_status = Order.ORDER_CONFIRMED
                    order_obj.save()

                    return redirect('payment_success')
                else:
                
                    status_message = "Unable to process. Add item to cart."
                    messages.error(request, status_message)
                    return redirect('cart')
                      
            except Order.DoesNotExist:
                # Handle the case where no order is found with the provided ID
                return JsonResponse({'error': 'Order not found'}, status=404)
        else:
            # Payment signature is invalid, handle the error
            return JsonResponse({'error': 'Invalid payment signature'}, status=400)

    # Handle invalid request methods
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required(login_url='account')
def view_orders(request):
    user = request.user
    customer = user.customer_profile
    all_orders = Order.objects.filter(owner=customer).exclude(order_status=Order.CART_STAGE)
    context={'orders': all_orders}

    return render(request, 'orders/orders.html', context)
    
def payment_success(request):

    return render(request, 'cart/payment_success.html')