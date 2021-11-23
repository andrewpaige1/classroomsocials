from app import User
users = User.query.all()
for user in users:
    print(user.first_name)