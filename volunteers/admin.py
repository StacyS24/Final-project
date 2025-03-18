from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(VolunteerPreferences)
admin.site.register(Organisation)
admin.site.register(VolunteerOpportunity)
admin.site.register(VolunteerApplications)
admin.site.register(SavedOpportunities)
admin.site.register(Testimonial)
admin.site.register(Comment)
admin.site.register(TestimonialReport)
admin.site.register(Notifications)
admin.site.register(Message)
admin.site.register(Badges)
admin.site.register(AwardBadge)
