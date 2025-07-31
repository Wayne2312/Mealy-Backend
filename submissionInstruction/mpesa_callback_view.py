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
def mpesa_callback_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"M-Pesa callback received: {data}")
            
            callback_metadata = data.get('Body', {}).get('stkCallback', {}).get('CallbackMetadata', {})
            items = callback_metadata.get('Item', [])
            
            result_data = {}
            for item in items:
                result_data[item.get('Name')] = item.get('Value')
            
            amount = result_data.get('Amount')
            mpesa_receipt_number = result_data.get('MpesaReceiptNumber')
            transaction_date = result_data.get('TransactionDate')
            phone_number = result_data.get('PhoneNumber')
            checkout_request_id = data.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')
            
            try:
                order = Order.objects.get(mpesa_checkout_request_id=checkout_request_id)
                
                if data.get('Body', {}).get('stkCallback', {}).get('ResultCode') == 0:
                    order.payment_status = 'completed'
                    order.status = 'confirmed'
                    order.mpesa_receipt_number = mpesa_receipt_number
                    order.transaction_date = transaction_date
                    order.payer_phone = phone_number
                    order.save()
                    
                    print(f"Order {order.id} payment confirmed via M-Pesa callback. Receipt: {mpesa_receipt_number}")
                else:
                    error_message = data.get('Body', {}).get('stkCallback', {}).get('ResultDesc', 'Payment failed')
                    order.payment_status = 'failed'
                    order.status = 'failed'
                    order.payment_error = error_message
                    order.save()
                    
                    print(f"Order {order.id} payment failed via M-Pesa callback. Error: {error_message}")
                
                return JsonResponse({'status': 'Callback processed successfully'}, status=200)
            
            except Order.DoesNotExist:
                print(f"Order with checkout_request_id {checkout_request_id} not found")
                return JsonResponse({'error': 'Order not found'}, status=404)
            
        except json.JSONDecodeError:
            print("Invalid JSON in M-Pesa callback")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print(f"Error processing M-Pesa callback: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)