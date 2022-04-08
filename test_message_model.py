import os
from unittest import TestCase

from models import db, User, Message, Follows, LikedBy
from flask import session

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app, db, g, CURR_USER_KEY
app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING'] = True


db.create_all()

class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        user1 = User.signup(
                username="test_user",
                password="test_password",
                email="test1@test.com",
                image_url="test.com",
            )

        db.session.commit()

        self.id = user1.id
    
    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

    def test_message_model(self):
        """Does basic model work?"""

        m = Message(
            text="I love testing",
            user_id=self.id
        )

        db.session.add(m)
        db.session.commit()
        user1 = User.query.get(self.id)

        self.assertEqual(m.user.username, "test_user")
        self.assertEqual("I love testing", m.text)
        self.assertIn(m, user1.messages)


