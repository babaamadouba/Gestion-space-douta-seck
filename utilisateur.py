class Utilisateur:
    def __init__(self, id, email, password_hash, role):
        self._id = id
        self._email = email
        self._password_hash = password_hash
        self._role = role

    @property
    def id(self):
        return self._id

    @property
    def email(self):
        return self._email

    @property
    def password_hash(self):
        return self._password_hash

    @property
    def role(self):
        return self._role
    
    @id.setter
    def id(self, value):
        self._id = value