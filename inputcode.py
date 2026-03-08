# input_handler.py
import re
import csv
from datetime import datetime
import bcrypt
from manager import GestionnaireReservation
from base2 import BaseDeDonnees
from creneau import Creneau
from groupe import Groupe

class entrer:
    def __init__(self, db: BaseDeDonnees, manager: GestionnaireReservation):
        self.db = db
        self.manager = manager

    # ================= Validation utils =================
    def valider_heure(self, heure_str):
        try:
            datetime.strptime(heure_str, "%H:%M")
            return True
        except ValueError:
            return False

    def valider_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def valider_email(self, email):
        regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return re.match(regex, email) is not None

    # ================= VERIFICATION DATE PASSEE =================
    def date_est_valide(self, date_str):
        """
        Vérifie que la date entrée n'est pas passée.
        Retourne True si la date est aujourd'hui ou dans le futur, False sinon.
        """
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return False  # format invalide
        today = datetime.today().date()
        return date_obj >= today

    # ================= CREER CRENEAU =================
    def creer_creneau(self):
        self.afficher_creneaux()
        print('liste des creneaux deja creer')
        print('creer un nouveau creneau')
        while True:
            debut = input("Heure début (HH:MM) : ").strip()
            fin = input("Heure fin (HH:MM) : ").strip()
            if self.valider_heure(debut) and self.valider_heure(fin):
                break
            print("Format invalide ! Utilisez HH:MM, par exemple 14:30")
        creneau = self.manager.creer_creneau(debut, fin)
        print(f"Créneau créé avec ID : {creneau.id}")
        return creneau

    # ================= AFFICHER TOUS LES CRENEAUX =================
    def afficher_creneaux(self):
        creneaux = self.db.obtenir_tous_creneaux()
        if not creneaux:
            print("Aucun créneau trouvé.")
            return
        for c in creneaux:
            print(f"ID:{c['id']} | {c['heure_debut']} - {c['heure_fin']}")

    # ================= CREER GROUPE =================
    def creer_groupe(self):
        print('liste des groupes deja creer')
        self.afficher_groupes()
        print(' creer un nouveau groupe')
        while True:
            nom = input("Nom du groupe : ").strip()
            responsable = input("Responsable : ").strip()
            if not nom or not responsable:
                print("Nom et responsable ne peuvent pas être vides.")
                continue
            if self.db.obtenir_groupe_par_nom(nom):
                print(f"Un groupe avec le nom '{nom}' existe déjà. Choisissez un autre nom.")
                continue
            break
        groupe = self.manager.creer_groupe(nom, responsable)
        print(f"Groupe créé avec ID : {groupe.id}")
        return groupe

    # ================= AFFICHER TOUS LES GROUPES =================
    def afficher_groupes(self):
        groupes = self.db.obtenir_tous_groupes()
        if not groupes:
            print("Aucun groupe trouvé.")
            return
        for g in groupes:
            print(f"ID:{g['id']} | Nom:{g['nom']} | Responsable:{g['responsable']}")

    # ================= CREER RESERVATION =================
    def creer_reservation(self):
        while True:
            # 1️ Saisie de la date
            date_res = input("Date (YYYY-MM-DD) : ").strip()
            if not self.valider_date(date_res):
                print("Format de date invalide ! Utilisez YYYY-MM-DD")
                continue

            # 2️ Vérifier que la date n'est pas passée
            if not self.date_est_valide(date_res):
                print("Impossible de réserver pour une date passée !")
                continue

            # 3️ Afficher tous les créneaux
            print("\n--- Liste des créneaux ---")
            self.afficher_creneaux()

            # 4️ Afficher tous les groupes
            print("\n--- Liste des groupes ---")
            self.afficher_groupes()

            # 5️ Saisie des IDs
            try:
                id_creneau = int(input("ID créneau : "))
                id_groupe = int(input("ID groupe : "))
            except ValueError:
                print("ID doit être un nombre entier.")
                continue

            # 6️ Saisie du motif
            motif = input("Motif : ").strip()
            if not motif:
                print("Motif obligatoire.")
                continue

            # 7️ Vérifier que le créneau existe
            creneau_data = self.db.obtenir_creneau(id_creneau)
            if not creneau_data:
                print("Créneau inexistant.")
                continue

            heure_debut = creneau_data["heure_debut"]
            heure_fin = creneau_data["heure_fin"]

            # 8️ Vérifier chevauchement avec réservations existantes
            reservation_existante = self.db.reservation_chevauchement_detail(date_res, heure_debut, heure_fin)
            if reservation_existante:
                print(f"Attention : ce créneau ({heure_debut}-{heure_fin}) chevauche une réservation existante "
                      f"le {date_res} de {reservation_existante['heure_debut']} à {reservation_existante['heure_fin']} "
                      f"pour le groupe '{reservation_existante['nom']}'")
                continue

            # 9️ Vérifier si le créneau est libre pour la date
            if not self.db.reserver_valide(date_res, id_creneau):
                print(f"Le créneau {id_creneau} est déjà réservé pour la date {date_res}.")
                continue

            # 10️ Vérifier que le groupe existe
            groupe_data = self.db.obtenir_groupe(id_groupe)
            if not groupe_data:
                print("Groupe inexistant.")
                continue

            break  

        #  Créer les objets
        creneau = Creneau(creneau_data["id"], creneau_data["heure_debut"], creneau_data["heure_fin"])
        groupe = Groupe(groupe_data["id"], groupe_data["nom"], groupe_data["responsable"])

        # 1️ Créer et enregistrer la réservation
        reservation = self.manager.creer_reservation(date_res, creneau, groupe, motif)
        print(f"Réservation créée avec ID : {reservation.id}")
        return reservation

    # ================= CREER UTILISATEUR (ADMIN) =================
    def creer_utilisateur(self):
        while True:
            email = input("Email : ").strip()
            mot_de_passe = input("Mot de passe : ").strip()
            role = input("Rôle (admin/membre) : ").strip().lower()
            if not email or not mot_de_passe or role not in ["admin", "membre"]:
                print("Veuillez saisir des informations valides.")
                continue
            if not self.valider_email(email):
                print("Email invalide.")
                continue
            break
        hash_mdp = bcrypt.hashpw(mot_de_passe.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        utilisateur = self.manager.creer_utilisateur(email, hash_mdp, role)
        print(f"Utilisateur créé avec ID : {utilisateur.id}")
        return utilisateur

    # ================= AFFICHER RESERVATIONS =================
    def afficher_reservations(self):
     reservations = self.db.obtenir_reservations()
     if not reservations:
        print("Aucune réservation trouvée.")
        return
     for r in reservations:
        print(f"ID:{r['id']} | Date:{r['date_reservation']} | "
              f"{r['heure_debut']} - {r['heure_fin']} | Groupe:{r['nom']} | Motif:{r['motif']}")

    # ================= AFFICHER CRENEAUX PAR DATE =================
    def afficher_creneaux_par_date(self):
        date = input("Entrer la date (YYYY-MM-DD) : ").strip()
        if not self.valider_date(date):
            print("Format de date invalide.")
            return
        creneaux = self.db.obtenir_creneaux_par_date(date)
        if not creneaux:
            print("Aucun créneau trouvé.")
            return
        print(f"\n--- Créneaux pour la date {date} ---")
        for c in creneaux:
            print(f"ID:{c['id']} | {c['heure_debut']} - {c['heure_fin']} | {c['statut']}")

    # ================= ANNULER UNE RESERVATION =================
    def annuler_reservation(self):
        self.afficher_reservations()
        try:
            id_res = int(input("\nEntrez l'ID de la réservation à annuler : "))
        except ValueError:
            print("ID invalide.")
            return
        if self.db.annuler_reservation(id_res):
            print(f"Réservation ID {id_res} annulée avec succès.")
        else:
            print(f"Aucune réservation trouvée avec l'ID {id_res}.")

    # ================= MODIFIER UNE RESERVATION =================
    def modifier_reservation(self):
        self.afficher_reservations()
        try:
            id_res = int(input("Entrez l'ID de la réservation à modifier : ").strip())
        except ValueError:
            print("ID invalide.")
            return

        res = self.db.obtenir_reservation_par_id(id_res)
        if not res:
            print(f"Aucune réservation trouvée avec l'ID {id_res}.")
            return

        # Saisie de la nouvelle date
        while True:
            date_res = input(f"Nouvelle date (YYYY-MM-DD) [{res['date_reservation']}] : ").strip()
            if not date_res:
                date_res = res['date_reservation']
                break
            if not self.valider_date(date_res):
                print("Format de date invalide ! Utilisez YYYY-MM-DD")
                continue
            if not self.date_est_valide(date_res):
                print("Impossible de choisir une date passée !")
                continue
            break

        # Afficher les créneaux pour la date
        print("\n--- Créneaux disponibles pour cette date ---")
        self.afficher_creneaux_par_date()

        # Choix du nouveau créneau
        while True:
            try:
                id_creneau = input(f"Nouvel ID de créneau [{res['id_creneau']}] : ").strip()
                id_creneau = int(id_creneau) if id_creneau else res['id_creneau']
            except ValueError:
                print("ID invalide.")
                continue

            creneau_data = self.db.obtenir_creneau(id_creneau)
            if not creneau_data:
                print("Créneau inexistant.")
                continue

            if self.db.reservation_chevauchement(date_res, creneau_data["heure_debut"], creneau_data["heure_fin"]):
                print(f"Attention : ce créneau ({creneau_data['heure_debut']}-{creneau_data['heure_fin']}) "
                      f"chevauche une réservation existante.")
                continue

            break

        # Afficher les groupes disponibles
        print("\n--- Groupes existants ---")
        self.afficher_groupes()

        while True:
            try:
                id_groupe = input(f"Nouvel ID de groupe [{res['id_groupe']}] : ").strip()
                id_groupe = int(id_groupe) if id_groupe else res['id_groupe']
            except ValueError:
                print("ID invalide.")
                continue

            groupe_data = self.db.obtenir_groupe(id_groupe)
            if not groupe_data:
                print("Groupe inexistant.")
                continue
            break

        motif = input(f"Nouveau motif [{res['motif']}] : ").strip()
        motif = motif if motif else res['motif']

        self.db.modifier_reservation(id_res, date_res, id_creneau, id_groupe, motif)
        print(f"Réservation ID {id_res} modifiée avec succès !")

        # ================= TELECHARGER LES RESERVATIONS =================

    def telecharger_reservations(self, nom_fichier="reservations.csv"):
     reservations = self.db.obtenir_reservations()
     if not reservations:
        print("Aucune réservation à télécharger.")
        return

     # Création du fichier CSV
     try:
        with open(nom_fichier, mode="w", newline="", encoding="utf-8") as fichier_csv:
            writer = csv.writer(fichier_csv)
            # Écrire l'en-tête (ajout de Motif)
            writer.writerow(["ID", "Date", "Heure début", "Heure fin", "Groupe", "Motif"])
            # Écrire les réservations
            for r in reservations:
                writer.writerow([
                    r['id'],
                    r['date_reservation'],
                    r['heure_debut'],
                    r['heure_fin'],
                    r['nom'],
                    r.get('motif', '')  # utiliser r['motif'] si la colonne existe
                ])
        print(f"Les réservations ont été téléchargées dans le fichier '{nom_fichier}'.")
     except Exception as e:
        print(f"Erreur lors du téléchargement : {e}")