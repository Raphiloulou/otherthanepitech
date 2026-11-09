"""
Les pouvoirs proposés entre deux salles.
Pour en créer un nouveau : écris une fonction, puis ajoute une ligne au tableau.
"""
import random

from reglages import BLEU, GRIS, JAUNE, ORANGE, ROUGE, VERT, VIOLET


def double_tir(joueur):
    joueur.nb_tirs += 1


def tir_rapide(joueur):
    joueur.delai_tir *= 0.8


def puissance(joueur):
    joueur.degats += 1


def diagonales(joueur):
    joueur.tirs_diagonaux = True


def percant(joueur):
    joueur.percant = True


def rebond(joueur):
    joueur.rebonds += 1


def bottes(joueur):
    joueur.vitesse *= 1.15


def coeur_en_plus(joueur):
    joueur.vie_max += 1
    joueur.vie += 1


def potion(joueur):
    joueur.vie = min(joueur.vie_max, joueur.vie + 2)


def armure(joueur):
    joueur.duree_invincible += 0.3


# "unique" : le pouvoir ne peut être choisi qu'une seule fois
AMELIORATIONS = [
    {"nom": "Double tir", "texte": "Une flèche\nde plus", "effet": double_tir, "couleur": JAUNE, "unique": False},
    {"nom": "Tir rapide", "texte": "Tire 20 %\nplus vite", "effet": tir_rapide, "couleur": ORANGE, "unique": False},
    {"nom": "Puissance", "texte": "+1 dégât\npar flèche", "effet": puissance, "couleur": ROUGE, "unique": False},
    {"nom": "Diagonales", "texte": "Deux flèches\nsur les côtés", "effet": diagonales, "couleur": VIOLET, "unique": True},
    {"nom": "Perçant", "texte": "Les flèches\ntraversent", "effet": percant, "couleur": BLEU, "unique": True},
    {"nom": "Rebond", "texte": "Les flèches\nrebondissent", "effet": rebond, "couleur": VERT, "unique": False},
    {"nom": "Bottes", "texte": "Déplacement\n+15 %", "effet": bottes, "couleur": GRIS, "unique": False},
    {"nom": "Coeur +1", "texte": "Une vie max\nen plus", "effet": coeur_en_plus, "couleur": ROUGE, "unique": False},
    {"nom": "Potion", "texte": "Rend\n2 vies", "effet": potion, "couleur": VERT, "unique": False},
    {"nom": "Armure", "texte": "Invincible\nplus longtemps", "effet": armure, "couleur": GRIS, "unique": False},
]


def tirer_trois_choix(deja_prises):
    disponibles = [a for a in AMELIORATIONS if not (a["unique"] and a in deja_prises)]
    return random.sample(disponibles, 3)
