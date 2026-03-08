# menu.py
from base2 import BaseDeDonnees
from manager import GestionnaireReservation
from inputcode import entrer

class Menu:

    def __init__(self):
        self.db = BaseDeDonnees()
        self.manager = GestionnaireReservation(self.db)
        self.entrer = entrer(self.db, self.manager)
        self.utilisateur_connecte = None

    # ================= AUTHENTIFICATION =================
    def se_connecter(self):
        print("===== CONNEXION =====")
        email = input("Email : ")
        mot_de_passe = input("Mot de passe : ")

        utilisateur = self.db.verifier_utilisateur(email, mot_de_passe)
        if utilisateur:
            self.utilisateur_connecte = utilisateur
            print(f"Bienvenue {utilisateur.email} ! (Rôle : {utilisateur.role})")
            self.afficher_menu_principal()
        else:
            print("Email ou mot de passe incorrect.")

    # ================= MENU PRINCIPAL =================
    def afficher_menu_principal(self):
        while True:
            print("\n===== MENU =====")
            print("1. Créer un créneau")
            print("2. Créer un groupe")
            print("3. Créer une réservation")
            print("4. Afficher les créneaux")
            print("5. Afficher les groupes")
            print("6. Afficher les réservations")
            print("8. Afficher les créneaux par date")
            print("9. Annuler une réservation")
            print("10. Modifier une réservation") 
            print("11. Telecharger la liste des ressr") 
            if self.utilisateur_connecte.role == "admin":
                print("7. Créer un utilisateur")
            print("0. Déconnexion")

            choix = input("Votre choix : ")

            if choix == "1":
                self.entrer.creer_creneau()
            elif choix == "2":
                self.entrer.creer_groupe()
            elif choix == "3":
                self.entrer.creer_reservation()
            elif choix == "4":
                self.afficher_tous_creneaux()
            elif choix == "5":
                self.afficher_tous_groupes()
            elif choix == "6":
                self.entrer.afficher_reservations()
            elif choix == "7" and self.utilisateur_connecte.role == "admin":
                self.entrer.creer_utilisateur()
            elif choix == "8":
                self.entrer.afficher_creneaux_par_date()
            elif choix == "9":
             self.entrer.annuler_reservation() 
            elif choix == "10":
               self.entrer.modifier_reservation()
            if choix == "11":
                 self.entrer.telecharger_reservations()
            elif choix == "0":
                print("Déconnexion...")
                self.utilisateur_connecte = None
                break
            else:
                print("Choix invalide")

    # ================= AFFICHER TOUS LES CRENEAUX =================
    def afficher_tous_creneaux(self):
        creneaux = self.db.obtenir_tous_creneaux()
        if not creneaux:
            print("Aucun créneau disponible.")
            return
        print("\n--- Liste des créneaux ---")
        for c in creneaux:
            print(f"ID:{c['id']} | {c['heure_debut']} - {c['heure_fin']}")

    # ================= AFFICHER TOUS LES GROUPES =================
    def afficher_tous_groupes(self):
        groupes = self.db.obtenir_tous_groupes()
        if not groupes:
            print("Aucun groupe disponible.")
            return
        print("\n--- Liste des groupes ---")
        for g in groupes:
            print(f"ID:{g['id']} | Nom:{g['nom']} | Responsable:{g['responsable']}")


# ================= LANCER LE MENU =================
if __name__ == "__main__":
    menu = Menu()
    menu.se_connecter()
    
