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

from app import app, db, g, CURR_USER_KEY
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


    def test_is_following(self):
        """Testing if following a user works"""
        with self.client as client:
            with client.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.id

            url = f'/users/follow/{self.id2}'
            response = client.post(url, follow_redirects = True)
            self.assertEqual(response.status_code, 200)

            # make sure all other stuff is done below the response

            curr_user = User.query.get(self.id)
            html = response.get_data(as_text=True)
            self.assertIn("<!-- following page -->", html)
            user_two = User.query.get(self.id2)
            self.assertTrue(curr_user.is_following(user_two))


    def test_is_not_following(self):
        with self.client as client:
            with client.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.id
            curr_user = User.query.get(self.id)
            user_two = User.query.get(self.id2)
            self.assertFalse(curr_user.is_following(user_two)) # check if not following


    def test_is_followed_by(self):
        """Check to see if a user is being followed by a different user"""
        with self.client as client:
            with client.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.id

            url = f'/users/follow/{self.id2}'
            response = client.post(url, follow_redirects = True)

            self.assertEqual(response.status_code, 200)
            curr_user = User.query.get(self.id)
            user_two = User.query.get(self.id2)
            self.assertTrue(user_two.is_followed_by(curr_user))


    def test_user_signup_success(self):
        """Check to see if a user successfully signs up"""
        with self.client as client:
            with client.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.id

            url = '/signup'
            response = client.post(url, follow_redirects = True,
                                        data = {"username": "new_user",
                                        "password": "test_password",
                                        "email": "newtest1@test.com",
                                        "image_url": "newtest.com"})
            self.assertEqual(response.status_code, 200)

            new_user = User.query.filter_by(email = "newtest1@test.com").one()
            self.assertIn(new_user, User.query.all())

    # def test_user_signup_fail(self):
    #     """Check to see if a user unsuccessfully signs up"""
    #     with self.client as client:
    #         with client.session_transaction() as change_session:
    #             change_session[CURR_USER_KEY] = self.id

    #         url = '/signup'
    #         try:
    #             client.post(url, follow_redirects = True,
    #                                         data = {"username": "test_user",
    #                                                 "password": "test_password",
    #                                                 "email": "testsdfgsdfg2@test.com",
    #                                                 "image_url": "newtest.com"})
    #         except IntegrityError:
    #             self.assertNotIn(User(
    #                 username="test_user",
    #                 password="test_password",
    #                 email="testsdfgsdfg2@test.com",
    #                 image_url="newtest.com"
    #                 ), User.query.all())



    def test_authenticate_user_success(self):
        """Tests to see if a user is authenticated"""
        with self.client as client:
            with client.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.id

            curr_user = User.query.get(self.id)
            self.assertEquals(curr_user, curr_user.authenticate(username="test_user",
                                                        password="test_password"))


    def test_authenticate_user_fail_username(self):
        """Tests to see if a user is not authenticated with wrong username"""
        with self.client as client:
            with client.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.id

            curr_user = User.query.get(self.id)
            self.assertFalse(curr_user.authenticate(username="test", password="test_password"))


    def test_authenticate_user_fail_password(self):
        """Tests to see if a user is not authenticated with wrong password"""
        with self.client as client:
            with client.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.id

            curr_user = User.query.get(self.id)
            self.assertFalse(curr_user.authenticate(username="test", password="test"))














