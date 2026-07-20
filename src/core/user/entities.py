from core.permissions import Permissions


class BaseUser:
    def __init__(self, username,  password, email, is_admin, permissions):
        self.username = username
        self.password = password
        self.email = email
        self.is_admin = is_admin
        self.permissions = permissions


class AdminUser(BaseUser):
    def __init__(self, username, password, email):
        super().__init__(username, password, email, is_admin=True, permissions=Permissions.list())


class RegularUser(BaseUser):
    def __init__(self, username, password, email, permissions):
        super().__init__(username, password, email, is_admin=False, permissions=permissions)




