from django.db import models
from django.conf import settings

class Item(models.Model):
    CATEGORY_CHOICES = [
        ('bike', 'Транспорт'),
        ('tool', 'Инструмент'),
        ('tech', 'Техника'),
        ('clothes', 'Одежда'),
        ('other', 'Другое'),
    ]
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='items', verbose_name=' Владелец ')
    title = models.CharField(' Название ', max_length=200)
    description = models.TextField(' Описание ', blank=True)
    category = models.CharField(' Категория ', max_length=20, choices=CATEGORY_CHOICES, default='other')
    daily_price = models.DecimalField(' Цена в день, ₽ ', max_digits=10, decimal_places=2)
    is_available = models.BooleanField(' Доступна для аренды ', default=True)
    created_at = models.DateTimeField(' Создана ', auto_now_add=True)
    location = models.CharField('Местоположение', max_length=255, blank=True, help_text='Город, район, адрес')

    class Meta:
        verbose_name = ' Вещь '
        verbose_name_plural = ' Вещи '

    def __str__(self):
        return f'{self.title} ({self.owner.username})'

class RentalRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('approved', 'Одобрена'),
        ('rejected', 'Отклонена'),
        ('returned', 'Возвращена'),
    ]
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='rental_requests', verbose_name=' Вещь ')
    renter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rental_requests', verbose_name=' Арендатор ')
    start_date = models.DateField(' Дата начала аренды ')
    end_date = models.DateField(' Дата окончания аренды ')
    status = models.CharField(' Статус ', max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(' Создана ', auto_now_add=True)

    class Meta:
        verbose_name = ' Заявка на аренду '
        verbose_name_plural = ' Заявки на аренду '

    def __str__(self):
        return f'Аренда {self.item.title} от {self.renter.username}'

class UserReview(models.Model):
    RATING_CHOICES = [
        (1, '1 - плохо'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5 - отлично'),
    ]
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='written_reviews', verbose_name=' Автор отзыва ')
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_reviews', verbose_name=' Кому отзыв ')
    rating = models.PositiveSmallIntegerField(' Оценка ', choices=RATING_CHOICES)
    text = models.TextField(' Текст отзыва ', blank=True)
    created_at = models.DateTimeField(' Создан ', auto_now_add=True)

    class Meta:
        verbose_name = ' Отзыв о пользователе '
        verbose_name_plural = ' Отзывы о пользователях '
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f'Отзыв от {self.from_user} к {self.to_user} ({self.rating})'