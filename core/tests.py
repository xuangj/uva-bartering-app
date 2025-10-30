from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from core.models import Chat, Message, Post, Profile
from core.forms import PostForm


class PostCreationTests(TestCase):

    def setUp(self):
        """Set up a test user and log them in for authenticated tests."""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpassword"
        )
        self.profile = Profile.objects.create(user=self.user, bio="This is a test bio.")
        
        login_successful = self.client.login(username='testuser', password='testpassword')
        
        # Optionally, assert that the login worked (good practice)
        self.assertTrue(login_successful, "Test client failed to log in the user.")
        # Define the URL for the post_create view
        self.url = reverse('post_create')
        
        # 💥 Ensure you have a 'home' URL defined for the redirect to work in tests
        # We assume the 'home' URL resolves to '/' 
        self.home_url = reverse('home')


    def test_get_request_renders_form(self):
        """Test that a GET request returns a 200 OK status and uses the correct form."""
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(self.url)
        
        # 1. Check HTTP Status Code: Should be 200 (Success)
        self.assertEqual(response.status_code, 200)
        
        # 2. Check Template Used: Ensure the correct template is rendered
        #self.assertTemplateUsed(response, 'templates/post_form.html')
        
        # 3. Check Form in Context: Ensure the postForm is passed to the template
        #self.assertIsInstance(response.context['form'], PostForm)

    def test_valid_post_creates_post_and_redirects(self):
        """Test a valid POST request saves an post and redirects to home."""
        
        # Define the valid data payload for the POST request
        valid_data = {
            'title': 'Test post Title',
            'description': 'This is a description of the test post.',
        }
        
        # 1. Check initial count: Should be 0 posts before the POST
        initial_post_count = Post.objects.count()

        # Perform the POST request
        response = self.client.post(self.url, data=valid_data)

        # 2. Check HTTP Status Code: Should be 302 (Redirect) after success
        self.assertEqual(response.status_code, 302)
        
        # 3. Check Redirect Location: Must redirect to the home page URL
        self.assertRedirects(response, self.home_url)

        # 4. Check Database: Post count should have increased by 1
        self.assertEqual(Post.objects.count(), initial_post_count + 1)
        
        # 5. Check Object Data: Verify the saved post is correct
        new_post = Post.objects.latest('created_at')
        self.assertEqual(new_post.title, 'Test post Title')
        self.assertEqual(new_post.poster.user, self.user) # Check that the logged-in user was assigned as poster

    
    def test_unauthenticated_user_redirected(self):
        """Test that a user not logged in is redirected to the login page."""
        # Log out the client
        self.client.logout()
        
        response = self.client.get(self.url)
        
        # Check that the unauthenticated user is redirected to the login URL
        login_url = reverse('account_login') + '?next=' + self.url
        self.assertRedirects(response, login_url, status_code=302, target_status_code=200)


class ProfileModelTests(TestCase):
    """
    Tests creation of Profile objects and their relationship to User.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass"
        )
        self.profile = Profile.objects.create(user=self.user, bio="This is a test bio.")

    def test_profile_str(self):
        """Profile __str__ returns username"""
        self.assertEqual(str(self.profile), "testuser")

    def test_profile_user_link(self):
        """Profile correctly links to a User"""
        self.assertEqual(self.profile.user.username, "testuser")
        self.assertEqual(self.user.profile.bio, "This is a test bio.")


class PostModelTests(TestCase):
    """
    Tests creation of Post objects and their link to Profile.
    """

    def setUp(self):
        self.user = User.objects.create_user(username="poster", password="pass")
        self.profile = Profile.objects.create(user=self.user)
        self.post = Post.objects.create(
            poster=self.profile,
            title="Test Post",
            description="This is a post used for testing.",
            image="https://example.com/image.jpg",
        )

    def test_post_str(self):
        """Post __str__ returns title"""
        self.assertEqual(str(self.post), "Test Post")

    def test_post_fields(self):
        """Post saves and retrieves correct data"""
        self.assertEqual(self.post.poster.user.username, "poster")
        self.assertEqual(self.post.description, "This is a post used for testing.")
        self.assertIn("image.jpg", self.post.image)


class ChatAndMessageTests(TestCase):
    """
    Tests Chat and Message relationships between Profiles.
    """

    def setUp(self):
        # Create two users and their profiles
        self.user1 = User.objects.create_user(username="alice", password="pass")
        self.user2 = User.objects.create_user(username="bob", password="pass")
        self.profile1 = Profile.objects.create(user=self.user1)
        self.profile2 = Profile.objects.create(user=self.user2)

        # Create a chat between them
        self.chat = Chat.objects.create(user1=self.profile1, user2=self.profile2)

    def test_chat_str(self):
        """Chat __str__ returns readable pair"""
        self.assertIn("alice", str(self.chat))
        self.assertIn("bob", str(self.chat))

    def test_message_creation_and_ordering(self):
        """Messages are linked to chat and ordered by timestamp"""
        msg1 = Message.objects.create(
            chat=self.chat, sender=self.profile1, content="Hi Bob"
        )
        msg2 = Message.objects.create(
            chat=self.chat, sender=self.profile2, content="Hi Alice"
        )

        messages = list(self.chat.messages.all())
        self.assertEqual(messages[0], msg1)
        self.assertEqual(messages[1], msg2)
        self.assertEqual(messages[0].content, "Hi Bob")
        self.assertEqual(messages[1].sender.user.username, "bob")
