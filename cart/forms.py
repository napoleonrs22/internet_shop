from wsgiref.validate import validator

from django import forms
from django.core.validators import MaxValueValidator
from .models import CartItem

class AddToCartForm(forms.Form):
    size_id = forms.IntegerField(required=False)
    quantity = forms.IntegerField(required=False)

    def __init__(self, *args, product=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.product = product

        if product:
            sizes = product.product_size.filter(stock__gt=0)
            if sizes.exists():
                self.fields['size_id'] = forms.ChoiceField(
                    choices=[(ps.id, ps.size.name) for ps in sizes],
                    required=True,
                    initial=sizes.first().id
                )
class UpdateCartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['quantity']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.product_size:
            max_stock = self.instance.product_size.stock
            self.fields['quantity'].validators.append(MaxValueValidator(max_stock))