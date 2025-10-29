from django.contrib.auth.models import User
from django.test import TestCase

from core.models import Chat, Message, Post, Profile


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
