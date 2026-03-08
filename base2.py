# ======================= CLASS_BASE_DE_DONNEE =======================

import mysql.connector
import bcrypt
from creneau import Creneau
from groupe import Groupe
from utilisateur import Utilisateur
from reservation import Reservation


class BaseDeDonnees:

    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="amadou",
            password="ama12345",
            database="Gestion_Espace"
        )

        self.curseur = self.conn.cursor(dictionary=True)

    # ================= ENREGISTRER CRENEAU =================
    def enregistrer_creneau(self, creneau: Creneau):
        sql = "INSERT INTO Creneau (heure_debut, heure_fin) VALUES (%s, %s)"
        self.curseur.execute(sql, (creneau.heure_debut, creneau.heure_fin))
        self.conn.commit()
        creneau.id = self.curseur.lastrowid

    # ================= ENREGISTRER GROUPE =================
    def enregistrer_groupe(self, groupe: Groupe):
        sql = "INSERT INTO Groupe (nom, responsable) VALUES (%s, %s)"
        self.curseur.execute(sql, (groupe.nom, groupe.responsable))
        self.conn.commit()
        groupe.id = self.curseur.lastrowid

    # ================= ENREGISTRER UTILISATEUR =================
    def enregistrer_utilisateur(self, utilisateur: Utilisateur):
        sql = "INSERT INTO Utilisateur (email, password, role) VALUES (%s, %s, %s)"
        self.curseur.execute(sql, (
            utilisateur.email,
            utilisateur.password_hash,
            utilisateur.role
        ))
        self.conn.commit()
        utilisateur.id = self.curseur.lastrowid

    # ================= VERIFIER UTILISATEUR =================
    def verifier_utilisateur(self, email, mot_de_passe):
        """
        Vérifie si l'utilisateur existe et si le mot de passe est correct.
        Retourne un objet Utilisateur si OK, sinon None.
        """
        self.curseur.execute(
            "SELECT * FROM Utilisateur WHERE email=%s", (email,)
        )
        row = self.curseur.fetchone()
        if not row:
            return None

        if bcrypt.checkpw(mot_de_passe.encode('utf-8'), row['password'].encode('utf-8')):
            utilisateur = Utilisateur(
                row['id'],
                row['email'],
                row['password'],
                row['role']
            )
            return utilisateur
        return None

    # ================= OBTENIR UTILISATEUR PAR EMAIL =================
    def obtenir_utilisateur_par_email(self, email):
        self.curseur.execute(
            "SELECT * FROM Utilisateur WHERE email=%s", (email,)
        )
        return self.curseur.fetchone()

    # ================= ENREGISTRER RESERVATION =================
    def enregistrer_reservation(self, reservation: Reservation):
        sql = """
        INSERT INTO Reservation (date_reservation, id_creneau, id_groupe, motif)
        VALUES (%s, %s, %s, %s)
        """
        self.curseur.execute(sql, (
            reservation.date_reservation,
            reservation.creneau.id,
            reservation.groupe.id,
            reservation.motif
        ))
        self.conn.commit()
        reservation.id = self.curseur.lastrowid

    # ================= CHARGER CRENEAU PAR ID =================
    def obtenir_creneau(self, id_creneau):
        self.curseur.execute(
            "SELECT * FROM Creneau WHERE id=%s", (id_creneau,))
        return self.curseur.fetchone()

    # ================= CHARGER GROUPE PAR ID =================
    def obtenir_groupe(self, id_groupe):
        self.curseur.execute(
            "SELECT * FROM Groupe WHERE id=%s", (id_groupe,))
        return self.curseur.fetchone()
    def obtenir_groupe_par_nom(self, nom):
     curseur = self.conn.cursor(dictionary=True)
     try:
        curseur.execute("SELECT * FROM Groupe WHERE nom=%s", (nom,))
        result = curseur.fetchone()  # consomme la ligne
        # consommer tout le reste au cas où
        while curseur.fetchone():
            pass
        return result
     finally:
        curseur.close()  # ferme correctement le curseur
    # ================= AFFICHER RESERVATIONS =================
    def obtenir_reservations(self):
     self.curseur.execute("""
        SELECT r.id, r.date_reservation,
               c.heure_debut, c.heure_fin,
               g.nom,
               r.motif
        FROM Reservation r
        JOIN Creneau c ON r.id_creneau = c.id
        JOIN Groupe g ON r.id_groupe = g.id
     """)
     return self.curseur.fetchall()
    def reserver_valide(self, date, id_creneau):
     curseur = self.conn.cursor(dictionary=True)
     try:
        curseur.execute(
            "SELECT * FROM Reservation WHERE date_reservation=%s AND id_creneau=%s",
            (date, id_creneau)
        )
        return curseur.fetchone() is None  # True si disponible
     finally:
        curseur.close()

    # ================= RESERVATION CHEVAUCHEMENT =================
    def reservation_chevauchement(self, date, heure_debut, heure_fin):
    
     cursor = self.conn.cursor(dictionary=True)

     query = """
     SELECT c.heure_debut, c.heure_fin
     FROM Reservation r
     JOIN Creneau c ON r.id_creneau = c.id
     WHERE r.date_reservation = %s
     """

     cursor.execute(query, (date,))
     reservations = cursor.fetchall()
     cursor.close()

     for r in reservations:
        # Si les horaires se chevauchent, on retourne True
        if heure_debut < r["heure_fin"] and heure_fin > r["heure_debut"]:
            return True  

     return False
    # ================= CHEVLOCHEMENT RESERVATION DETAIL =================
    def reservation_chevauchement_detail(self, date, heure_debut, heure_fin):
   
     cursor = self.conn.cursor(dictionary=True)
     try:
        query = """
        SELECT r.id, c.heure_debut, c.heure_fin, g.nom
        FROM Reservation r
        JOIN Creneau c ON r.id_creneau = c.id
        JOIN Groupe g ON r.id_groupe = g.id
        WHERE r.date_reservation = %s
        """
        cursor.execute(query, (date,))
        reservations = cursor.fetchall()
        for r in reservations:
            # Vérifie chevauchement
            if heure_debut < r["heure_fin"] and heure_fin > r["heure_debut"]:
                return r  # Retourne la réservation qui bloque
        return None
     finally:
        cursor.close()
    # ================= OBTENIR TOUS LES CRENEAUX =================

    def obtenir_tous_creneaux(self):
     with self.conn.cursor(dictionary=True) as curseur:
        curseur.execute("SELECT * FROM Creneau")
        return curseur.fetchall()
     # ================= CRENEAUX PAR DATE (LIBRE / RESERVE) =================
     
    def obtenir_creneaux_par_date(self, date):
    
     with self.conn.cursor(dictionary=True) as curseur:
        # Récupérer tous les créneaux
        curseur.execute("SELECT * FROM Creneau ORDER BY heure_debut ASC")
        tous_creneaux = curseur.fetchall()

        # Récupérer toutes les réservations pour la date
        curseur.execute("""
            SELECT c.heure_debut, c.heure_fin
            FROM Reservation r
            JOIN Creneau c ON r.id_creneau = c.id
            WHERE r.date_reservation = %s
            ORDER BY c.heure_debut ASC
        """, (date,))
        reservations = curseur.fetchall()

     # Fusionner les intervalles RESERVE
     intervals = []
     for r in reservations:
        debut = r["heure_debut"]
        fin = r["heure_fin"]
        if not intervals:
            intervals.append([debut, fin])
        else:
            last = intervals[-1]
            # Si chevauchement, on fusionne
            if debut <= last[1]:
                last[1] = max(last[1], fin)
            else:
                intervals.append([debut, fin])

     # Construire la liste finale
     creneaux_filtres = []
     for c in tous_creneaux:
        c_debut = c["heure_debut"]
        c_fin = c["heure_fin"]

        # Vérifier si ce créneau chevauche un intervalle RESERVE
        chevauche = False
        for interval in intervals:
            if c_debut < interval[1] and c_fin > interval[0]:
                # Si chevauche, on garde uniquement le plus grand intervalle RESERVE
                if not any(x for x in creneaux_filtres if x["statut"] == "RESERVE" and x["heure_debut"] == interval[0]):
                    creneaux_filtres.append({
                        "id": "RESERVE",  # ou None si tu veux
                        "heure_debut": interval[0],
                        "heure_fin": interval[1],
                        "statut": "RESERVE"
                    })
                chevauche = True
                break
        if not chevauche:
            creneaux_filtres.append({
                "id": c["id"],
                "heure_debut": c_debut,
                "heure_fin": c_fin,
                "statut": "LIBRE"
            })

     # Trier par heure de début
     creneaux_filtres.sort(key=lambda x: x["heure_debut"])
     return creneaux_filtres
    # ================= OBTENIR TOUS LES GROUPES =================

    def obtenir_tous_groupes(self):
     with self.conn.cursor(dictionary=True) as curseur:
        curseur.execute("SELECT * FROM Groupe")
        return curseur.fetchall()
     
    # ================= SUPPRIMER UNE RESERVATION =================
    def annuler_reservation(self, id_reservation):
   
     self.curseur.execute("SELECT * FROM Reservation WHERE id=%s", (id_reservation,))
     res = self.curseur.fetchone()
     if not res:
        return False  # Pas de réservation avec cet ID
     self.curseur.execute("DELETE FROM Reservation WHERE id=%s", (id_reservation,))
     self.conn.commit()
     return True
    # ================= MODIFIER UNE RESERVATION =================
    def modifier_reservation(self, id_reservation, date_res, id_creneau, id_groupe, motif):
  
      self.curseur.execute(
        """
        UPDATE Reservation
        SET date_reservation=%s,
            id_creneau=%s,
            id_groupe=%s,
            motif=%s
        WHERE id=%s
        """,
        (date_res, id_creneau, id_groupe, motif, id_reservation)
     )
      self.conn.commit()
      return True
    
    def obtenir_reservation_par_id(self, id_reservation):
     self.curseur.execute("""
        SELECT r.id, r.date_reservation, r.id_creneau, r.id_groupe, r.motif,
               c.heure_debut, c.heure_fin,
               g.nom
        FROM Reservation r
        JOIN Creneau c ON r.id_creneau = c.id
        JOIN Groupe g ON r.id_groupe = g.id
        WHERE r.id = %s
     """, (id_reservation,))
     return self.curseur.fetchone()