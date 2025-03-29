from .models import *
from django.utils import timezone

def sample_data():
    # Create sample volunteer users
    user1 = User.objects.create_user(username='volunteer1', password='password', user_type='volunteer', location='London', postcode='E1 6AN')
    user2 = User.objects.create_user(username='volunteer2', password='password', user_type='volunteer', location='Manchester', postcode='M1 1AA')
    user3 = User.objects.create_user(username='volunteer3', password='password', user_type='volunteer', location='Bristol', postcode='BS1 2AA')

    # Create sample organization users
    organisation_user = User.objects.create_user(username='organisation1', password='password', user_type='organisation', location='London', postcode='E1 6AN')

    # Create an organisation
    organisation = Organisation.objects.create(
        user=organisation_user,
        organisation_name="Tech Volunteers",
        website_url="http://techvolunteers.org",
        mission_statement="We connect tech professionals with volunteer opportunities.",
        cause_categories=['Education', 'Technology'],
        organisation_size="Medium",
        logo="tech_logo.png"
    )

    # Create some volunteer opportunities
    opportunity1 = VolunteerOpportunity.objects.create(
        organisation=organisation,
        title="Teach Coding to Kids",
        description="Volunteer to teach kids how to code in Python and HTML.",
        skills_required=["Python", "HTML", "JavaScript"],
        location="London",
        street_address="123 Tech Street",
        city="London",
        postcode="E1 6AN",
        county="Greater London",
        country="United Kingdom",
        date=timezone.now().date(),
        duration="3 months",
        commitment_level="5 hours per week",
        remote=False,
        contact_info={"email": "info@techvolunteers.org"},
        latitude=51.5074,
        longitude=-0.1278,
        urgent=False
    )

    opportunity2 = VolunteerOpportunity.objects.create(
        organisation=organisation,
        title="Help at Local Food Bank",
        description="Assist in sorting and distributing food to people in need.",
        skills_required=["None"],
        location="Manchester",
        street_address="456 Charity Lane",
        city="Manchester",
        postcode="M1 1AA",
        county="Greater Manchester",
        country="United Kingdom",
        date=timezone.now().date(),
        duration="Ongoing",
        commitment_level="2 hours per week",
        remote=False,
        contact_info={"email": "support@techvolunteers.org"},
        latitude=53.4808,
        longitude=-2.2426,
        urgent=False
    )

    # Volunteer application to an opportunity
    VolunteerApplications.objects.create(user=user1, opportunity=opportunity1, status='accepted')
    VolunteerApplications.objects.create(user=user2, opportunity=opportunity2, status='pending')
    VolunteerApplications.objects.create(user=user3, opportunity=opportunity1, status='rejected')

    # Create testimonials
    testimonial1 = Testimonial.objects.create(user=user1, text="Volunteering with Tech Volunteers was amazing. I learned a lot!", status="published")
    testimonial2 = Testimonial.objects.create(user=user2, text="A fantastic experience volunteering at the food bank.", status="published")

    # Add some comments to testimonials
    Comment.objects.create(testimonial=testimonial1, user=user2, text="Great job, keep it up!")
    Comment.objects.create(testimonial=testimonial2, user=user3, text="Thank you for your work!")

    # Save opportunities for volunteers
    SavedOpportunities.objects.create(user=user1, opportunity=opportunity1)
    SavedOpportunities.objects.create(user=user2, opportunity=opportunity2)

    # Create volunteer preferences
    VolunteerPreferences.objects.create(user=user1, skills=["Python", "Django"], interests=["Teaching", "Tech"], availability="Weekends", hours_available="10 hours", age_group="18-25", languages=["English"])
    VolunteerPreferences.objects.create(user=user2, skills=["Event Management", "Teamwork"], interests=["Community Service", "Food Distribution"], availability="Evenings", hours_available="5 hours", age_group="26-35", languages=["English"])

    # Create a badge and award it to a volunteer
    badge = Badges.objects.create(name="Top Volunteer", description="Awarded for outstanding contributions", image="badge.png")
    AwardBadge.objects.create(volunteer=user1, badge=badge)

    
