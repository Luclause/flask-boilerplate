from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Post
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='jason')
        u.set_password('password')

        self.assertFalse(u.check_password('notmypassword'))
        self.assertTrue(u.check_password('password'))

    def test_avatar(self):
        u = User(username='jason', email='jason@example.com')
        url = 'https://www.gravatar.com/avatar/eba69e62f8bc92297b7a97659b5d6130?d=identicon&s=128'
        self.assertEqual(u.avatar(128), (url))

    def test_follow(self):
        u1 = User(username='jason', email='jason@example.com')
        u2 = User(username='jun', email='jun@example.com')

        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        # Check new users having no followers
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u1.followers.all(), [])

        # Check following logic
        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'jun')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'jason')

        # Check unfollowing logic
        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_follow_posts(self):
        # Create four users
        u1 = User(username='jason', email='jason@example.com')
        u2 = User(username='jun', email='jun@example.com')
        u3 = User(username='jack', email='jack@example.com')
        u4 = User(username='john', email='john@example.com')
        db.session.add_all([u1, u2, u3, u4])

        # Create four posts
        now = datetime.utcnow()
        p1 = Post(body='post from jason', author=u1,
                  timestamp=now + timedelta(seconds=1))
        p2 = Post(body='post from jun', author=u2,
                  timestamp=now + timedelta(seconds=1))
        p3 = Post(body='post from jack', author=u3,
                  timestamp=now + timedelta(seconds=1))
        p4 = Post(body='post from john', author=u4,
                  timestamp=now + timedelta(seconds=1))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # Setup the followers
        u1.follow(u2)
        u1.follow(u4)
        u2.follow(u3)
        u3.follow(u4)
        db.session.commit()

        # Check the followed posts of each user
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        self.assertEqual(f1, [p1, p2, p4])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])


if __name__ == '__main__':
    unittest.main(verbosity=2)
