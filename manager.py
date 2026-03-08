# ======================= CLASS_MANAGER =======================
from creneau import Creneau
from groupe import Groupe
from utilisateur import Utilisateur
from reservation import Reservation


class GestionnaireReservation:

    def __init__(self, db):
        self.db = db

    def creer_creneau(self, heure_debut, heure_fin):
        creneau = Creneau(None, heure_debut, heure_fin)
        self.db.enregistrer_creneau(creneau)
        return creneau

    def creer_groupe(self, nom, responsable):
        groupe = Groupe(None, nom, responsable)
        self.db.enregistrer_groupe(groupe)
        return groupe

    def creer_utilisateur(self, email, password_hash, role):
        utilisateur = Utilisateur(None, email, password_hash, role)
        self.db.enregistrer_utilisateur(utilisateur)
        return utilisateur

    def creer_reservation(self, date_reservation, creneau, groupe, motif=None):
        reservation = Reservation(None, date_reservation, creneau, groupe, motif)
        self.db.enregistrer_reservation(reservation)
        return reservation

    
        
    



   