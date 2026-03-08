# creneau.py
class Creneau:
    def __init__(self, id=None, heure_debut=None, heure_fin=None):
        self._id = id
        self.heure_debut = heure_debut
        self.heure_fin = heure_fin

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, valeur):
        self._id = valeur