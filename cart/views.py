from urllib import request

from django.shortcuts import render
from  django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404,redirect
from django.views.generic import View
from  django.template.response import TemplateResponse
from  django.contrib import messages
from django.db import transaction
from main.models import  Product, ProductSize
from .models import Cart, CartItem
from  .forms import AddToCartForm, UpdateCartItemForm
import json


class CartMixin:
    def get_cart(self, request):
        if hasattr(request, 'cart'):
            return request.cart
        if not request.session.session_key:
            request.session.create()

        cart, created = Cart.objects.get_or_create(
            session_key=request.session.session_key,
        )
        request.session['cart_id'] = cart.id
        request.session.modified = True
        return cart

class AddToCartView(View, CartMixin):
    @transaction.atomic
    def post(self, request,slug):
        cart = self.get_cart(request)
        product = get_object_or_404(Product, slug=slug)
        form = AddToCartForm(request.POST, product=product)

        if not form.is_valid():
            return JsonResponse({
                'error': 'Invalid form data',
                'errors':form.errors,
            },status=400)
        size_id = form.cleaned_data['size_id']
        if size_id:
            product_size = get_object_or_404(
                ProductSize,
                id=size_id,
                product=product,
            )
        else:
            product_size = product.product_sizes.filter(stock__gt=0).first()
            if not product_size:
                return JsonResponse({
                    'error': 'No product size found',
                    'errors': form.errors,
                },status=400)
        quantity = form.cleaned_data['quantity']
        if product_size.stock < quantity:
            return JsonResponse({
                'error': 'Not enough stock',
            },status=400)
        existing_item = cart.item.filter(
            product=product,
            product__size=product_size,
        ).first()

        if existing_item:
            total_quantity = existing_item.quantity
            if total_quantity > product_size.stock:
                return JsonResponse({
                    "error": f"Can't add {quantity} more stock",
                },status=400)

        cart_item = cart.add_product(product,product_size, quantity=quantity,)

        request.session['cart_id'] = cart.id
        request.session.modified = True

        if request.headers.get('HX-Request'):
            return  redirect('cart-cart_model')
        else:
            return  JsonResponse({
                'success': True,
                'total_items': cart.total_items,
                'message': f'{product.name} added to cart',
                'cart_item_id':cart_item.id
            })



            '''product = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']

            product.quantity = quantity
            product.save()
            '''