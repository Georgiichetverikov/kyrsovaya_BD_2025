from django import forms
from .models import Item, RentalRequest, UserReview
from .models import RentalRequest
from datetime import date





class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['title', 'description', 'category', 'daily_price', 'is_available']


class RentalRequestForm(forms.ModelForm):
    class Meta:
        model = RentalRequest
        fields = ['start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'min': date.today().isoformat()}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'min': date.today().isoformat()}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date < date.today():
                raise forms.ValidationError("Дата начала не может быть в прошлом.")
            if end_date <= start_date:
                raise forms.ValidationError("Дата окончания должна быть позже даты начала.")

        return cleaned_data

class UserReviewForm(forms.ModelForm):
    class Meta:
        model = UserReview
        fields = ['rating', 'text']
        widgets = {
            'rating': forms.Select(choices=UserReview.RATING_CHOICES),
            'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Напишите ваш отзыв...'}),
        }
        labels = {
            'rating': 'Оценка (1–5)',
            'text': 'Отзыв',
        }