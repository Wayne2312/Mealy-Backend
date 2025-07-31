from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import date
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from app.models import Order
from project import settings


@csrf_exempt
@login_required
def mpesa_payment_view(request):
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
            
            if phone.startswith('0'):
                phone = '254' + phone[1:]
            elif phone.startswith('+'):
                phone = phone[1:]
            elif not phone.startswith('254'):
                phone = '254' + phone

            mpesa = mpesa()

            amount = int(order.total_amount)
            account_reference = f"ORDER_{order.id}"
            transaction_desc = f"Payment for order #{order.id}"
            
            try:
                response = mpesa.stk_push(
                    phone=phone,
                    amount=amount,
                    account_reference=account_reference,
                    transaction_desc=transaction_desc,
                    callback_url=settings.MPESA_CONFIG['CALLBACK_URL']
                )
                
                if response.get('ResponseCode') == '0':
                    order.mpesa_checkout_request_id = response.get('CheckoutRequestID')
                    order.mpesa_merchant_request_id = response.get('MerchantRequestID')
                    order.save()
                    
                    return JsonResponse({
                        'success': True,
                        'message': 'Payment request sent to your phone. Please complete the transaction.',
                        'checkout_request_id': response.get('CheckoutRequestID'),
                        'merchant_request_id': response.get('MerchantRequestID')
                    }, status=200)
                else:
                    error_message = response.get('ResponseDescription', 'Payment request failed')
                    return JsonResponse({
                        'error': error_message,
                        'mpesa_response': response
                    }, status=400)

            except Exception as e:
                print(f"Error initiating M-Pesa payment: {e}")
                return JsonResponse({
                    'error': 'Failed to initiate payment',
                    'details': str(e)
                }, status=500)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print(f"Error processing M-Pesa payment: {e}")
            return JsonResponse({'error': f'Failed to process payment: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)