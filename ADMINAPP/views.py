from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from USERAPP.models import UserRole,UserProfile
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404


def adminindex(request):
    user = request.user  # Get the current logged-in user
    return render(request, 'adminindex.html')

def userspanel(request):
    users_with_roles = User.objects.select_related('userrole').all()
    context = {'users_with_roles': users_with_roles}
    return render(request, 'USERSpanel.html', context)

def add_user(request):
    if request.method == 'POST':
        # Retrieve form data
        username = request.POST['userName']
        email = request.POST['email']
        first_name = request.POST['FirstName']
        last_name = request.POST['LastName']
        password = request.POST['Password']
        role = request.POST['userrole']

        # Get the profile picture from the form
        profile_picture = request.FILES.get('userImage')

        # Create a new user
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=make_password(password),  # Hash the password
        )
        user.save()

        # Create or update user's role
        user_role, created = UserRole.objects.get_or_create(user=user)
        user_role.role = role
        user_role.save()

        # Create or update user's profile
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        user_profile.profile_picture = profile_picture
        user_profile.save()

        # Redirect to a success page or any other desired URL
        return redirect('userspanel')

    return redirect('userspanel')


def get_user_details(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        try:
            user_profile = UserProfile.objects.get(user=user)
            user_data = {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'password': user.password,  # Note: Passwords should not be sent to the client for security reasons.
                'user_image_url': user_profile.profile_picture.url if user_profile.profile_picture else None,  # Get the profile picture URL
            }
            return JsonResponse(user_data)
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'User profile not found'}, status=404)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    
    
def delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        
        # Deactivate the user by setting the 'is_active' field to False
        user.is_active = False
        user.save()
        
        return JsonResponse({'message': 'User deactivated successfully'})
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    
def activate_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if user.is_active:
        return JsonResponse({'message': 'User is already active'})
    
    user.is_active = True
    user.save()
    
    response_data = {'message': 'User activated successfully', 'is_active': user.is_active}
    print(response_data)  # Print the response data for debugging
    
    return JsonResponse(response_data)
    
    
def update_user(request, user_id=None):
    if request.method == "POST":
        # Process the form data, whether it's an update or addition

        # Extract user_id from the form data or data attributes
        user_id = request.POST.get("user-id", None)

        # Collect updated data from the form
        username = request.POST.get("userName")
        email = request.POST.get("email")
        first_name = request.POST.get("FirstName")
        last_name = request.POST.get("LastName")
        password = request.POST.get("Password")
        userrole = request.POST.get("userrole")
        # Add more fields as needed

        # Depending on whether user_id is None, it's an addition or update
        if user_id is None:
            # Add a new user
            # You can create a new User instance here and set its attributes

            # Example:
            # user = User(username=username, email=email, first_name=first_name, last_name=last_name, password=password)
            # user.save()

            # After saving the new user, you can create/update the associated UserProfile if needed

            return JsonResponse({"message": "User added successfully"})
        else:
            # Update an existing user based on user_id
            try:
                user = User.objects.get(id=user_id)

                # Update the user's attributes
                user.username = username
                user.email = email
                user.first_name = first_name
                user.last_name = last_name
                # Update other user attributes as needed

                user.save()

                # Optionally, you can update the associated UserProfile if needed
                # userProfile = UserProfile.objects.get(user=user)
                # userProfile.country = country
                # userProfile.district = district
                # Update other UserProfile attributes as needed
                # userProfile.save()

                return JsonResponse({"message": "User updated successfully"})
            except User.DoesNotExist:
                return JsonResponse({"error": "User not found"}, status=404)

    else:
        # Handle GET requests, if needed
        # You can return a rendered template for the form here
        return redirect('userspanel')  # Replace with your template name
    
    
    
def delete_multiple_users(request):
    if request.method == 'POST':
        # Get user IDs from the request
        user_ids = request.POST.getlist('user_ids[]')

        # Set the is_active field to null for the selected users
        User.objects.filter(id__in=user_ids).update(is_active=False)

        # Return a JSON response to indicate successful deletion
        return JsonResponse({'message': 'Users deleted successfully'})

    # If the request method is not POST, return an error JSON response
    return JsonResponse({'error': 'Invalid request method'}, status=400)