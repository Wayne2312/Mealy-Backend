from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Meal, OrderItem, DailyMenu

@csrf_exempt
@login_required
def meal_detail_view(request, meal_id):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied. Only administrators can manage meals.'}, status=403)
    if request.method == 'DELETE':
        try:
            meal = Meal.objects.get(id=meal_id)
            pending_orders = OrderItem.objects.filter(
            meal=meal,
            order__status__in=['pending', 'preparing', 'ready']
            ).exists()
            if pending_orders:
                return JsonResponse({
                    'error': 'Cannot delete meal with pending orders. Complete or cancel all orders first.'
                }, status=400)
            daily_menus = DailyMenu.objects.filter(meals=meal)
            for menu in daily_menus:
                menu.meals.remove(meal)
                print(f"Removed meal '{meal.name}' from daily menu for {menu.date}")
            meal_name = meal.name
            meal.delete()
            print(f"Meal '{meal_name}' deleted successfully")
            return JsonResponse({
                'message': f'Meal "{meal_name}" deleted successfully'
            }, status=200)
        except Meal.DoesNotExist:
            return JsonResponse({'error': 'Meal not found'}, status=404)
        except Exception as e:
            print(f"Error deleting meal: {e}")
            return JsonResponse({'error': f'Failed to delete meal: {str(e)}'}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)