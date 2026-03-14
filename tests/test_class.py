from app.user import User

def test_user_greet():
    user = User('Ibragim')
    assert user.greet() == 'Hello, Ibragim'

