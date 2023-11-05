# Unit testing for User object
from models.user import User

# Invalid email test
print("Invalid email test:")
new_user = User("invalidenmail.", "John Doe")
print("Error:", new_user.error)

print("\n")

# Valid email test
print("Valid email test:")
new_user = User("thisisavalidemail@outlook.com", "Jane Doe")
print("Error:", new_user.error)
print("Stored email:", new_user.email)

print("\n")

# Invalid parameter test
print("Invalid parameter test:")
new_user = User("nonameprovided@outlook.com")
print("Error:", new_user.error)