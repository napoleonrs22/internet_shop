from django.shortcuts import get_list_or_404
from django.views.generic import TemplateView, DetailView
from django.http import HttpResponse
from django.template.response import TemplateResponse
from .models import Product, Category, Size
from django.db.models import Q


class IndexView(TemplateView):
    template_name = 'main/base.html'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = None

        return context
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'main/hpme_content.html', context)
        return TemplateResponse(request, self.template_name, context) 
    

class CatalogView(TemplateView):
    template = 'main/base.html'
    

    FILTER_MAPPING = {
        'color': lambda queryset, value: queryset.filter(color___iexact=value),
        'min_price': lambda queryset, value: queryset.filter(price_gte=value),
        'max_price': lambda queryset, value: queryset.filter(price_lte=value),
        'size': lambda queryset, value: queryset.filter(product_sizes__size__name=value),
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_date(**kwargs)
        category_slug = kwargs.get('category_slug')
        categories = Category.objects.all()
        products = Product.objects.all().order_by('-created_at')
        current_category = None

        if category_slug:
            current_category = get_list_or_404(Category, slug=category_slug)
            products = products.filter(category=current_category)

        query = self.request.GET.get('q') 
        if query:
            products = products.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query) 
            )
        filter_params  = {}

        for param, filter_func in self.FILTER_MAPPING.items():
            value = self.request.GET.get(param)
            if value:
                products = filter_func(products, value)
                filter_params[param] = value
            else:
                filter_params[param] = ''
        filter_params['q'] = query or ''
        context.update({
            'categories': categories,
            'products': products,
            'current_category': current_category,
            'filter_params': filter_params,
            'sizes': Size.objects.all(),
            'search_query': query or '',
        })
        if self.request.GET.get('show_search') =='true':
            context['show_search'] = True
        elif self.request.GET.get('reset_search') == 'true':
            context['show_search'] = True

        return context
    