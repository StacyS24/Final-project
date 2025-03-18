#Import django modules
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import *
from django.contrib.auth.forms import AuthenticationForm
from django.forms import DateInput

# -------------------- User Signup Form --------------------
class VolunteerSignUpForm(UserCreationForm):
    """
    Form for user registration. Inherits from UserCreationForm.
    Includes additional fields like phone number, location, and postcode.
    """
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 'location','postcode', 'password1', 'password2']
        widgets = {
             # Customizing form input placeholders
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Phone Number'}),
            'location': forms.TextInput(attrs={'placeholder': 'Location'}),
        }


# -------------------- Login Form --------------------
class CustomLoginForm(AuthenticationForm):
    """
    Custom login form that adds placeholder text to the username and password fields.
    """
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={'placeholder': 'Username'})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )


# -------------------- User Profile Update Form --------------------
class UserProfileForm(forms.ModelForm):
    """
    Form for users to update their profile details, including email, phone number,
    location, and profile picture.
    """
    class Meta:
        model = User
        fields = ['email', 'phone_number', 'location', 'profile_picture'] 


# -------------------- Profile Picture Upload Form --------------------
class ProfilePictureForm(forms.ModelForm):
    """
    Form to allow users to upload or update their profile picture.
    """
    class Meta:
        model = User
        fields = ['profile_picture']


# -------------------- Volunteer Preferences --------------------
# Skill options for volunteers
SKILLS_CHOICES = [
    ('fundraising', 'Fundraising'),
    ('event_planning', 'Event Planning'),
    ('public_speaking', 'Public Speaking'),
    ('community_outreach', 'Community Outreach'),
    ('volunteer_management', 'Volunteer Management'),
    ('advocacy', 'Advocacy'),
    ('grant_writing', 'Grant Writing'),
    ('Customer_service', 'Customer service'),
    ('it_support', 'IT Support'),
    ('legal_support', 'Legal Support'),
    ('teaching', 'Teaching/Tutoring'),
    ('mentoring', 'Mentoring'),
    ('workshop_facilitation', 'Workshop Facilitation'),
    ('first_aid', 'First Aid/CPR'),
    ('healthcare_assistance', 'Healthcare Assistance'),
    ('mental_health_support', 'Mental Health Support'),
    ('construction', 'Construction'),
    ('gardening', 'Gardening'),
    ('graphic_design', 'Graphic Design'),
    ('photography', 'Photography'),
    ('videography', 'Videography'),
    ('writing', 'Writing/Content Creation'),
    ('social_media_management', 'Social Media Management'),
    ('Programming', 'Programming'),
    ('translation', 'Translation'),
    ('sign_language', 'Sign Language'),  
    ('animal_care', 'Animal Care'),
    ('environmental_conservation', 'Environmental Conservation'),
    ('sustainability_projects', 'Sustainability Projects'),
]

# Interests choices for volunteer preferences
INTERESTS_CHOICES = [
    ('homelessness_support', 'Homelessness Support'),
    ('poverty_alleviation', 'Poverty Alleviation'),
    ('youth_development', 'Youth Development'),
    ('elderly_support', 'Elderly Support'),
    ('refugee_assistance', 'Refugee Assistance'),
    ('food_security', 'Food Banks'),
    ('crisis_intervention', 'Crisis Intervention'),
    ('special_education', 'Special Education Support'),
    ('mental_health_awareness', 'Mental Health Awareness'),
    ('physical_health', 'Physical Health & Fitness'),
    ('disabilities_support', 'Disabilities Support'),
    ('substance_abuse_recovery', 'Substance Abuse Recovery'),
    ('public_health_advocacy', 'Public Health Advocacy'),
    ('environmental_conservation', 'Environmental Conservation'),
    ('climate_change_advocacy', 'Climate Change Advocacy'),
    ('wildlife_protection', 'Wildlife Protection'),
    ('community_gardening', 'Community Gardening'),
    ('urban_cleanup', 'Urban Cleanup'),
    ('recycling', 'Recycling and Waste Reduction'),
    ('animal_rescue', 'Animal Rescue & Shelters'),
    ('wildlife_conservation', 'Wildlife Conservation'),
    ('farm_animal_care', 'Farm Animal Care'),
    ('veterinary_assistance', 'Veterinary Assistance'),
    ('animal_rights', 'Animal Rights Advocacy'),
    ('gender_equality', 'Gender Equality'),
    ('racial_justice', 'Racial Justice'),
    ('lgbtq_advocacy', 'LGBTQ+ Advocacy'),
    ('disability_rights', 'Disability Rights'),
    ('emergency_medical_assistance', 'Emergency Medical Assistance'),
    ('shelter_housing', 'Shelter and Housing Support'),
    ('search_rescue', 'Search & Rescue Operations'),
]

# Availability options for volunteers
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

# Hours available per week choices for volunteers
HOURS_AVAILABLE_CHOICES = [
    ('1-5', '1-5 hours per week'),
    ('5-10', '5-10 hours per week'),
    ('10-20', '10-20 hours per week'),
    ('20-30', '20-30 hours per week'),
    ('30+', '30+ hours per week'),
    ('full_time', 'Full-Time Commitment'),
    ('flexible', 'Flexible/As Needed'),
]

# Age group options for volunteer preferences
AGE_GROUP_CHOICES = [
    ('under_18', 'Under 18'),
    ('18_24', '18-24 years'),
    ('25_34', '25-34 years'),
    ('35_44', '35-44 years'),
    ('45_54', '45-54 years'),
    ('55_64', '55-64 years'),
    ('65_plus', '65 years and older'),

]

# Languages options for volunteer preferences
LANGUAGES_CHOICES = [
    ('english', 'English'),
    ('spanish', 'Spanish'),
    ('french', 'French'),
    ('german', 'German'),
    ('mandarin', 'Mandarin'),
    ('arabic', 'Arabic'),
    ('hindi', 'Hindi'),
    ('portuguese', 'Portuguese'),
    ('russian', 'Russian'),
    ('japanese', 'Japanese'),
    ('other', 'Other (Please specify)'),
]

# -------------------- Volunteer Preferences Form --------------------
class VolunteerPreferencesForm(forms.ModelForm):
    """
    Form that allows volunteers to specify their preferences regarding:
    - Availability
    - Weekly commitment (hours available)
    - Skills they can contribute
    - Interests they are passionate about
    - Languages they speak
    - Age group they prefer working with
    """

    model = VolunteerPreferences
    availability = forms.ChoiceField(
        choices=AVAILABILITY_CHOICES,
    )

    hours_available = forms.ChoiceField(
        choices=HOURS_AVAILABLE_CHOICES
    )

    age_group = forms.ChoiceField(
        choices=AGE_GROUP_CHOICES, 
    )

    skills = forms.MultipleChoiceField(
        choices=SKILLS_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-input'}),
        required=False,
    )

    interests = forms.MultipleChoiceField(
        choices=INTERESTS_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-input'}),
        required=False,
    )

    languages = forms.MultipleChoiceField(
        choices=LANGUAGES_CHOICES, 
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-input'}),
    )
    
    class Meta:
        model = VolunteerPreferences
        fields = ['availability', 'hours_available', 'age_group','skills', 'interests',  'languages']



# Choices for organization size (Small, Medium, Large)
ORGANISATION_SIZE = [
    ('small (1-10 employees) ', 'Small (1-10 employees)'),
    ('medium(11-50 employees) ', 'Medium (11-50 employees)'),
    ('large (51+ employees)', 'Large (51+ employees)'),
]

# Cause categories for organizations
CAUSE_CATEGORIES_CHOICES = [
    ('education', 'Education'),
    ('health', 'Health'),
    ('environment', 'Environment'),
    ('animal_welfare', 'Animal Welfare'),
    ('human_rights', 'Human Rights'),
    ('social_services', 'Social Services'),
    ('arts_and_culture', 'Arts and Culture'),
    ('community_development', 'Community Development'),
    ('sports', 'Sports'),
    ('disaster_relief', 'Disaster Relief'),
  
]
     
# -------------------- Organization Sign-Up Form --------------------
class OrganisationSignUpForm(UserCreationForm): 
    """
    Form for organization sign-up allowing them to 
    create an account and provide information.
    """
    username = forms.CharField(max_length=150, required=True, label='Username')
    cause_categories = forms.MultipleChoiceField(
        choices=CAUSE_CATEGORIES_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-input'}), 
        required=True
    )
    
    organisation_size = forms.ChoiceField(
        choices=ORGANISATION_SIZE,
        widget=forms.Select(attrs={'class': 'form-control'}), 
        required=True
    )

    organisation_name = forms.CharField(max_length=255, label='Organisation Name', required=True)
    website_url = forms.URLField(label='Website URL', required=False)
    mission_statement = forms.CharField(widget=forms.Textarea, label='Mission Statement', required=True)
    logo = forms.ImageField(required=False, label='Logo')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'location'] 


# -------------------- Organization Profile Form --------------------
class OrganisationProfileForm(forms.ModelForm):
    """
    Form for organizations to update their profile information after registration.
    """
    cause_categories = forms.MultipleChoiceField(
        choices=CAUSE_CATEGORIES_CHOICES,
        widget=forms.CheckboxSelectMultiple(), 
        required=True
    )
    
    organisation_size = forms.ChoiceField(
        choices=ORGANISATION_SIZE,
        widget=forms.Select(attrs={'class': 'form-control'}),  
        required=True
    )

    class Meta:
        model = Organisation
        fields = ['organisation_name','organisation_size', 'cause_categories', 'website_url','mission_statement', 'logo'] 


# -------------------- Custom Login Form --------------------
class CustomLoginForm(AuthenticationForm):
    """
    Custom login form with specific styling and error handling for user authentication.
    """
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autofocus': True
        }),
        label='Username'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        }),
        label='Password'
    )
    # Custom validation to check if the account is active
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError("This account is inactive.", code='inactive')
        

# -------------------- Volunteer Opportunity Form --------------------       
class VolunteerOpportunityForm(forms.ModelForm):
    """
    Form for creating or updating volunteer opportunities with 
    fields for description, skills, location, and duration.
    """

    # Duration choices: predefined options for the duration of the opportunity.
    DURATION_CHOICES = [
        ('One-time', 'One-time'),
        ('Ongoing', 'Ongoing'),
        ('Short-term', 'Short-term'),
        ('Long-term', 'Long-term')
    ]
    # Skills choices: predefined options for the skills required for the opportunity.
    SKILLS_CHOICES = [
        ('fundraising', 'Fundraising'),
        ('event_planning', 'Event Planning'),
        ('public_speaking', 'Public Speaking'),
        ('community_outreach', 'Community Outreach'),
        ('Customer_service', 'Customer service'),
        ('volunteer_management', 'Volunteer Management'),
        ('advocacy', 'Advocacy'),
        ('grant_writing', 'Grant Writing'),
        ('it_support', 'IT Support'),
        ('legal_support', 'Legal Support'),
        ('teaching', 'Teaching/Tutoring'),
        ('mentoring', 'Mentoring'),
        ('workshop_facilitation', 'Workshop Facilitation'),
        ('first_aid', 'First Aid/CPR'),
        ('healthcare_assistance', 'Healthcare Assistance'),
        ('mental_health_support', 'Mental Health Support'),
        ('construction', 'Construction'),
        ('gardening', 'Gardening/Landscaping'),
        ('graphic_design', 'Graphic Design'),
        ('photography', 'Photography'),
        ('videography', 'Videography'),
        ('writing', 'Writing/Content Creation'),
        ('social_media_management', 'Social Media Management'),
        ('Programming', 'Programming'),
        ('translation', 'Translation'),
        ('sign_language', 'Sign Language'),
        ('animal_care', 'Animal Care'),
        ('environmental_conservation', 'Environmental Conservation'),
        ('sustainability_projects', 'Sustainability Projects'),
        ('cooking','cooking')
    ]
    
    duration = forms.ChoiceField(choices=DURATION_CHOICES, label="Duration", help_text="Select the duration of the opportunity.")
    skills_required = forms.MultipleChoiceField(
        choices=SKILLS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label="Required Skills",
        help_text="Select all skills that are relevant for this opportunity."
    )
    phone_number = forms.CharField(
        max_length=15,
        label="Contact Phone Number",
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., +1 234 567 8901'}),
        help_text="Provide a phone number for applicants to contact."
    )

    street_address = forms.CharField(
        max_length=255,
        label="Street address",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., 123 Main St'}),
        help_text="Provide the street address of the opportunity (optional)."
    )
    city = forms.CharField(
        max_length=100,
        label="City",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., London'}),
        help_text="Provide the city (optional)."
    )
    postcode = forms.CharField(
        max_length=10,
        label="Postcode",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., AB1 2CD'}),
        help_text="Provide the postcode (optional)."
    )
    county = forms.CharField(
        max_length=100,
        label="County",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., Greater London'}),
        help_text="Provide the county (optional)."
    )
    country = forms.CharField(
        max_length=100,
        label="Country",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., United Kingdom'}),
        help_text="Provide the country (optional)."
    )

    class Meta:
        model = VolunteerOpportunity
        fields = [
            'title', 'description', 'skills_required', 'location', 'date',
            'duration', 'commitment_level', 'remote', 'phone_number', 'street_address',
            'city','postcode','county','country','urgent'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g., Community Cleanup'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe the opportunity...'}),
            'location': forms.TextInput(attrs={'placeholder': 'e.g., Local Community Center'}),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'commitment_level': forms.TextInput(attrs={'placeholder': 'e.g., Weekly, Monthly'}),
            'urgent': forms.CheckboxInput()
        }
        labels = {
            'title': 'Opportunity Title',
            'description': 'Description',
            'skills_required': 'Required Skills',
            'location': 'Location',
            'date': 'Start Date',
            'commitment_level': 'Commitment Level',
            'remote': 'Remote Option',
            'phone_number': 'Contact Phone Number'
        }
        help_texts = {
            'skills_required': 'List any specific skills or experience that are essential for this role.',
            'remote': 'Select if this opportunity is remote (can be done from home).',
            'date': 'Select the start date for the opportunity.',
            'commitment_level': 'Specify the level of commitment required, e.g., Weekly, Monthly.',
        }

# -------------------- Testimonial Form --------------------
class TestimonialForm(forms.ModelForm):
    """
    Form for submitting testimonials with optional image upload.
    """
    class Meta:
        model = Testimonial
        fields = ['text', 'image']  
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'cols': 50}),
        }

# -------------------- User Search Form --------------------
class userSearchForm(forms.Form):
    """
    Form for searching users by query input.
    """
    query = forms.CharField(label='Search Users', max_length=100)

# -------------------- Message Form --------------------
class MessageForm(forms.ModelForm):
    """
    Form for sending messages to users with recipient validation.
    """

    recipient_name = forms.CharField(max_length=150, label="Recipient Name", required=True)
    
    class Meta:
        model = Message
        fields = ['recipient_name', 'content']

    def clean_recipient_name(self):
        """
        Validate that the recipient exists in the system.
        """
        recipient_name = self.cleaned_data['recipient_name']
        try:
            recipient = User.objects.get(username=recipient_name)
        except User.DoesNotExist:
            raise ValidationError("The user with this name does not exist.")
        return recipient

    def save(self, commit=True):
        """
        Save the message and link it to the recipient.
        """
        message = super().save(commit=False)
        recipient_name = self.cleaned_data['recipient_name']
        recipient = User.objects.get(username=recipient_name)
        message.recipient = recipient
        if commit:
            message.save()
        return message

# -------------------- Profile Privacy Form --------------------
class ProfilePrivacyForm(forms.ModelForm):
    """
    Form for toggling the profile privacy setting.
    """
    profile_is_private = forms.BooleanField(
        required=False, 
        label='Make Profile Private', 
        widget=forms.CheckboxInput()  
    )

    class Meta:
        model = User
        fields = ['profile_is_private']

# -------------------- Report Testimonial Form --------------------
class ReportTestimonialForm(forms.ModelForm):
    """
    Form for reporting a testimonial with a reason for the report.
    """
    class Meta:
        model = TestimonialReport
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe the issue...'}),
        }