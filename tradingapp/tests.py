from django.test import TestCase
from django.contrib.auth import get_user_model
# Assuming your CustomUser and UserProfile are in the 'users' app
# If they are in 'tradingapp', adjust the import path
from models.models import UserProfile 
# You'd also import the Item model from wherever it is defined
from models.models import Item 

User = get_user_model() 

class UserModelTests(TestCase):
    """
    Tests the creation and functionality of the CustomUser model.
    """
    
    def test_create_user(self):
        # 1. Action: Attempt to create a regular user
        user = User.objects.create_user(
            username='normaluser', 
            email='normal@test.com', 
            password='foo'
        )
        
        # 2. Assertions: Check if the user attributes are correct
        self.assertEqual(user.username, 'normaluser')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

class ProfileAndItemTests(TestCase):
    """
    Tests the relationships between CustomUser, UserProfile, and Item models.
    """

    def setUp(self):
        # This function runs before every test method in this class
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='testpassword'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            bio='This is a test bio.',
        )

    def test_profile_link(self):
        # Test the OneToOne relationship works from the user object
        self.assertEqual(self.user.profile.bio, 'This is a test bio.')
        
    def test_item_creation_and_fk(self):
        # 1. Action: Create an item linked to the test user
        item = Item.objects.create(
            seller=self.user,
            title='Test Product',
            description='A product for testing purposes.',
        )
        
        # 2. Assertions: Check that the foreign key relationship is sound
        self.assertEqual(item.seller.username, 'testuser')
        self.assertEqual(Item.objects.count(), 1)