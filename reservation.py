from creneau import Creneau
from groupe import Groupe

class Reservation:

    def __init__(self, id, date_reservation, creneau: Creneau, groupe: Groupe, motif=None):
        self._id = id
        self._date_reservation = date_reservation
        self._creneau = creneau
        self._groupe = groupe
        self._motif = motif

    # ===== ID =====
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, valeur):
        self._id = valeur

    # ===== DATE =====
    @property
    def date_reservation(self):
        return self._date_reservation

    # ===== CRENEAU =====
    @property
    def creneau(self):
        return self._creneau

    # ===== GROUPE =====
    @property
    def groupe(self):
        return self._groupe

    # ===== MOTIF =====
    @property
    def motif(self):
        return self._motif
    
   