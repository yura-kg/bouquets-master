from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db import IntegrityError
from django.contrib import messages
import csv
from .models import FlowerItem
from .forms import FlowerItemForm

@login_required
def flower_catalog(request):
    flower_items = FlowerItem.objects.filter(user=request.user)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        flower_items = flower_items.filter(name__icontains=search_query)
    
    return render(request, 'catalog/flower_catalog.html', {
        'flower_items': flower_items,
        'search_query': search_query
    })

@login_required
def add_flower_item(request):
    if request.method == 'POST':
        form = FlowerItemForm(request.POST)
        if form.is_valid():
            flower_item = form.save(commit=False)
            flower_item.user = request.user
            try:
                flower_item.save()
                if request.headers.get('HX-Request'):
                    return render(request, 'catalog/partials/flower_item_row.html', {'item': flower_item})
                return redirect('flower_catalog')
            except IntegrityError:
                form.add_error('name', 'Элемент с таким названием уже существует')
    else:
        form = FlowerItemForm()
    
    return render(request, 'catalog/partials/flower_item_form.html', {'form': form})

@login_required
def edit_flower_item(request, pk):
    flower_item = get_object_or_404(FlowerItem, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = FlowerItemForm(request.POST, instance=flower_item)
        if form.is_valid():
            form.save()
            if request.headers.get('HX-Request'):
                return render(request, 'catalog/partials/flower_item_row.html', {'item': flower_item})
            return redirect('flower_catalog')
    else:
        form = FlowerItemForm(instance=flower_item)
    
    return render(request, 'catalog/partials/flower_item_form.html', {'form': form, 'edit': True})

@login_required
def delete_flower_item(request, pk):
    flower_item = get_object_or_404(FlowerItem, pk=pk, user=request.user)
    
    if request.method == 'POST':
        flower_item.delete()
        if request.headers.get('HX-Request'):
            return HttpResponse('')
        return redirect('flower_catalog')
    
    return render(request, 'catalog/partials/delete_confirm.html', {'item': flower_item})

@login_required
def search_flowers(request):
    query = request.GET.get('q', '')
    flowers = FlowerItem.objects.filter(
        user=request.user, 
        name__icontains=query
    )[:10]  # Limit results
    
    return JsonResponse({
        'results': [{'id': f.id, 'name': f.name, 'price': str(f.price)} for f in flowers]
    })

@login_required
def import_csv(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        
        imported_count = 0
        errors = []
        
        # First, delete all existing items for complete replacement
        FlowerItem.objects.filter(user=request.user).delete()
        
        for row_num, row in enumerate(reader, 2):  # Start from line 2 (after header)
            try:
                name = row.get('Title', '').strip()
                price = row.get('Price', '0').strip()
                
                if name and price:
                    # Try to convert price to decimal
                    try:
                        price_value = float(price)
                    except ValueError:
                        price_value = 0
                    
                    FlowerItem.objects.create(
                        user=request.user,
                        name=name,
                        price=price_value,
                        type='flower'  # Default type
                    )
                    imported_count += 1
                    
            except Exception as e:
                errors.append(f"Строка {row_num}: {str(e)}")
        
        messages.success(request, f'Импортировано {imported_count} элементов')
        if errors:
            messages.warning(request, f'Найдено ошибок: {len(errors)}')
        
        return redirect('flower_catalog')
    
    return render(request, 'catalog/partials/import_modal.html')
