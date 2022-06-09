"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.msg = Message(text="yo what is up")

        db.session.commit()

        self.id = self.testuser.id
        self.msg_id = self.msg.id


    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_add_message_not_logged_in(self):
        """Tests to see if a message can be added while logged in"""

        with self.client as client:
            url = "/messages/new"
            response = client.get(url, follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            html = response.get_data(as_text=True)

            self.assertIn("Access unauthorized.", html)

    # def test_delete_message(self):
    #     """Test if a message can be deleted"""
    #     with self.client as client:
    #         with client.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.testuser.id

    #         resp = client.post("/messages/new", data={"text": "Hello"})

    #         url = f"/messages/{self.msg_id}/delete"
    #         response = client.post(url, follow_redirects=True)

    #         msg = Message.query.one()

    #         self.assertIn(msg, user.messages)


