from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model, login as auth_login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from .models import Item, RentalRequest, UserReview
from .forms import ItemForm, RentalRequestForm, UserReviewForm
from django.contrib.auth import logout as auth_logout
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Item, RentalRequest
from .forms import RentalRequestForm
from .models import UserReview
from .forms import UserReviewForm


User = get_user_model()

from django.db.models import Q

def item_list(request):
    items = Item.objects.filter(is_available=True)

    # Поиск по названию или описанию
    query = request.GET.get('q')
    if query:
        items = items.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    # Фильтр по категории
    category = request.GET.get('category')
    if category and category != 'all':
        items = items.filter(category=category)

    # Фильтр по цене
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    if price_min:
        items = items.filter(daily_price__gte=price_min)
    if price_max:
        items = items.filter(daily_price__lte=price_max)

    # Сортировка
    sort = request.GET.get('sort')
    valid_sorts = ['-created_at', 'daily_price', '-daily_price']
    if sort in valid_sorts:
        items = items.order_by(sort)

    # Передаём в шаблон все параметры для восстановления формы
    categories = Item.CATEGORY_CHOICES

    return render(request, 'rentals/item_list.html', {
        'items': items,
        'categories': categories,
        'query': query,
        'selected_category': category or 'all',
        'price_min': price_min,
        'price_max': price_max,
        'sort': sort,
    })

def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    return render(request, 'rentals/item_detail.html', {'item': item})


@login_required
def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.owner = request.user
            item.save()
            messages.success(request, 'Вещь успешно добавлена.')
            return redirect('rentals:item_detail', item_id=item.id)
    else:
        form = ItemForm()

    categories = Item.CATEGORY_CHOICES

    return render(request, 'rentals/item_form.html', {
        'form': form,
        'categories': categories
    })

@login_required
def create_rental_request(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    # Проверка: нельзя арендовать свою вещь
    if item.owner == request.user:
        messages.error(request, 'Вы не можете арендовать свою собственную вещь.')
        return redirect('rentals:item_detail', item_id=item.id)

    if request.method == 'POST':
        form = RentalRequestForm(request.POST)
        if form.is_valid():
            # Проверка: не отправлял ли уже пользователь заявку на эту вещь?
            existing_request = RentalRequest.objects.filter(
                item=item,
                renter=request.user,
                status__in=['pending', 'approved']
            ).exists()

            if existing_request:
                messages.error(request, 'Вы уже отправили заявку на эту вещь.')
            else:
                rental_request = form.save(commit=False)
                rental_request.item = item
                rental_request.renter = request.user
                rental_request.save()
                messages.success(request, f'Заявка на аренду вещи "{item.title}" успешно отправлена владельцу.')
            return redirect('rentals:item_detail', item_id=item.id)
        else:

            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')

            return render(request, 'rentals/rental_request_form.html', {
                'form': form,
                'item': item
            })
    else:
        form = RentalRequestForm()

    # Если GET-запрос — отображаем форму
    return render(request, 'rentals/rental_request_form.html', {
        'form': form,
        'item': item
    })

@login_required
def approve_request(request, request_id):
    rental_request = get_object_or_404(RentalRequest, id=request_id, item__owner=request.user)
    if rental_request.status == 'pending':
        rental_request.status = 'approved'
        rental_request.save()
        messages.success(request, f'Заявка на "{rental_request.item.title}" одобрена.')
    else:
        messages.warning(request, 'Невозможно одобрить заявку: статус не "ожидает".')
    return redirect('rentals:owner_requests')

@login_required
def reject_request(request, request_id):
    rental_request = get_object_or_404(RentalRequest, id=request_id, item__owner=request.user)
    if rental_request.status == 'pending':
        rental_request.status = 'rejected'
        rental_request.save()
        messages.info(request, f'Заявка на "{rental_request.item.title}" отклонена.')
    else:
        messages.warning(request, 'Невозможно отклонить заявку: статус не "ожидает".')
    return redirect('rentals:owner_requests')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('rentals:item_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('rentals:item_list')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def user_dashboard(request):
    user = request.user
    my_items_count = Item.objects.filter(owner=user).count()
    my_rentals_count = RentalRequest.objects.filter(renter=user).count()
    owner_requests_count = RentalRequest.objects.filter(item__owner=user).count()
    avg = UserReview.objects.filter(to_user=user).aggregate(Avg('rating'))['rating__avg']
    return render(request, 'rentals/user_dashboard.html', {
        'average_rating': avg,
        'my_items_count': my_items_count,
        'my_rentals_count': my_rentals_count,
        'owner_requests_count': owner_requests_count,
    })

@login_required
def my_items(request):
    items = Item.objects.filter(owner=request.user)
    return render(request, 'rentals/my_items.html', {'my_items': items})

@login_required
def my_rentals(request):
    rentals = RentalRequest.objects.filter(renter=request.user)
    return render(request, 'rentals/my_rentals.html', {'my_rentals': rentals})

@login_required
def owner_requests(request):
    owner_requests = RentalRequest.objects.filter(item__owner=request.user).select_related('item', 'renter')
    return render(request, 'rentals/owner_requests.html', {'owner_requests': owner_requests})


@login_required
def user_rating(request, user_id):
    target_user = get_object_or_404(User, id=user_id)

    # Нельзя оставлять отзыв самому себе
    if target_user == request.user:
        messages.error(request, 'Нельзя оставлять отзыв самому себе.')
        return redirect('rentals:item_list')

    # Получаем все отзывы
    reviews = UserReview.objects.filter(to_user=target_user).select_related('from_user')

    # Считаем среднюю оценку
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    # Проверяем, оставлял ли текущий пользователь отзыв
    existing_review = UserReview.objects.filter(from_user=request.user, to_user=target_user).first()

    if request.method == 'POST':
        form = UserReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.from_user = request.user
            review.to_user = target_user
            review.save()
            messages.success(request, 'Ваш отзыв успешно сохранён.')
            return redirect('rentals:user_rating', user_id=target_user.id)
    else:
        # Если уже есть отзыв — показываем его в форме
        form = UserReviewForm(instance=existing_review) if existing_review else UserReviewForm()

    return render(request, 'rentals/user_rating.html', {
        'target_user': target_user,
        'reviews': reviews,
        'average_rating': avg_rating,
        'form': form,
        'existing_review': existing_review,
    })

def user_profile(request, user_id):
    target = get_object_or_404(User, id=user_id)
    items = Item.objects.filter(owner=target)
    reviews = UserReview.objects.filter(to_user=target)
    avg = reviews.aggregate(Avg('rating'))['rating__avg']
    return render(request, 'rentals/user_profile.html', {
        'target_user': target,
        'user_items': items,
        'reviews': reviews,
        'average_rating': avg,
    })

@login_required
def item_edit(request, item_id):
    item = get_object_or_404(Item, id=item_id, owner=request.user)
    if request.method == 'POST':
        item.title = request.POST.get('title')
        item.description = request.POST.get('description')
        item.category = request.POST.get('category')
        item.daily_price = request.POST.get('daily_price')
        item.is_available = 'is_available' in request.POST
        item.save()
        messages.success(request, 'Вещь успешно обновлена.')
        return redirect('rentals:item_detail', item_id=item.id)
    return render(request, 'rentals/item_form.html', {'item': item})

@login_required
def item_edit(request, item_id):
    """Редактирование существующей вещи владельцем."""
    item = get_object_or_404(Item, id=item_id, owner=request.user)  # Только владелец может редактировать
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Вещь успешно обновлена.')
            return redirect('rentals:item_detail', item_id=item.id)
    else:
        form = ItemForm(instance=item)
    return render(request, 'rentals/item_form.html', {'form': form, 'item': item}) # Передаём item для заголовка

@login_required
def item_delete(request, item_id):
    """Удаление вещи владельцем."""
    item = get_object_or_404(Item, id=item_id, owner=request.user) # Только владелец может удалить
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Вещь успешно удалена.')
        return redirect('rentals:my_items')
    messages.error(request, 'Для удаления вещи используйте форму.')
    return redirect('rentals:my_items')

@login_required
def item_edit(request, item_id):
    item = get_object_or_404(Item, id=item_id, owner=request.user)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Вещь успешно обновлена.')
            return redirect('rentals:item_detail', item_id=item.id)
    else:
        form = ItemForm(instance=item)

    # Передаём категории
    categories = Item.CATEGORY_CHOICES

    return render(request, 'rentals/item_form.html', {
        'form': form,
        'item': item,
        'categories': categories,
    })

def logout_view(request):
    auth_logout(request)
    messages.info(request, "Вы вышли из системы.")
    return redirect('login')

@login_required
def cancel_request(request, request_id):
    """Отмена заявки на аренду пользователем, который её создал."""
    rental_request = get_object_or_404(RentalRequest, id=request_id, renter=request.user)
    if rental_request.status == 'pending':
        rental_request.status = 'cancelled'
        rental_request.save()
        messages.success(request, 'Заявка на аренду отменена.')
    else:
        messages.warning(request, 'Невозможно отменить заявку, статус не "ожидает".')
    return redirect('rentals:my_rentals')