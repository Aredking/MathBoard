from app.models import User

def test_password_hashing(app):
    with app.app_context():
        u = User(username='test', name='Test')
        u.set_password('secret')
        assert u.check_password('secret')
        assert not u.check_password('wrong')