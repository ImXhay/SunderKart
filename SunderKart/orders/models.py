from django.db import models
from customers.models import Customer
from products.models import Product
from django.contrib.auth.models import User 

# order date 

class Order(models.Model):
    
    LIVE=0
    DELETE=0
    DELETE_CHOICES=((LIVE,"live"),(DELETE,"delete"))
    
    #order ststus
    CART_STAGE =0
    ORDER_CONFIRMED=1
    ORDER_PROCESSED=2
    ORDER_DELEVERED=3
    ORDER_REJECTED=4
    STATUS_CHOICE=((ORDER_PROCESSED,"ORDER_PROCESSED"),
                   (ORDER_DELEVERED,"ORDER_DELEVERED"), 
                   (ORDER_REJECTED,"ORDER_REJECTED"))  #what the user might change
    
    order_status=models.IntegerField(choices=STATUS_CHOICE, default=CART_STAGE)
    owner=models.ForeignKey(Customer, on_delete=models.SET_NULL,null=True ,related_name="orders")


    delete_status=models.IntegerField(choices=DELETE_CHOICES,default=LIVE)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    total_price=models.FloatField(default=0)

    def __str__(self) -> str:

        return "order-{}-{}".format(self.id,self.owner.name)


class OrderedItem(models.Model):
    product=models.ForeignKey(Product, on_delete=models.SET_NULL,null=True)
    quantity=models.IntegerField(default=1)
    owner=models.ForeignKey(Order, on_delete=models.CASCADE, related_name="added_items")

    
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    transaction_id = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    status = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    # Add any additional fields as needed

    def __str__(self):
        return f"Payment {self.payment_id} - {self.user.username}"