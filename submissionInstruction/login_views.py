# myapp/login_views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
import json

# Helper function for user serialization (could be in a separate utils.py)
def serialize_user(user):
    return {
        'id': user.id,
        'email': user.email,
        'name': user.first_name if user.first_name else user.username,
        'role': 'admin' if user.is_staff else 'customer',
        'is_authenticated': True
    }

@csrf_exempt
def login_view(request):
    """
    Handles user login.
    Expects a POST request with 'email' and 'password' in JSON body.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            # Django's default User model uses 'username'. We use email as username.
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                user_data = serialize_user(user)
                # Dummy token for now
                access_token = 'dummy_token_for_now'
                print(f"User {email} logged in successfully.")
                return JsonResponse({
                    'message': 'Login successful',
                    'user': user_data,
                    'access_token': access_token
                }, status=200)
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
    """
    Returns details about the currently authenticated user.
    Requires user to be logged in.
    """
    if request.method == 'GET':
        if request.user.is_authenticated:
            user_data = serialize_user(request.user)
            print(f"Returning user data for: {request.user.email}")
            return JsonResponse(user_data, status=200)
        else:
            print("User is not authenticated for /api/auth/me")
            return JsonResponse({'message': 'User not authenticated'}, status=401)
    else:
        return JsonResponse({'error': 'Only GET requests are allowed for /auth/me'}, status=405)

# Note: Logout view is missing in the original file. You might want to add it here or in a separate auth utilities file.
# @csrf_exempt
# def logout_view(request):
#     logout(request)
#     return JsonResponse({'message': 'Logged out successfully'}, status=200)