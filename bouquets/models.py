from django.db import models
from django.conf import settings

class Bouquet(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    
    # Tilda fields
    tilda_uid = models.CharField('Tilda UID', max_length=100, blank=True, null=True)
    category = models.CharField('Категория', max_length=200)
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    text = models.TextField('Текст', blank=True)
    photo = models.URLField('Фото', blank=True)
    
    # SEO fields
    seo_title = models.CharField('SEO заголовок', max_length=200, blank=True)
    seo_description = models.TextField('SEO описание', blank=True)
    seo_keywords = models.TextField('SEO ключевые слова', blank=True)
    url = models.SlugField('URL', max_length=200, blank=True)
    
    # Calculated price
    calculated_price = models.DecimalField(
        'Рассчитанная цена', 
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)
    
    class Meta:
        verbose_name = 'Букет'
        verbose_name_plural = 'Букеты'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def calculate_price(self):
        """Calculate price based on composition"""
        total = sum(
            item.flower_item.price * item.quantity 
            for item in self.composition.all()
        )
        self.calculated_price = total
        self.save()
        return total

class BouquetComposition(models.Model):
    bouquet = models.ForeignKey(
        Bouquet,
        on_delete=models.CASCADE,
        related_name='composition',
        verbose_name='Букет'
    )
    flower_item = models.ForeignKey(
        'catalog.FlowerItem',
        on_delete=models.CASCADE,
        verbose_name='Элемент'
    )
    quantity = models.PositiveIntegerField('Количество', default=1)
    
    class Meta:
        verbose_name = 'Состав букета'
        verbose_name_plural = 'Состав букетов'
        unique_together = ['bouquet', 'flower_item']
    
    def __str__(self):
        return f"{self.flower_item.name} x{self.quantity}"
