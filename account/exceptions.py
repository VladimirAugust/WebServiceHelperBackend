class UserAlreadyExist(Exception):
	def __init__(self):
		self.message = "Username or Email already exists"


class URLHashDoesNotExist(Exception):
	def __init__(self):
		self.message = "Url Hash is incorrect"