from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import date
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from project import settings
from .models import Meal, DailyMenu, Order, OrderItem

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
def serialize_order(order):
    items_data = []
    for item in order.items.all():
        items_data.append({
            'meal_name': item.meal_name,
            'quantity': item.quantity,
            'price_at_order': float(item.price_at_order),
            'total_item_price': float(item.total_item_price),
            'meal_id': item.meal.id if item.meal else None
        })

    return {
        'id': order.id,
        'user_email': order.user.email,
        'customer_id': order.user.id,
        'order_date': order.order_date.isoformat(),
        'total_amount': float(order.total_amount),
        'status': order.status,
        'payment_status': order.payment_status,
        'items': items_data,
        'customer_name': order.user.first_name if order.user.first_name else order.user.username,
        'date': order.order_date.strftime('%Y-%m-%d %H:%M:%S'),
        'total': float(order.total_amount)
    }



def hello_world(request):
    return HttpResponse("Hello from My Django App!")

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)
                user_data = {
                    'id': user.id,
                    'email': user.email,
                    'name': user.first_name if user.first_name else user.username,
                    'role': 'admin' if user.is_staff else 'customer',
                    'access_token': 'dummy_token_for_now'
                }
                print(f"User {email} logged in successfully.")
                return JsonResponse({'message': 'Login successful', 'user': user_data, 'access_token': user_data['access_token']}, status=200)
            else:
                print(f"Login failed for email: {email}")
                return JsonResponse({'error': 'Invalid credentials'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        except Exception as e:
            print(f"An error occurred during login: {e}")
            return JsonResponse({'error': 'An internal server error occurred'}, status=500)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed for login'}, status=405)

@csrf_exempt
def me_view(request):
    
    if request.method == 'GET':
        if request.user.is_authenticated:
            user = request.user
            user_data = {
                'id': user.id,
                'email': user.email,
                'name': user.first_name if user.first_name else user.username,
                'role': 'admin' if user.is_staff else 'customer',
                'is_authenticated': True
            }
            print(f"Returning user data for: {user.email}")
            return JsonResponse(user_data, status=200)
        else:
            print("User is not authenticated for /api/auth/me")
            return JsonResponse({'message': 'User not authenticated'}, status=401)
    else:
        return JsonResponse({'error': 'Only GET requests are allowed for /auth/me'}, status=405)

@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            name = data.get('name')
            role = data.get('role', 'customer')
            if not email or not password or not name:
                return JsonResponse({'error': 'Email, password, and name are required'}, status=400)
            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'User with this email already exists'}, status=409)
            
            user = User.objects.create_user(username=email, email=email, password=password)
            if role == 'admin':
                user.is_staff = True
                user.is_superuser = True
            user.save()
            login(request, user)

            user_data = {
                'id': user.id,
                'email': user.email,
                'name': user.first_name,
                'role': 'admin' if user.is_staff else 'customer',
                'access_token': 'dummy_token_for_now'
            }
            print(f"User {email} registered and logged in successfully.")
            return JsonResponse({'message': 'Registration successful', 'user': user_data, 'access_token': user_data['access_token']}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        except Exception as e:
            print(f"An error occurred during registration: {e}")
            return JsonResponse({'error': 'An internal server error occurred during registration'}, status=500)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed for registration'}, status=405)
    
    
@csrf_exempt
@login_required 
def meals_list_create_view(request):
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
            if not all(k in data for k in ['name', 'description', 'price', 'category']):
                return JsonResponse({'error': 'Missing required meal fields (name, description, price, category).'}, status=400)
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


@csrf_exempt
@login_required
def orders_list_create_view(request):
    if request.method == 'GET':
        if request.user.is_staff:
            orders = Order.objects.all().prefetch_related('items').select_related('user')
        else:
            orders = Order.objects.filter(user=request.user).prefetch_related('items').select_related('user')
        
        orders_data = [serialize_order(order) for order in orders]
        print(f"Returning {len(orders_data)} orders from database.")
        return JsonResponse(orders_data, safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            meal_id = data.get('meal_id')
            quantity = data.get('quantity', 1)

            if not meal_id or not quantity:
                return JsonResponse({'error': 'Meal ID and quantity are required to place an order.'}, status=400)
            
            try:
                meal = Meal.objects.get(id=meal_id)
            except Meal.DoesNotExist:
                return JsonResponse({'error': 'Meal not found.'}, status=404)

            order = Order.objects.create(
                user=request.user,
                customer_name=request.user.first_name if request.user.first_name else request.user.username,
                customer_email=request.user.email,
                status='pending', 
                payment_status='pending'
            )

            order_item = OrderItem.objects.create(
                order=order,
                meal=meal,
                meal_name=meal.name,
                price_at_order=meal.price,
                quantity=quantity
            )
            
            order.total_amount = order_item.total_item_price
            order.save()

            print(f"Order {order.id} placed successfully by {request.user.email}.")
            return JsonResponse({'message': 'Order placed successfully', 'order': serialize_order(order)}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print(f"Error placing order: {e}")
            return JsonResponse({'error': f'Failed to place order: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
@login_required
def daily_revenue_view(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied. Only administrators can view revenue.'}, status=403)

    if request.method == 'GET':
        today = date.today()
        today_completed_orders = Order.objects.filter(
            order_date__date=today,
            payment_status='completed'
        )
        
        total_revenue = sum(order.total_amount for order in today_completed_orders)
        total_orders = today_completed_orders.count()

        revenue_data = {
            "total_revenue": float(total_revenue),
            "total_orders": total_orders
        }
        print(f"Returning daily revenue for {today}.")
        return JsonResponse(revenue_data)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


