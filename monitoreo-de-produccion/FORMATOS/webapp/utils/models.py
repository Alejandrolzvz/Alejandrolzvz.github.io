from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, role_id, role_name):
        self.id = id
        self.username = username
        self.role_id = role_id
        self.role = role_name # Para compatibilidad existente
