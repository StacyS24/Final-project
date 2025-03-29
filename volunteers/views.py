from .recommendations import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.views import LoginView
from django.views.decorators.csrf import csrf_exempt
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import messages
from django.http import Http404
from django.db.models import Max
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.http import JsonResponse
from django.db.models import Count
from django.urls import reverse
from datetime import timedelta
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
from .forms import *
from .models import *
import os
import requests
from dotenv import load_dotenv
from .sample_data import sample_data
# Create your views here.
sample_data()
def signup(request):
    """
    This view handles the signup process for any user.
    """
    return render(request,'index.html')

@csrf_exempt
def organisationSignUp(request):
    """
    This view handles the signup process for an organization.
    - If the request method is POST, it validates and saves the user and organization data.
    - Creates a new user, assigns it a user type of 'organisation', and saves the organization instance.
    - After saving, it logs in the new user and redirects to the organization's profile page.
    """
    if request.method == 'POST':
        form = OrganisationSignUpForm(request.POST, request.FILES)

        if form.is_valid():   
            user = form.save(commit=False)
            user.user_type = 'organisation'  
            user.save()  
              
            organisation = Organisation(
                user=user,  
                organisation_name=form.cleaned_data['organisation_name'], 
                website_url=form.cleaned_data['website_url'],
                mission_statement=form.cleaned_data['mission_statement'],
                cause_categories=form.cleaned_data['cause_categories'],
                organisation_size=form.cleaned_data['organisation_size'],
                logo=form.cleaned_data.get('logo'),  
            )

            organisation.save()             
            login(request, user)
            return redirect('organisation-profile')
    else:
        form = OrganisationSignUpForm()
    return render(request, 'organisation-sign-up.html', {'form': form})

@csrf_exempt
def volunteerSignUp(request):
    """
    This view handles the signup process for a volunteer.
    - If the request method is POST, it validates and saves both the user data and volunteer preferences.
    - Creates a new user with the type 'volunteer' and saves the user's preferences.
    - After saving, the user is logged in and redirected to their profile page.
    """
    if request.method == 'POST': 
        user_form = VolunteerSignUpForm(request.POST)
        preferences_form = VolunteerPreferencesForm(request.POST)

        if user_form.is_valid() and preferences_form.is_valid():
            user = user_form.save()  
            preferences = preferences_form.save(commit=False)
            user.user_type = 'volunteer'
            preferences.user = user  
            preferences.save()          
            user.is_active = True
            user.save()   
            login(request, user)
            return redirect('volunteer-profile') 
    else:
        user_form = VolunteerSignUpForm()
        preferences_form = VolunteerPreferencesForm()

    return render(request, 'volunteer-sign-up.html', {
        'user_form': user_form,
        'preferences_form': preferences_form,
    })



@csrf_exempt

def login_view(request):
    """
    This view handles the login process for users.
    - If the request method is POST, it authenticates the user based on the provided username and password.
    - If the credentials are correct, the user is logged in, if authentication fails an error message is shown.
    """
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():          
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
         
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                if user.user_type == 'volunteer':
                    return redirect('volunteer-profile')
                elif user.user_type == 'organisation':
                    return redirect('organisation-profile')
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})


def logout(request):
    """
    This view lets a user log out. Then redirects them back to the sign up page. 
    """
    auth_logout(request)  
    return redirect('sign-up') 


def format_text(value):
    """
    This function formats a string or a list of strings by replacing underscores with spaces and capitalizing each word.
    """
    if isinstance(value, str):
        return value.replace("_", " ").title()  
    elif isinstance(value, list):  
        return [item.replace("_", " ").title() for item in value]
    return value 


def volunteerProfile(request):
    """
    This view displays the volunteer's profile page.
    - If the user is not authenticated, they are redirected to the login page.
    - Retrieves the volunteer's preferences, saved and applied opportunities, notifications, and awarded badges.
    - Also computes similarity scores for opportunity recommendations based on the user's skills, location, and interests.
    - Generates both content-based and collaborative recommendations for volunteer opportunities.
    """
    if not request.user.is_authenticated:
        return redirect('login')
    
    user = request.user
    volunteer_preferences = get_object_or_404(VolunteerPreferences, user=user)
    Saved_opportunities = VolunteerOpportunity.objects.filter(saved_by=user)
    applied_opportunities = VolunteerOpportunity.objects.filter(applied_by=user).prefetch_related('volunteerapplications_set')
    notifications = Notifications.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')
    awarded_badges  = AwardBadge.objects.filter(volunteer=request.user).select_related('badge')
    
    applied_opps_with_status = []
    for opportunity in applied_opportunities:
        application = opportunity.volunteerapplications_set.filter(user=user).first()
        status = application.status if application else 'Not Applied' 
        applied_opps_with_status.append({
            'opportunity': opportunity,
            'status': status,         
        })
    
    user = request.user
    users, preferences, opportunities = load_data(user)  
    users_skills, users_location, opportunities_skills, opportunities_location,user_interests  = preprocess_data(users, preferences, opportunities)   
    similarity_scores = compute_similarity(users_skills, users_location, opportunities_skills, opportunities_location,users,user_interests ) 
    recommendations = recommend_opportunities(similarity_scores, opportunities)
    interaction_matrix = build_interaction_matrix()
    collaborative_recommendations = recommend_collaborative(user.id, interaction_matrix, opportunities)
    formatted_skills = format_text(volunteer_preferences.skills)
    formatted_interests = format_text(volunteer_preferences.interests)
    formatted_age_group = format_text(volunteer_preferences.age_group)

    context = {
        'user': user,
        'volunteer_preferences': volunteer_preferences,
        'skills': formatted_skills,
        'interests': formatted_interests,
        'availability': volunteer_preferences.availability,
        'hours_available': volunteer_preferences.hours_available,
        'age_group': formatted_age_group,
        'languages': volunteer_preferences.languages,
        'saved_opportunities': Saved_opportunities,
        'applied_opportunities': applied_opps_with_status,
        'notifications': notifications,
        'recommendations': recommendations,
        'collaborative_recommendations': collaborative_recommendations,
        'badges': awarded_badges
    }

    return render(request, 'volunteer-profile.html', context)


def upload_profile_picture(request):
    """
    This view allows a user to upload or update their profile picture.
    """
    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
        else:
            form = ProfilePictureForm(instance=request.user)
    return redirect('volunteer-profile')


@login_required
def organisationProfile(request):
    """
    This view displays the organization's profile page.
    - Retrieves the organization associated with the logged-in user.
    - Displays the organization's opportunities and unread notifications.
    - The cause categories are formatted to replace underscores with spaces and capitalize words.
    """
    organisation = get_object_or_404(Organisation, user=request.user)
    notifications = Notifications.objects.filter(recipient=request.user, is_read=False)
    opportunities = VolunteerOpportunity.objects.filter(organisation=organisation) 
    cause_categories = [category.replace("_", " ").title() for category in organisation.cause_categories]
    context = {
        'organisation': organisation,
        'opportunities': opportunities,
        'notifications': notifications,
        'cause_categories': cause_categories  
    }

    return render(request, 'organisation-profile.html', context)


@login_required
def editVolunteerProfile(request):
    """
    This view allows a volunteer to edit their profile.
    - The form processes user data, preferences, and privacy settings.
    - If the form is valid, it saves the changes and redirects to the volunteer's profile page, Otherwise, it renders the forms with the current data.
    """
    user = request.user
    volunteer_preferences = get_object_or_404(VolunteerPreferences, user=user)

    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, request.FILES, instance=user)
        preferences_form = VolunteerPreferencesForm(request.POST, instance=volunteer_preferences)
        privacy_form = ProfilePrivacyForm(request.POST, instance=user)

        if user_form.is_valid() and preferences_form.is_valid() and privacy_form.is_valid():
            user_form.save()
            preferences_form.save()
            privacy_form.save()
            return redirect('volunteer-profile')
    else:
        user_form = UserProfileForm(instance=user)
        preferences_form = VolunteerPreferencesForm(instance=volunteer_preferences)
        privacy_form = ProfilePrivacyForm(instance=user)

    context = {
        'profile_form': user_form,
        'preferences_form': preferences_form,
        'privacy_form': privacy_form
    }

    return render(request, 'edit-volunteer-profile.html', context)

@login_required
def editOrganisationProfile(request): 
    """
    This view allows an organization to edit its profile.
    - The form processes the organization's data.
    - If the form is valid, it saves the changes and redirects to the organization's profile page, Otherwise, it renders the form with the current data.
    """
    organisation = Organisation.objects.get(user=request.user)
    if request.method == 'POST':    
        organisation_form = OrganisationProfileForm(request.POST, request.FILES, instance=organisation)       
        if organisation_form.is_valid():         
            organisation_form.save()
            return redirect('organisation-profile')
    else:    
        organisation_form = OrganisationProfileForm(instance=organisation)
    context = {   
        'organisation_form': organisation_form
    }
    return render(request, 'edit-organisation-profile.html', context)


def home(request):
    """
    This view renders the home page with a list of all volunteer opportunities.
    """
    opportunities = VolunteerOpportunity.objects.all()       
    context = {
        'opportunities' : opportunities,
    }
    return render(request,'home.html', context)

def urgent_opportunties(request):
    """
    This view renders a page that shows only the urgent volunteer opportunities.
    - It filters the opportunities to show those marked as urgent, and orders them by creation date.
    """
    urgent_opportunities = VolunteerOpportunity.objects.filter(urgent=True).order_by('-created_at')
    return render(request, 'urgent_opportunties.html', {'urgent_opportunities': urgent_opportunities})


def search_users(request):
    """
    This view allows searching for users based on a query.
    - The search checks for usernames, skills, or interests matching the query.
    - It returns search results and also displays volunteer opportunities.
    """
    search_form = userSearchForm()
    results = []
    opportunities = VolunteerOpportunity.objects.all()   

    if 'query' in request.GET:
        query = request.GET['query']
        results = User.objects.filter(
            Q(username__icontains=query) |
            Q(volunteerpreferences__skills__icontains=query) |
            Q(volunteerpreferences__interests__icontains=query)
        ).distinct()

    return render(request, 'home.html', {'form': search_form, 'results': results, 'opportunities': opportunities})


@login_required
def postVolunteerOpportunity(request):
    """
    This view allows an organization to post a new volunteer opportunity.
    """
    if request.method == 'POST':
        form = VolunteerOpportunityForm(request.POST)
        if form.is_valid():
            opportunity = form.save(commit=False)
            opportunity.organisation = request.user.organisation  
            opportunity.save()
            return redirect('organisation-profile') 
    else:
        form = VolunteerOpportunityForm()

    return render(request, 'post-volunteer-opportunity.html', {'form': form})


AVAILABILITY_CHOICES = [
    ('daily', 'Daily'),
    ('weekly', 'Weekly'),
    ('monthly', 'Monthly'),
    ('weekends', 'Weekends Only'),
    ('weekdays', 'Weekdays Only'),
    ('evenings', 'Evenings'),
    ('mornings', 'Mornings'),
    ('flexible', 'Flexible/As Needed'),
    ('one_time', 'One-Time Events'),
]


def all_oppourtunities(request):
    """
    Retrieves and displays all volunteer opportunities.
    Filters the opportunities based on optional query parameters: location, remote status, and commitment level.
    """  
    opportunities = VolunteerOpportunity.objects.all()
    
    location = request.GET.get('location')
    remote = request.GET.get('remote')
    commitment = request.GET.get('commitment')
    
    if location:
        opportunities = opportunities.filter(location__icontains=location)
    if remote:
        opportunities = opportunities.filter(remote=(remote == 'yes'))
    if commitment:
        opportunities = opportunities.filter(commitment_level__icontains=commitment) 
    return render(request, 'all-oppourtunities.html', {'opportunities': opportunities})


def delete_opportunity(request, opportunity_id):
    """
    Allows an organization to delete a volunteer opportunity they have posted.
    Redirects to the organization profile page after successful deletion.
    """
    opportunity = get_object_or_404(VolunteerOpportunity, id=opportunity_id)
    if request.user == opportunity.organisation.user:
        opportunity.delete()
        return redirect('organisation-profile')
    return redirect('opportunity-details', opportunity_id=opportunity_id)


@login_required
def save_opportunity(request, opportunity_id):
    """
    Allows the user to save a volunteer opportunity.
    If the opportunity is already saved, it removes it from the user's saved list.
    """
    opportunity = get_object_or_404(VolunteerOpportunity, id=opportunity_id)
    saved, created = SavedOpportunities.objects.get_or_create(user=request.user, opportunity=opportunity)

    if not created: 
        saved.delete()

    return redirect('volunteer-profile')

@csrf_exempt
def apply_opportunity(request, opportunity_id):
    """
    Allows the user to apply for a volunteer opportunity.
    - If the user has already applied, it withdraws their application.
    - Sends success messages based on the application status.
    - Awards badges to users who apply for 1 or 5 opportunities.
    """
    opportunity = get_object_or_404(VolunteerOpportunity, id=opportunity_id)
    application, created = VolunteerApplications.objects.get_or_create(user=request.user, opportunity=opportunity)

    if created:
        messages.success(request, f"Successfully applied to {opportunity.title}")
    else:
        application.delete()
        messages.info(request, f"Withdrawn application from {opportunity.title}")
    
    if VolunteerApplications.objects.filter(user=request.user).count() == 1:
        badge = Badges.objects.get(name="Opportunity seeker")
        if not AwardBadge.objects.filter(volunteer=request.user, badge=badge).exists():
            AwardBadge.objects.create(volunteer=request.user, badge=badge)
            messages.success(request, "Congratulations! You've earned the 'Opportunity Seeker' badge!")
    if VolunteerApplications.objects.filter(user=request.user).count() == 5:
        badge = Badges.objects.get(name="Opportunity volunteer")
        if not AwardBadge.objects.filter(volunteer=request.user, badge=badge).exists():
            AwardBadge.objects.create(volunteer=request.user, badge=badge)
            messages.success(request, "Congratulations! You've earned the 'Opportunity Volunteer' badge!")

    return redirect('volunteer-profile')


def opportunity_detail(request, opportunity_id): 
    """
    Displays information about a speific volunteer opportunity.
    - Includes a list of applications to the opportunity.
    - Renders the 'opportunity-detail.html' template with the opportunity and applications.
    """
    opportunity = get_object_or_404(VolunteerOpportunity, id=opportunity_id)  
    applications = VolunteerApplications.objects.filter(opportunity=opportunity)

    return render(request, 'opportunity-detail.html', {
        'opportunity': opportunity,
        'applications': applications,
        'user': request.user,
    })


@login_required
def confirm_volunteer(request, application_id):
    """
    Allows an organization to confirm a volunteer for an opportunity.
    Sends a notification to the volunteer upon confirmation.
    """
    application = get_object_or_404(VolunteerApplications, id=application_id)

    if request.user == application.opportunity.organisation.user:
        application.status = 'accepted'
        application.save()     
        notification_message = f"You have been confirmed for the opportunity '{application.opportunity.title}'!"

        Notifications.objects.create(
            recipient=application.user,  
            message=notification_message,
            related_opportunity=application.opportunity,  
            created_at=timezone.now(),
            is_read=False
        )

    return redirect('opportunity-detail', opportunity_id=application.opportunity.id)



def send_message(request, recipient_id):
    """
    Allows a user to send a message to another user.
    Upon submitting the form, the message is saved, and the user is redirected to the recipient's profile.
    """
    try:
        recipient = User.objects.get(id=recipient_id) 
    except User.DoesNotExist:
        raise Http404("User not found")

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.recipient = recipient
            message.sender = request.user  
            message.save()   
            return redirect('user_detail', user_id=recipient.id)
    else:    
        form = MessageForm(initial={'recipient_name': recipient.username})
    return render(request, 'chat.html', {'form': form, 'recipient': recipient})


@login_required
def chat_with_sender(request, sender_id):
    """
    Allows a user to view and send messages to a specific sender.
    Retrieves all previous messages between the user and the sender, sorts them by timestamp, and displays them.
    """
    sender = get_object_or_404(User, id=sender_id)
    
    messages = Message.objects.filter(
        sender=request.user, recipient=sender
    ) | Message.objects.filter(
        sender=sender, recipient=request.user
    )
    
    messages = messages.order_by('timestamp')
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            message = Message(sender=request.user, recipient=sender, content=content)
            message.save()
            return redirect('chat_with_sender', sender_id=sender.id)
    
    return render(request, 'chat.html', {'sender': sender, 'messages': messages})



@login_required

def view_messages(request):
    """
    Displays a list of all conversations the user has had, with the last message in each conversation.
    Retrieves and orders conversations by the most recent message time.
    """  
    conversations = Message.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).values('sender', 'recipient').annotate(last_message_time=Max('timestamp')).order_by('-last_message_time')

    user_ids = set()
    for conversation in conversations:
        user_ids.add(conversation['sender'])
        user_ids.add(conversation['recipient'])
    user_ids.discard(request.user.id) 

    conversations = [
        {
            'recipient': User.objects.get(id=user_id),
            'last_message': Message.objects.filter(
                Q(sender=request.user, recipient=user_id) | Q(sender=user_id, recipient=request.user)
            ).order_by('-timestamp').first()
        }
        for user_id in user_ids
    ]

    return render(request, 'message_list.html', {'conversations': conversations})


@receiver(post_save, sender=VolunteerApplications)
def notify_organisations(sender,instance, created, **kwargs):
    """
    Notifies the organization when a volunteer applies for their opportunity.
    Creates a notification for the organization about the new application.
    """
    if created:
        opportunity = instance.opportunity
        organisation_user = opportunity.organisation.user
        volunteer = instance.user  

        notification_message = f"{volunteer.username} has applied for '{opportunity.title}'."
        Notifications.objects.create(
            recipient=organisation_user,
            message=notification_message,
            related_opportunity=opportunity
        )


def testimonial_list(request):
    """
    Displays a list of all testimonials, ordered by creation date.
    Highlights the testimonial with the most likes by showing it as the top testimonial.
    """
    testimonials = Testimonial.objects.all().order_by('-created_at')
    top_testimonial = Testimonial.objects.annotate(like_count=Count('likes')).order_by('-like_count').first()
    return render(request, 'testimonial_list.html', {'testimonials': testimonials,'top_testimonial': top_testimonial })


def testimonial_detail(request, testimonial_id):
    """
    Displays a detailed view of a specific testimonial, including comments.
    Allows users to like or unlike the testimonial, and to add comments.
    """
    testimonial = get_object_or_404(Testimonial, id=testimonial_id)
    if request.method == 'POST':
        if 'like' in request.POST:
            if request.user in testimonial.likes.all():
                testimonial.likes.remove(request.user)
            else:
                testimonial.likes.add(request.user)
        elif 'comment_text' in request.POST:
            comment_text = request.POST['comment_text']
            Comment.objects.create(testimonial=testimonial, user=request.user, text=comment_text)

    comments = testimonial.comments.all()
    return render(request, 'testimonial_detail.html', {'testimonial': testimonial, 'comments': comments})


def add_comment(request, testimonial_id):   
    """
    Allows a user to add a comment to a specific testimonial.
    Displays the updated comments after the new comment is added.
    """
    testimonial = get_object_or_404(Testimonial, id=testimonial_id)
    if request.method == 'POST':
        comment_text = request.POST.get('comment_text')    
        if comment_text:
            Comment.objects.create(
                testimonial=testimonial,
                user=request.user,
                text=comment_text
            )
    comments = testimonial.comments.all()  
    return render(request, 'testimonial_detail.html', {
        'testimonial': testimonial,
        'comments': comments
    })

@login_required
def like_testimonial(request, testimonial_id):
    """
    Allows a user to like or unlike a specific testimonial.
    """
    testimonial = get_object_or_404(Testimonial, id=testimonial_id)
    if request.user in testimonial.likes.all():
        testimonial.likes.remove(request.user)
    else:
        testimonial.likes.add(request.user)

    return redirect('testimonial_detail', testimonial_id=testimonial.id)


def submit_testimonial(request):
    """
    Handles the submission of a testimonial. 
    - It saves the testimonial and awards badges based on the number of testimonials the user has submitted.
    - Redirects the user to the testimonial list page.
    """
    if request.method == 'POST':
        form = TestimonialForm(request.POST, request.FILES)  
        if form.is_valid():
            testimonial = form.save(commit=False)
            testimonial.user = request.user  
            testimonial.save()
            
            if Testimonial.objects.filter(user=request.user).count() == 1:
                badge = Badges.objects.get(name="First Impression") 
                AwardBadge.objects.create(volunteer=request.user, badge=badge)
                messages.success(request, "Congratulations! You've earned the 'First Impression' badge!")
            if Testimonial.objects.filter(user=request.user).count() == 3:
                badge = Badges.objects.get(name="Reviewer") 
                AwardBadge.objects.create(volunteer=request.user, badge=badge)
                messages.success(request, "Congratulations! You've earned the 'Reviewer' badge!")
            if Testimonial.objects.filter(user=request.user).count() == 10:
                badge = Badges.objects.get(name="Top Contributor") 
                AwardBadge.objects.create(volunteer=request.user, badge=badge)
                messages.success(request, "Congratulations! You've earned the 'Top Contributor' badge!")
            return redirect('testimonial_list')  
    else:
        form = TestimonialForm()
    return render(request, 'submit_testimonial.html', {'form': form})

def report_testimonial(request, testimonial_id):
    """
    Allows the user to report a testimonial. 
    After submitting the report, the user is redirected to the testimonial detail page.
    """
    testimonial = get_object_or_404(Testimonial, id=testimonial_id)   
    if request.method == 'POST':
        form = ReportTestimonialForm(request.POST)
        
        if form.is_valid():
            report = form.save(commit=False)
            report.testimonial = testimonial
            report.user = request.user
            report.save()
            return redirect('testimonial_detail', testimonial_id=testimonial.id)
    
    else:
        form = ReportTestimonialForm()

    return render(request, 'report_testimonial.html', {'form': form, 'testimonial': testimonial})



def user_detail(request, user_id):
    """
    Displays information about a user. Retrieves user details, preferences (if a volunteer), and 
    organization details (if an organization). Also displays a message form and user profile privacy status.
    """
    user = get_object_or_404(User, id=user_id)
    form = MessageForm(request.POST)   
    preferences = None
    organisation = None

    if user.user_type == 'volunteer':
        preferences = VolunteerPreferences.objects.filter(user=user).first()
    
    elif user.user_type == 'organisation':
        organisation = get_object_or_404(Organisation, user=user)

    is_private = user.profile_is_private

    return render(request, 'user_detail.html', {
        'user': user,
        'preferences': preferences,
        'organisation': organisation,
        'form': form,
        'is_private': is_private
    })


def mark_notification_as_read(request, notification_id):
    """
    Marks a notification as read and deletes it. 
    The user is then redirected based on their user type 
    """
    notification = get_object_or_404(Notifications, id=notification_id, recipient=request.user)
    
    notification.is_read = True
    notification.delete()
   
    if request.user.user_type == 'organisation':
        return redirect('organisation-profile')
    else:
        return redirect('volunteer-profile')

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
def get_coordinates(address):
    """
    This function takes an address as input, makes a request to the Google Geocoding API to retrieve the coordinates
    for that address, and returns the coordinates if successful.
    
    Parameters:
    address (str): The address for which coordinates are to be fetched.
    
    Returns:
    tuple: A tuple containing the latitude and longitude if the request is successful, otherwise (None, None).
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    url = f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}'
    
    response = requests.get(url)
    data = response.json()
    
    if data['status'] == 'OK':
        # Get the latitude and longitude
        latitude = data['results'][0]['geometry']['location']['lat']
        longitude = data['results'][0]['geometry']['location']['lng']
        return latitude, longitude
    else:
        print(f"Error fetching coordinates for {address}: {data['status']}")
        return None, None 

def update_opportunities_with_coordinates(opportunity_id):
    """
    This function updates the coordinates (latitude and longitude) of a specific volunteer opportunity by calling 
    the get_coordinates function. It fetches the address of the opportunity and updates its latitude and longitude 
    if coordinates are successfully fetched from the Geocoding API.
    
    Parameters:
    opportunity_id (int): The ID of the opportunity to update.
    
    Returns:
    None: Updates the opportunity record in the database and logs success or failure.
    """
    opportunity= VolunteerOpportunity.objects.get(id = opportunity_id)
    
    address = f"{opportunity.street_address}, {opportunity.city}, {opportunity.country}"
    latitude, longitude = get_coordinates(address)
        
    if latitude and longitude:
        opportunity.latitude = latitude
        opportunity.longitude = longitude
        opportunity.save()
        print(f"Updated {opportunity.title} with coordinates: ({latitude}, {longitude})")
    else:
        print(f"Failed to get coordinates for {opportunity.title}") 






