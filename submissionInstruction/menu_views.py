# myapp/menu_views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from app.models import Meal, DailyMenu
import json
from datetime import date


def serialize_meal(meal):
    return {
        'id': meal.id,
        'name': meal.name,
        'description': meal.description,
        'price': float(meal.price), 
        'category': meal.category,
        'image_url': meal.image_url,
        'created_at': meal.created_at.isoformat(),
        'updated_at': meal.updated_at.isoformat(),
    }

@csrf_exempt
@login_required
def meals_list_create_view(request):
    """
    Handles GET for listing meals from the database and POST for creating a new meal in the database.
    Only allows 'admin' users to create meals.
    """
 
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied. Only administrators can manage meals.'}, status=403)

    if request.method == 'GET':
     
        meals = Meal.objects.all()
        
        meals_data = [serialize_meal(meal) for meal in meals]
        print("Returning meals list from database.")
        return JsonResponse(meals_data, safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
         
            required_fields = ['name', 'description', 'price', 'category']
            if not all(k in data for k in required_fields):
                return JsonResponse({'error': f'Missing required meal fields ({", ".join(required_fields)}).'}, status=400)

          
            meal = Meal.objects.create(
                name=data.get('name'),
                description=data.get('description'),
                price=data.get('price'),
                category=data.get('category'),
                image_url=data.get('image_url') 
            )
            print(f"Meal '{meal.name}' created and saved to database.")
            
            return JsonResponse({
                'message': 'Meal created successfully',
                'meal': serialize_meal(meal)
            }, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        except Exception as e:
            print(f"Error creating meal: {e}")
            return JsonResponse({'error': f'Failed to create meal: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
@login_required 
def daily_menu_view(request):
    """
    Handles GET for today's menu and POST for creating/updating a daily menu.
    Only allows 'admin' users to create/update menus.
    """
    if request.method == 'GET':
        today = date.today()
        try:
        
            daily_menu = DailyMenu.objects.get(date=today)
            meals_on_menu = [serialize_meal(meal) for meal in daily_menu.meals.all()]
            print(f"Returning daily menu for {today} from database.")
            return JsonResponse({"date": today.isoformat(), "meals": meals_on_menu})
        except DailyMenu.DoesNotExist:
            print(f"No daily menu found for {today}.")
            return JsonResponse({"date": today.isoformat(), "meals": []})
        except Exception as e:
            print(f"Error fetching daily menu: {e}")
            return JsonResponse({'error': 'An internal server error occurred while fetching menu'}, status=500)

    elif request.method == 'POST':
        if not request.user.is_staff:
            return JsonResponse({'error': 'Permission denied. Only administrators can create daily menus.'}, status=403)
        try:
            data = json.loads(request.body)
            menu_date_str = data.get('date')
            meal_ids = data.get('meal_ids', [])

            if not menu_date_str or not isinstance(meal_ids, list):
                return JsonResponse({'error': 'Missing date or meal_ids for daily menu.'}, status=400)

            menu_date = date.fromisoformat(menu_date_str)

        
            daily_menu, created = DailyMenu.objects.get_or_create(date=menu_date)

        
            daily_menu.meals.clear()
            meals_to_add = Meal.objects.filter(id__in=meal_ids)
            daily_menu.meals.add(*meals_to_add)

            print(f"Daily menu for {menu_date} {'created' if created else 'updated'} with {len(meals_to_add)} meals.")
            return JsonResponse({'message': f'Daily menu for {menu_date} created/updated successfully'}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except ValueError:
            return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)
        except Exception as e:
            print(f"Error creating daily menu: {e}")
            return JsonResponse({'error': f'Failed to create/update daily menu: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)