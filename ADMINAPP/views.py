from datetime import date, timedelta
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from USERAPP.models import UserRole,UserProfile
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
import pyotp
from django.db import transaction
from USERAPP.views import ProfilePictureForm
from .models import Warehouse, UserRole
from django.contrib.auth.decorators import login_required


@login_required
def adminindex(request):
    # Get the total number of users
    total_users = User.objects.count()

    # Get the number of active users (users with is_active=True)
    active_users = User.objects.filter(is_active=True).count()

    # Get the number of inactive users (users with is_active=False)
    inactive_users = User.objects.filter(is_active=False).count()

    # Get the total number of warehouse managers (based on role)
    total_warehouse_managers = User.objects.filter(userrole__role='warehouse manager').count()

    # Get the number of active warehouse managers (based on role and is_active=True)
    active_warehouse_managers = User.objects.filter(userrole__role='warehouse manager', is_active=True).count()

    # Get the number of inactive warehouse managers (based on role and is_active=False)
    inactive_warehouse_managers = User.objects.filter(userrole__role='warehouse manager', is_active=False).count()

    # Get the total number of inventory controllers (based on role)
    total_inventory_controllers = User.objects.filter(userrole__role='inventory controller').count()

    # Get the number of active inventory controllers (based on role and is_active=True)
    active_inventory_controllers = User.objects.filter(userrole__role='inventory controller', is_active=True).count()

    # Get the number of inactive inventory controllers (based on role and is_active=False)
    inactive_inventory_controllers = User.objects.filter(userrole__role='inventory controller', is_active=False).count()

    context = {
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'total_warehouse_managers': total_warehouse_managers,
        'active_warehouse_managers': active_warehouse_managers,
        'inactive_warehouse_managers': inactive_warehouse_managers,
        'total_inventory_controllers': total_inventory_controllers,
        'active_inventory_controllers': active_inventory_controllers,
        'inactive_inventory_controllers': inactive_inventory_controllers,
    }

    return render(request, 'Admin/adminindex.html', context)




@login_required
def userspanel(request):
    users_with_roles = User.objects.select_related('userrole').all()
    context = {'users_with_roles': users_with_roles}
    return render(request, 'Admin/USERSpanel.html', context)



@login_required
def add_user(request):
    if request.method == 'POST':
        # Retrieve form data
        email = request.POST['email']
        first_name = request.POST['FirstName']
        last_name = request.POST['LastName']
        role = request.POST['userrole']

        # Get the profile picture from the form
        profile_picture = request.FILES.get('userImage')
        totp_secret = pyotp.random_base32()
        otp = pyotp.TOTP(totp_secret, digits=8)
        otp_value = otp.now()  # Get the current OTP value
        # Create a new user
        user = User(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(str(otp_value))  # Set the OTP value as the user's password
        user.save()

        # Create or update user's role
        user_role, created = UserRole.objects.get_or_create(user=user)
        user_role.role = role
        user_role.save()

        # Create or update user's profile
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        user_profile.profile_picture = profile_picture
        user_profile.save()

        subject = 'Your account has been created'
        message = f'Your account has been created successfully. Use OTP: {otp_value} to login. Login link:- http://127.0.0.1:8000/'
        from_email = settings.EMAIL_HOST_USER  # Your sender email address
        recipient_list = [user.email]

        send_mail(subject, message, from_email, recipient_list)

        # Redirect to a success page or any other desired URL
        return redirect('userspanel')

    return redirect('userspanel')



@login_required
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
    
    

@login_required
def delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        
        if user.is_active:
            # Deactivate the user by setting the 'is_active' field to False
            user.is_active = False
            user.save()

            # Send a deactivation email to the user
            subject = 'Your account has been deactivated'
            message = 'Your account has been deactivated.'
            from_email = settings.EMAIL_HOST_USER  # Your sender email address
            recipient_list = [user.email]

            send_mail(subject, message, from_email, recipient_list)
        
            return JsonResponse({'message': 'User deactivated successfully'})
        else:
            return JsonResponse({'message': 'User is already inactive'})
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)




@login_required
def activate_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if user.is_active:
        return JsonResponse({'message': 'User is already active'})
    
    user.is_active = True
    user.save()
    
    # Send an activation email to the user
    subject = 'Your account has been activated'
    message = 'Your account has been activated successfully.'
    from_email = settings.EMAIL_HOST_USER  # Your sender email address
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)
    
    response_data = {'message': 'User activated successfully', 'is_active': user.is_active}
    print(response_data)  # Print the response data for debugging
    
    return JsonResponse(response_data)

    
    
    
@login_required
def warehousepanel(request):
    # Query all warehouse objects
    warehouses = Warehouse.objects.all()

    # Query available warehouse managers and inventory controllers
    available_managers = UserRole.objects.filter(role='warehouse manager', is_allocated=False, user__is_active=True)
    available_controllers = UserRole.objects.filter(role='inventory controller', is_allocated=False, user__is_active=True)

    # Pass the warehouse objects and available users to the template context
    context = {
        'warehouses': warehouses,
        'available_managers': available_managers,
        'available_controllers': available_controllers,
    }

    return render(request, 'Admin/WAREHOUSESPANEL.html', context)




@login_required
def add_warehouse(request):
    if request.method == 'POST':
        # Get data from the POST request
        warehouse_name = request.POST.get('warehouse_name')
        location = request.POST.get('location')
        address = request.POST.get('address')
        num_sectors = request.POST.get('num_sectors')
        manager_allocated_id = request.POST.get('manager_allocated')
        print(manager_allocated_id)
        controller_allocated_id = int(request.POST.get('controller_allocated'))

        # Initialize manager and controller as None
        manager = None
        controller = None

        # Retrieve the manager and controller based on their IDs
        if manager_allocated_id:
            try:
                manager_user = User.objects.get(id=manager_allocated_id)
                manager = UserRole.objects.get(user=manager_user)
                print("Found Manager:", manager)
                manager.is_allocated = True  # Update is_allocated field to True
                manager.save()  # Save the updated manager object
            except User.DoesNotExist:
                print("User not found")
            except UserRole.DoesNotExist:
                print("Manager not found")

        if controller_allocated_id:
            try:
                controller_user = User.objects.get(id=controller_allocated_id)
                controller = UserRole.objects.get(user=controller_user)
                print("Found Controller:", controller)
                controller.is_allocated = True  # Update is_allocated field to True
                controller.save()  # Save the updated controller object
            except User.DoesNotExist:
                print("User not found")
            except UserRole.DoesNotExist:
                print("Controller not found")

        # Create a new Warehouse object
        warehouse = Warehouse(
            warehouse_name=warehouse_name,
            location=location,
            address=address,
            num_sectors=num_sectors,
            manager=manager,  # Set the manager field
            controller=controller,  # Set the controller field
        )

        # Save the warehouse object to the database
        warehouse.save()

        # Redirect to a success page or another appropriate view
        return redirect('warehousepanel')  # Change 'success_page' to your desired URL name

    # Render the template for GET requests
    return render(request, 'Admin/warehousepanel.html')

@login_required
def admin_profile(request):
    user = request.user

    # Try to get the UserProfile or create it if it doesn't exist
    user_profile = get_object_or_404(UserProfile, user=user)

    if request.method == 'POST':
        # Handle profile picture update separately using the form
        profile_picture_form = ProfilePictureForm(request.POST, request.FILES, instance=user_profile)
        if profile_picture_form.is_valid():
            profile_picture_form.save()

        # Extract first name and last name from the full name
        
        
        full_name = request.POST.get('nameupdate', '')

        if ' ' in full_name:
            # Split the full name into first name and last name
            first_name, last_name = full_name.split(' ', 1)
            user.first_name = first_name
            user.last_name = last_name
        else:
            # If there is no space, consider the whole name as the first name
            user.first_name = full_name
            user.last_name = ''

        user.save()

        # Update user profile fields
        if request.POST.get('dobupdate'):
            user_profile.date_of_birth = request.POST.get('dobupdate')
        if request.POST.get('countryupdate'):
            user_profile.country = request.POST.get('countryupdate')
        if request.POST.get('stateupdate'):
            user_profile.state = request.POST.get('stateupdate')
        if request.POST.get('cityupdate'):
            user_profile.city = request.POST.get('cityupdate')
        if request.POST.get('distupdate'):
            user_profile.district = request.POST.get('distupdate')
        if request.POST.get('numupdate'):
            user_profile.phone_no = request.POST.get('numupdate')
        if request.POST.get('adrupdate'):
            user_profile.addressline1 = request.POST.get('adrupdate')
        if request.POST.get('adrlupdate'):
            user_profile.addressline2 = request.POST.get('adrlupdate')
        if request.POST.get('pinupdate'):
            user_profile.pin_code = request.POST.get('pinupdate')
            

        with transaction.atomic():
            user.save()
            user_profile.save()
        return redirect('profile_view')

    user_profile.date_of_birth = user_profile.date_of_birth.strftime('%Y-%m-%d') if user_profile.date_of_birth else ''
    sixteen_years_ago = date.today() - timedelta(days=16*365)
    sixtyfive_years_ago = date.today() - timedelta(days=65*365)
    context = {
        'user': user,
        'user_profile': user_profile,
        'sixteen_years_ago': sixteen_years_ago.strftime('%Y-%m-%d'),  # Format the date as YYYY-MM-DD
        'sixtyfive_years_ago': sixtyfive_years_ago.strftime('%Y-%m-%d'),
        'profile_picture_form': ProfilePictureForm(instance=user_profile),  # Pass the form to the template
    }
    return render(request, 'Admin/adminaccount.html', context)