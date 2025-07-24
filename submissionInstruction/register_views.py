# myapp/registration_views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login # Import login if auto-login after registration is desired
from django.contrib.auth.models import User
import json

# Helper function for user serialization (could be in a separate utils.py)
# Import or redefine serialize_user if needed in other files, or keep it here if only used for registration response
def serialize_user(user):
    return {
        'id': user.id,
        'email': user.email,
        'name': user.first_name if user.first_name else user.username,
        'role': 'admin' if user.is_staff else 'customer',
        'is_authenticated': True # Useful if auto-logging in
    }

@csrf_exempt
def register_view(request):
    """
    Handles user registration.
    Expects a POST request with 'email', 'password', 'name', and 'role' in JSON body.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            name = data.get('name')
            role = data.get('role', 'customer') # Default role to 'customer'

            # Basic validation
            if not email or not password or not name:
                return JsonResponse({'error': 'Email, password, and name are required'}, status=400)

            # Check if user with this email already exists
            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'User with this email already exists'}, status=409)

            # Create user. Use email as username.
            user = User.objects.create_user(username=email, email=email, password=password)
            user.first_name = name # Store name in first_name field

            # Assign role based on input
            # For Django's default User, 'admin' usually means is_staff=True
            if role == 'admin':
                user.is_staff = True
                # Consider if superuser is needed for all admins
                # user.is_superuser = True # Based on original code, this was included

            user.save()

            # Optionally log in the user immediately after registration (as per original code)
            # Remove this block if you don't want auto-login
            login(request, user)
            user_data = serialize_user(user)
            # Dummy token for now
            access_token = 'dummy_token_for_now'

            print(f"User {email} registered and logged in successfully.")
            return JsonResponse({
                'message': 'Registration successful',
                'user': user_data,
                'access_token': access_token
            }, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        except Exception as e:
            print(f"An error occurred during registration: {e}")
            return JsonResponse({'error': 'An internal server error occurred during registration'}, status=500)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed for registration'}, status=405)