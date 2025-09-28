from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from django.contrib import messages
import csv
from .models import Bouquet, BouquetComposition
from catalog.models import FlowerItem
from .forms import BouquetForm, BouquetCompositionForm

@login_required
def bouquet_list(request):
    bouquets = Bouquet.objects.filter(user=request.user).prefetch_related('composition')
    return render(request, 'bouquets/bouquet_list.html', {'bouquets': bouquets})

@login_required
def create_bouquet(request):
    if request.method == 'POST':
        form = BouquetForm(request.POST)
        if form.is_valid():
            bouquet = form.save(commit=False)
            bouquet.user = request.user
            bouquet.save()
            return redirect('edit_bouquet', pk=bouquet.pk)
    else:
        form = BouquetForm()
    
    return render(request, 'bouquets/bouquet_form.html', {'form': form})

@login_required
def edit_bouquet(request, pk):
    bouquet = get_object_or_404(Bouquet, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = BouquetForm(request.POST, instance=bouquet)
        if form.is_valid():
            form.save()
            return redirect('bouquet_list')
    
    composition_items = bouquet.composition.all()
    composition_form = BouquetCompositionForm(user=request.user)
    
    return render(request, 'bouquets/bouquet_edit.html', {
        'bouquet': bouquet,
        'form': BouquetForm(instance=bouquet),
        'composition_items': composition_items,
        'composition_form': composition_form,
    })

@login_required
def add_composition_item(request, bouquet_pk):
    bouquet = get_object_or_404(Bouquet, pk=bouquet_pk, user=request.user)
    
    if request.method == 'POST':
        form = BouquetCompositionForm(request.POST, user=request.user)
        if form.is_valid():
            composition_item = form.save(commit=False)
            composition_item.bouquet = bouquet
            
            # Check if item already exists in composition
            existing_item = BouquetComposition.objects.filter(
                bouquet=bouquet,
                flower_item=composition_item.flower_item
            ).first()
            
            if existing_item:
                existing_item.quantity += composition_item.quantity
                existing_item.save()
            else:
                composition_item.save()
            
            bouquet.calculate_price()
            
            if request.headers.get('HX-Request'):
                composition_items = bouquet.composition.all()
                return render(request, 'bouquets/partials/composition_list.html', {
                    'composition_items': composition_items,
                    'bouquet': bouquet
                })
    
    return redirect('edit_bouquet', pk=bouquet_pk)

@login_required
def remove_composition_item(request, bouquet_pk, item_pk):
    bouquet = get_object_or_404(Bouquet, pk=bouquet_pk, user=request.user)
    composition_item = get_object_or_404(BouquetComposition, pk=item_pk, bouquet=bouquet)
    
    if request.method == 'POST':
        composition_item.delete()
        bouquet.calculate_price()
        
        if request.headers.get('HX-Request'):
            composition_items = bouquet.composition.all()
            return render(request, 'bouquets/partials/composition_list.html', {
                'composition_items': composition_items,
                'bouquet': bouquet
            })
    
    return redirect('edit_bouquet', pk=bouquet_pk)

@login_required
def delete_bouquet(request, pk):
    bouquet = get_object_or_404(Bouquet, pk=pk, user=request.user)
    
    if request.method == 'POST':
        bouquet.delete()
        return redirect('bouquet_list')
    
    return render(request, 'bouquets/partials/delete_confirm.html', {'bouquet': bouquet})

@login_required
def search_flowers_for_bouquet(request):
    query = request.GET.get('q', '')
    flowers = FlowerItem.objects.filter(
        user=request.user, 
        name__icontains=query
    )[:10]
    
    return JsonResponse({
        'results': [{'id': f.id, 'name': f.name, 'price': str(f.price)} for f in flowers]
    })

@login_required
def import_tilda_csv(request):
    if request.method == 'POST' and request.FILES.get('tilda_csv_file'):
        csv_file = request.FILES['tilda_csv_file']
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file, delimiter='|')
        
        imported_count = 0
        errors = []
        
        # Complete replacement - delete all existing bouquets
        Bouquet.objects.filter(user=request.user).delete()
        
        for row_num, row in enumerate(reader, 2):
            try:
                # Extract relevant fields from Tilda CSV
                bouquet_data = {
                    'tilda_uid': row.get('Tilda UID', '').strip(),
                    'category': row.get('Category', '').strip(),
                    'title': row.get('Title', '').strip(),
                    'description': row.get('Description', '').strip(),
                    'text': row.get('Text', '').strip(),
                    'photo': row.get('Photo', '').strip(),
                    'seo_title': row.get('SEO title', '').strip(),
                    'seo_description': row.get('SEO descr', '').strip(),
                    'seo_keywords': row.get('SEO keywords', '').strip(),
                    'url': row.get('Url', '').strip(),
                }
                
                if bouquet_data['title']:  # Only create if title exists
                    bouquet = Bouquet.objects.create(
                        user=request.user,
                        **bouquet_data
                    )
                    imported_count += 1
                    
            except Exception as e:
                errors.append(f"Строка {row_num}: {str(e)}")
        
        messages.success(request, f'Импортировано {imported_count} букетов из Tilda')
        if errors:
            messages.warning(request, f'Найдено ошибок: {len(errors)}')
        
        return redirect('bouquet_list')
    
    return render(request, 'bouquets/partials/import_tilda_modal.html')

@login_required
def export_tilda_csv(request):
    bouquets = Bouquet.objects.filter(user=request.user).prefetch_related('composition')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="tilda_export.csv"'
    
    # Tilda CSV format columns
    fieldnames = [
        'Tilda UID', 'Brand', 'SKU', 'Mark', 'Category', 'Title', 'Description',
        'Text', 'Photo', 'Price', 'Quantity', 'Price Old', 'Editions', 
        'Modifications', 'External ID', 'Parent UID', 'Weight', 'Length', 
        'Width', 'Height', 'SEO title', 'SEO descr', 'SEO keywords', 'Url', 'Tabs:1'
    ]
    
    writer = csv.DictWriter(response, fieldnames=fieldnames, delimiter='|')
    writer.writeheader()
    
    for bouquet in bouquets:
        writer.writerow({
            'Tilda UID': bouquet.tilda_uid or '',
            'Category': bouquet.category,
            'Title': bouquet.title,
            'Description': bouquet.description,
            'Text': bouquet.text,
            'Photo': bouquet.photo or '',
            'Price': str(bouquet.calculated_price),
            'Quantity': '',  # Leave empty as requested
            'SEO title': bouquet.seo_title or '',
            'SEO descr': bouquet.seo_description or '',
            'SEO keywords': bouquet.seo_keywords or '',
            'Url': bouquet.url or '',
            # Empty fields for Tilda format
            'Brand': '', 'SKU': '', 'Mark': '', 'Price Old': '', 
            'Editions': '', 'Modifications': '', 'External ID': '', 
            'Parent UID': '', 'Weight': '', 'Length': '', 'Width': '', 
            'Height': '', 'Tabs:1': ''
        })
    
    return response
