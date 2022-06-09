"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows
from flask import session
from sqlalchemy.exc import IntegrityError

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app, db, CURR_USER_KEY
app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING'] = True


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

class UserModelTestCase(TestCase):
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

        user2 = User.signup(
                username="test_user2",
                password="test_password2",
                email="test2@test.com",
                image_url="test2.com",
            )

        # db.session.add_all([user1, user2])
        db.session.commit()

        self.id = user1.id
        self.id2 = user2.id

        # session[CURR_USER_KEY] = self.user1.id

        # login_url = '/login'
        # self.client.post(login_url, data={"username": self.user1.username, "password": self.user1.password})

    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url=""
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr(self):
        """Testing if repr outputs correctly"""
        user1 = User.query.get(self.id)
        self.assertEqual(user1.__repr__(), f"<User #{user1.id}: {user1.username}, {user1.email}>")


    def test_invalid_user_signup(self):
        """Testing invalid user signup"""

        test_user = User.signup(None,
                    "hello",
                    "hello@hello.com",
                    None)

        test_user.id = 12234

        with self.assertRaises(IntegrityError) as context:
            db.session.commit()


    def test_valid_user_signup(self):
        """Testing valid user signup"""

        test_user = User.signup("testing",
                    "hello@hello.com",
                    "hello",
                    None)

        test_user.id = 12234
        db.session.commit()

        new_user = User.query.get(12234)

        self.assertEqual(test_user.username, new_user.username )
        self.assertEqual(test_user.email, new_user.email )
        self.assertTrue(new_user.password.__contains__('$2b'))


    def test_valid_user_authentication(self):
        """Tests for valid user authentication"""

        test_user = User.signup("testing",
                    "hello@hello.com",
                    "hello",
                    None)

        test_user.id = 12234
        db.session.commit()

        new_user = User.query.get(12234)
        auth_user = User.authenticate("testing", "hello")

        self.assertEqual(new_user, auth_user)


    def test_invalid_user_authentication(self):
        """Tests for valid user authentication"""

        test_user = User.signup("testing",
                    "hello@hello.com",
                    "hello",
                    None)

        db.session.commit()

        auth_user = User.authenticate("testing", "wrong_password")

        self.assertFalse(auth_user)

    def test_is_followed_by(self):
        """Test to see if user is followed by another user"""

        user1 = User.query.get(self.id)
        user2 = User.query.get(self.id2)

        user1.followers.append(user2)

        db.session.commit()

        self.assertIn(user2, user1.followers)
        self.assertTrue(user1.is_followed_by(user2))

    def test_is_following(self):
        """Test to see if user is following another user"""

        user1 = User.query.get(self.id)
        user2 = User.query.get(self.id2)

        user1.following.append(user2)

        db.session.commit()

        self.assertIn(user2, user1.following)
        self.assertTrue(user1.is_following(user2))













