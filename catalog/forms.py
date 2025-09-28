from django import forms
from .models import FlowerItem

class FlowerItemForm(forms.ModelForm):
    class Meta:
        model = FlowerItem
        fields = ['name', 'price', 'type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Название',
            'price': 'Цена (руб)',
            'type': 'Тип',
        }
