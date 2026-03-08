class Groupe:
    def __init__(self, id, nom, responsable):
        self._id = id
        self._nom = nom
        self._responsable = responsable

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def nom(self):
        return self._nom

    @property
    def responsable(self):
        return self._responsable
