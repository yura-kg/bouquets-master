from django import forms
from .models import Bouquet, BouquetComposition
from catalog.models import FlowerItem

class BouquetForm(forms.ModelForm):
    class Meta:
        model = Bouquet
        fields = [
            'tilda_uid', 'category', 'title', 'description', 'text', 'photo',
            'seo_title', 'seo_description', 'seo_keywords', 'url'
        ]
        widgets = {
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'photo': forms.URLInput(attrs={'class': 'form-control'}),
            'seo_title': forms.TextInput(attrs={'class': 'form-control'}),
            'seo_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'seo_keywords': forms.TextInput(attrs={'class': 'form-control'}),
            'url': forms.TextInput(attrs={'class': 'form-control'}),
            'tilda_uid': forms.TextInput(attrs={'class': 'form-control'}),
        }

class BouquetCompositionForm(forms.ModelForm):
    flower_item = forms.ModelChoiceField(
        queryset=FlowerItem.objects.none(),  # Will be set in __init__
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Цветок/Расходник'
    )
    
    class Meta:
        model = BouquetComposition
        fields = ['flower_item', 'quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['flower_item'].queryset = FlowerItem.objects.filter(user=user)
