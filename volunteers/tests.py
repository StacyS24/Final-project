from django.test import TestCase, Client  
from django.urls import reverse
from .models import *
from .forms import *
from .views import *

# Tests for the organisation signup process
class TestOrganisationSigUp(TestCase):
    def setUp(self):
        # Set up the test client and URL for organisation signup
        self.client = Client()
        self.signup_url = reverse('organisation-sign-up')

    def test_organisation_signup_success(self):
        # Test successful organisation signup
        data = {
            'username': 'orguser',
            'email': 'orguser@example.com',
            'password1': 'testpassword',
            'password2': 'testpassword',
            'location': 'London',
            'organisation_name': 'Test Organisation',
            'website_url': 'https://example.com',
            'mission_statement': 'Helping communities.',
            'cause_categories': ['education'],
            'organisation_size': 'small (1-10 employees) ',
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, 302)  
        self.assertTrue(User.objects.filter(username='orguser').exists())
        self.assertTrue(Organisation.objects.filter(organisation_name='Test Organisation').exists())

    def test_organisation_sign_up_invalid(self):
        # Test organisation signup with invalid data
        data = {
            'username': 'orguser',
            'email': 'orguser@example.com',
            'password1': 'testpassword',
            'password2': 'testpassword1',  # Mismatched passwords
            'location': 'London',
            'organisation_name': 'Test Organisation',
            'website_url': 'https://example.com',
            'mission_statement': 'Helping communities.',
            'cause_categories': ['education'],
            'organisation_size': 'small (1-10 employees) ',
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, 200)  # Form errors return to the same page


# Tests for the volunteer signup process
class TestVolunteerSignUp(TestCase):
    def setUp(self):
        # Set up the test client and URL for volunteer signup
        self.client = Client()
        self.signup_url = reverse('volunteer-sign-up')

    def test_volunteer_sign_up_success(self):
        # Test successful volunteer signup
        data = {
            'username': 'volunteer123',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane.doe@example.com',
            'phone_number': '1234567890',
            'location': 'London',
            'postcode': 'NW1 6XE',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'availability': 'Daily',
            'hours available': '1-5 hours per week',
            'age group': 'under 18',
            'skills': ['public speaking', 'translation'],
            'interests': ['food banks'],
            'languages': ['english']
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, 200)



# Tests for login functionality
class LoginTests(TestCase):
    def setUp(self):
        # Set up the test client, user, and login URL
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.login_url = reverse('login')

    def test_login_success(self):
        # Test successful login
        data = {'username': 'testuser', 'password': 'testpassword'}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 200)

    def test_login_failure(self):
        # Test login failure with incorrect password
        data = {'username': 'testuser', 'password': 'wrongpassword'}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 200)
     

# Tests for logout functionality
class Logout(TestCase):
    def setUp(self):
        # Set up the test client, user, and logout URL
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        self.logout_url = reverse('log-out')

    def test_logout(self):
        # Test logout functionality
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 302)

# Tests for volunteer profile view
class VolunteerProfileViewTests(TestCase):
    def setUp(self):
        # Set up the test client, user, and volunteer preferences
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.preferences = VolunteerPreferences.objects.create(user=self.user, skills=['programming'], interests=['Farm Animal Care'])
        self.edit_url = reverse('edit-volunteer-profile')

    def test_redirect_if_not_logged_in(self):
        # Test redirection to login page if user is not logged in
        response = self.client.get(reverse('volunteer-profile'))
        self.assertRedirects(response, reverse('login'))

    def test_edit_profile(self):
        # Test editing volunteer profile
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('edit-volunteer-profile'), {
            'skills': 'Updated Skill',
            'interests': 'Updated Interest'
        })
        self.assertEqual(response.status_code, 200)


# Tests for organisation profile view
class OrganisationProfileViewTests(TestCase):
    def setUp(self):
        # Set up the test client, user, and organisation
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.organisation = Organisation.objects.create(user=self.user, organisation_name="Test Organisation", cause_categories=['education'])

    def test_view_with_logged_in_user(self):
        # Test viewing organisation profile when logged in
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('organisation-profile'))
        self.assertEqual(response.status_code, 200)

    def test_edit_profile(self):
        # Test editing organisation profile
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('edit-organisation-profile'), {
            'cause_categories': ['education', 'healthcare'],
        })
        self.assertEqual(response.status_code, 200)




# Tests for searching users
class searchUsers(TestCase):
    def setUp(self):
        # Set up the test environment and user with preferences
        self.client = Client()
        self.user = User.objects.create(username='testuser', password='password')
        VolunteerPreferences.objects.create(user=self.user, skills="Django", interests="Development")

    def test_search_users(self):
        # Test searching for users by skills
        response = self.client.get(reverse('search_users'), {'query': 'Django'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testuser")  # Check if the user appears in search results


# Tests for posting a volunteer opportunity
class postVolunteerOpportunity(TestCase):
    def setUp(self):
        # Set up valid and invalid data for the opportunity form
        self.valid_data = {
            'title': 'Community Cleanup',
            'description': 'Join us in cleaning up the community park.',
            'skills_required': ['fundraising', 'event_planning'],
            'location': 'Local Community Center',
            'date': '2025-01-15',
            'duration': 'One-time',
            'commitment_level': 'Weekly',
            'remote': False,
            'phone_number': '+1 234 567 8901',
            'street_address': '123 Park Lane',
            'city': 'London',
            'postcode': 'EC1A 1BB',
            'county': 'Greater London',
            'country': 'UK',
        }
        self.invalid_data = {
            'title': '',  # Missing required fields
            'description': '',
            'skills_required': [],
            'location': '',
            'date': '',
            'phone_number': '',
        }

    def test_form_valid_data(self):
        # Test that the form is valid with proper data
        form = VolunteerOpportunityForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        instance = form.save(commit=False)
        self.assertEqual(instance.title, self.valid_data['title'])  

    def test_form_invalid_data(self):
        # Test that the form is invalid with missing data
        form = VolunteerOpportunityForm(data=self.invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)  # Verify error messages for required fields


# Tests for opportunity-related actions
class opportunityActions(TestCase):
    def setUp(self):
        # Set up test client, user, organisation, and opportunity
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username="testuser", password="password")
               
        self.organisation = Organisation.objects.create(
            user=self.user,
            organisation_name="Test Organisation",
            mission_statement="An organisation for testing purposes.",
            cause_categories=['education']
        )
               
        self.opportunity = VolunteerOpportunity.objects.create(
            organisation=self.organisation,
            title='Community Cleanup',
            description='Join us in cleaning up the community park.',
            skills_required=['fundraising', 'event_planning'],  
            location='Local Community Center',
            date='2025-01-15',
            duration='One-time',
            commitment_level='Weekly',
            remote=False,
            street_address='123 Park Lane',
            city='London',
            postcode='EC1A 1BB',
            county='Greater London',
            country='UK'
        )

    def test_save_opportuntiy(self):
        # Test saving and unsaving an opportunity
        url = reverse('save-opportunity', args=[self.opportunity.id])
        response = self.client.post(url)
        self.assertEqual(SavedOpportunities.objects.filter(user=self.user, opportunity=self.opportunity).count(), 1)
        self.assertEqual(response.status_code, 302)

        response = self.client.post(url)
        self.assertEqual(SavedOpportunities.objects.filter(user=self.user, opportunity=self.opportunity).count(), 0)
        self.assertEqual(response.status_code, 302)

    def test_save_opportunity_invalid_id(self):
        # Test saving an opportunity with an invalid ID
        url = reverse('save-opportunity', args=[999])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_apply_opportunity_invalid_id(self):
        # Test applying for an opportunity with an invalid ID
        url = reverse('apply-opportunity', args=[999])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)



# Tests for confirming volunteer applications and notifications
class OpportunityTests(TestCase):
    def setUp(self):
        # Set up test client, organisation user, volunteer user, and opportunity
        self.client = Client()
        self.org_user = User.objects.create_user(username="orguser", password="password")
        self.volunteer_user = User.objects.create_user(username="volunteeruser", password="password")

        self.organisation = Organisation.objects.create(
            user=self.org_user,
            organisation_name="Test Organisation",
            mission_statement="Test Description",
            cause_categories=['education']
        )
        self.opportunity = VolunteerOpportunity.objects.create(
            organisation=self.organisation,
            title="Community Cleanup",
            description="Join us to clean up the community park.",
            location="Local Community Center",
            skills_required=['gardening'],
            date="2025-01-15",
            duration="One-time",
            commitment_level="Weekly",
            remote=False,
            street_address="123 Park Lane",
            city="London",
            postcode="EC1A 1BB",
            county="Greater London",
            country="UK"
        )

    def test_confirm_volunteer(self):
        # Test confirming a volunteer application and sending a notification
        self.client.login(username="orguser", password="password")
        application = VolunteerApplications.objects.create(user=self.volunteer_user, opportunity=self.opportunity)
        application.refresh_from_db()
        self.assertEqual(application.status, "accepted")
        notification = Notifications.objects.filter(recipient=self.volunteer_user).first()
        self.assertIsNotNone(notification)
        self.assertIn("You have been confirmed", notification.message)

    def test_notify_organisation_on_application(self):
        # Test sending a notification to the organisation when an application is submitted
        application = VolunteerApplications.objects.create(user=self.volunteer_user, opportunity=self.opportunity)
        notification = Notifications.objects.filter(recipient=self.org_user).first()
        self.assertIsNotNone(notification)
        self.assertIn("has applied for", notification.message)
        self.assertEqual(notification.related_opportunity, self.opportunity)


# Tests for testimonials functionality
class TestimonialTests(TestCase):
    def setUp(self):
        # Set up test client and user
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username="testuser", password="password")

    def test_testimonial_list(self):
        # Test listing testimonials
        Testimonial.objects.create(user=self.user, text="Testimonial 1")
        Testimonial.objects.create(user=self.user, text="Testimonial 2")
        response = self.client.get(reverse('testimonial_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Testimonial 1")
        self.assertContains(response, "Testimonial 2")

    def test_submit_testimonial(self):
        # Test submitting a testimonial
        initial_count = Testimonial.objects.count()
        Testimonial.objects.create(user=self.user, text="Existing Testimonial")
        data = {'content': 'This is a testimonial'}
        response = self.client.post(reverse('submit_testimonial'), data)
        self.assertEqual(Testimonial.objects.count(), initial_count + 1)
        self.assertEqual(response.status_code, 200)

    def test_submit_testimonial_invalid_data(self):
        # Test submitting a testimonial with invalid data
        data = {'content': ''}
        response = self.client.post(reverse('submit_testimonial'), data)
        self.assertEqual(Testimonial.objects.count(), 0)
        self.assertEqual(response.status_code, 200)


# Tests for user detail views
class UserDetailTests(TestCase):
    def setUp(self):
        # Set up volunteer user, organisation user, and their preferences/organisation
        self.volunteer_user = User.objects.create_user(username="volunteer", password="password", user_type="volunteer")
        self.org_user = User.objects.create_user(username="organization", password="password", user_type="organisation")      
        self.volunteer_preferences = VolunteerPreferences.objects.create(user=self.volunteer_user, skills=["gardening"])
        self.organisation = Organisation.objects.create(
            user=self.org_user,
            organisation_name="Test Org",
            mission_statement="Helping the community",
            cause_categories=['education'],
            logo=None
        )

    def test_user_detail_volunteer(self):
        # Test user detail page for a volunteer user
        self.client.login(username="volunteer", password="password")
        response = self.client.get(reverse('user_detail', args=[self.volunteer_user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], self.volunteer_user)
        self.assertEqual(response.context['preferences'], self.volunteer_preferences)
        self.assertIsNone(response.context['organisation'])
        self.assertIsInstance(response.context['form'], MessageForm)

    def test_user_detail_private_profile(self):
        # Test viewing a private profile
        self.client.login(username="organization", password="password")
        self.org_user.profile_is_private = True
        self.org_user.save()
        response = self.client.get(reverse('user_detail', args=[self.org_user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_private'])