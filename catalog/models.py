from django.db import models
from django.conf import settings

class FlowerItem(models.Model):
    TYPE_CHOICES = [
        ('flower', 'Цветок'),
        ('supply', 'Расходник'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    name = models.CharField('Название', max_length=200)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    type = models.CharField('Тип', max_length=10, choices=TYPE_CHOICES, default='flower')
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)
    
    class Meta:
        verbose_name = 'Элемент каталога'
        verbose_name_plural = 'Элементы каталога'
        ordering = ['name']
        unique_together = ['user', 'name']  # Уникальное название для каждого пользователя
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()}) - {self.price} руб."
