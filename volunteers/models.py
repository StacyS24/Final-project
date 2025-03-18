from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# Custom user model that extends AbstractUser to support user types (volunteer, organisation) and additional fields.
class User(AbstractUser):
    # Choices for user types
    USER_TYPES = [
        ('volunteer', 'Volunteer'),
        ('organisation', 'Organisation')
    ]
    username = models.CharField(max_length=150, unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    location = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    user_created_at = models.DateTimeField(auto_now_add=True)
    saved_opportunities = models.ManyToManyField('VolunteerOpportunity', related_name='saved_by', through='SavedOpportunities')
    applied_opportunities = models.ManyToManyField('VolunteerOpportunity', related_name='applied_by', through='VolunteerApplications')
    profile_is_private = models.BooleanField(default=False)
    postcode = models.CharField(max_length=10)
     
    # User's groups and permissions (for Django's auth system)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='volunteers_user_set',  
        blank=True,
        help_text='The groups this user belongs to.',
        
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='volunteers_user_set',  
        blank=True,
        help_text='Specific permissions for this user.',
        
    )

# Organisation model, representing an organization
class Organisation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organisation_name = models.CharField(max_length=50, null=True,unique=True,) 
    website_url = models.URLField(blank=True, null=True)
    mission_statement = models.TextField()
    cause_categories = models.JSONField() 
    organisation_size = models.CharField(max_length=50)
    logo = models.ImageField(upload_to='organisation_logos/', blank=True, null=True)

    def __str__(self):
        return self.organisation_name

# VolunteerOpportunity model to represent volunteer opportunities posted by organisations.
class VolunteerOpportunity(models.Model):
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)  
    title = models.CharField(max_length=200)
    description = models.TextField()
    skills_required = models.JSONField()  
    location = models.CharField(max_length=100)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postcode = models.CharField(max_length=10)  
    county = models.CharField(max_length=100, null=True, blank=True)  
    country = models.CharField(max_length=100, default='United Kingdom') 
    date = models.DateField()
    duration = models.CharField(max_length=100)  
    commitment_level = models.CharField(max_length=100)  
    remote = models.BooleanField(default=False) 
    contact_info = models.JSONField(null=True, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField(null=True, blank=True)  
    longitude = models.FloatField(null=True, blank=True)
    urgent = models.BooleanField(default=False)


# VolunteerPreferences model to store preferences specific to a volunteer user.
class VolunteerPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) 
    skills = models.JSONField(default=list)  
    interests = models.JSONField(default=list)  
    availability = models.CharField(max_length=100)
    hours_available = models.CharField(max_length=100)
    age_group = models.CharField(max_length=50)
    languages = models.JSONField(default=list) 

# VolunteerApplications model to track the status of applications made by volunteers
class VolunteerApplications(models.Model):
    # Choices for application status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    ]  
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    opportunity = models.ForeignKey(VolunteerOpportunity, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

# SavedOpportunities model to track which opportunities a volunteer has saved.
class SavedOpportunities(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    opportunity = models.ForeignKey(VolunteerOpportunity, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

# Testimonial model for volunteers to post testimonials about their volunteering experiences.
class Testimonial(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    text = models.TextField()  
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True) 
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='liked_testimonials', blank=True) 
    status = models.CharField(
        max_length=20,
        choices=[('published', 'Published'), ('draft', 'Draft')],
        default='published',
    )  
    # Method to calculate total likes on a testimonial
    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return f"Testimonial by {self.user.username} at {self.created_at}"

# Comment model for users to comment on testimonials.
class Comment(models.Model):
    testimonial = models.ForeignKey(Testimonial, on_delete=models.CASCADE, related_name='comments')  
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    text = models.TextField()  
    created_at = models.DateTimeField(auto_now_add=True)  
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return f"Comment by {self.user.username} on {self.testimonial} at {self.created_at}"


# TestimonialReport model to track reports on testimonials.
class TestimonialReport(models.Model):
    testimonial = models.ForeignKey(Testimonial, on_delete=models.CASCADE, related_name='reports')
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    reason = models.TextField()  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report by {self.user.username} on {self.testimonial}"
    
# Badges model to represent different badges a volunteer can earn.
class Badges(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to='badges/', blank=True, null=True)

# AwardBadge model to track which badges have been awarded to volunteers.   
class AwardBadge(models.Model):
    volunteer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badges, on_delete=models.CASCADE, related_name='awarded_to')
    awarded_at = models.DateTimeField(auto_now_add=True)

# Notifications model to track notifications sent to users.
class Notifications(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    related_opportunity = models.ForeignKey('VolunteerOpportunity', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

# Message model for private messaging between users.
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)