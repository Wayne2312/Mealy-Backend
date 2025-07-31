from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from app.models import Meal, Order, OrderItem
import json
from datetime import date

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

@csrf_exempt
@login_required
def orders_list_create_view(request):
    """
    Handles GET for listing orders and POST for placing a new order.
    GET: For customers, lists their orders. For admins, lists all orders.
    POST: Allows authenticated users to place an order.
    """
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
            order_items_data = data.get('items')
            if not order_items_data:
                 meal_id = data.get('meal_id')
                 quantity = data.get('quantity', 1)
                 if meal_id:
                     order_items_data = [{'meal_id': meal_id, 'quantity': quantity}]
                 else:
                     return JsonResponse({'error': 'Order items data (items) or meal ID and quantity are required.'}, status=400)

            validated_items = []
            total_amount = 0.0
            for item_data in order_items_data:
                 meal_id = item_data.get('meal_id')
                 quantity = item_data.get('quantity', 1)
                 if not meal_id or not quantity:
                     return JsonResponse({'error': 'Each item must have meal_id and quantity.'}, status=400)
                 try:
                     meal = Meal.objects.get(id=meal_id)
                 except Meal.DoesNotExist:
                     return JsonResponse({'error': f'Meal with ID {meal_id} not found.'}, status=404)

                 price_at_order = meal.price
                 total_item_price = price_at_order * quantity
                 validated_items.append({
                     'meal': meal,
                     'meal_name': meal.name,
                     'price_at_order': price_at_order,
                     'quantity': quantity,
                     'total_item_price': total_item_price
                 })
                 total_amount += float(total_item_price)


            order = Order.objects.create(
                user=request.user,
                customer_name=request.user.first_name if request.user.first_name else request.user.username,
                customer_email=request.user.email,
                status='pending', 
                payment_status='pending',
                total_amount=total_amount
            )

            order_items_to_create = [
                OrderItem(
                    order=order,
                    meal=item['meal'],
                    meal_name=item['meal_name'],
                    price_at_order=item['price_at_order'],
                    quantity=item['quantity'],
                    total_item_price=item['total_item_price']
                )
                for item in validated_items
            ]
            OrderItem.objects.bulk_create(order_items_to_create)

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
    """
    Handles GET for today's revenue. Only accessible by 'admin' users.
    """
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

@csrf_exempt
@login_required
def mpesa_payment_view(request):
    """
    Handles POST for M-Pesa payments.
    Updates order payment status.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')
            phone = data.get('phone')

            if not order_id or not phone:
                return JsonResponse({'error': 'Order ID and phone number are required.'}, status=400)

            try:
                
                order = Order.objects.get(id=order_id, user=request.user)
            except Order.DoesNotExist:
                return JsonResponse({'error': 'Order not found or you do not have permission to pay for it.'}, status=404)


            order.payment_status = 'completed'
            order.status = 'confirmed' 
            order.save()

            print(f"M-Pesa payment simulated for order {order_id} from {phone}. Order status updated.")
            return JsonResponse({
                'success': True,
                'transaction_id': 'MPESA_SIM_TXN_12345',
                'message': 'Payment processed successfully'
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print(f"Error processing M-Pesa payment: {e}")
            return JsonResponse({'error': f'Failed to process payment: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)
