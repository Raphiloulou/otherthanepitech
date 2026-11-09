"""
Les bruitages sont fabriqués par le code : aucun fichier audio n'est nécessaire.

Un son numérique est une longue liste de nombres (les « échantillons »)
qui décrivent la forme de l'onde. Ici, on en calcule 22050 par seconde.
"""
import array
import math
import random

import pygame

ECHANTILLONS_PAR_SECONDE = 22050

_sons = {}


def onde(frequence_debut, frequence_fin, duree, forme="carre", volume=0.2):
    """Calcule un son dont la hauteur glisse de frequence_debut à frequence_fin."""
    nombre = int(ECHANTILLONS_PAR_SECONDE * duree)
    echantillons = array.array("h")  # "h" = entiers de 16 bits, entre -32768 et 32767
    phase = 0
    for i in range(nombre):
        avancement = i / nombre
        frequence = frequence_debut + (frequence_fin - frequence_debut) * avancement
        phase += frequence / ECHANTILLONS_PAR_SECONDE

        if forme == "carre":
            valeur = 1 if phase % 1 < 0.5 else -1
        elif forme == "bruit":
            valeur = random.uniform(-1, 1)
        else:
            valeur = math.sin(2 * math.pi * phase)

        # (1 - avancement) : le son s'éteint progressivement au lieu de couper net
        echantillons.append(int(valeur * (1 - avancement) * volume * 32767))
    return echantillons


def melodie(notes, duree=0.1, volume=0.2):
    """Enchaîne plusieurs notes (des fréquences en hertz)."""
    echantillons = array.array("h")
    for note in notes:
        echantillons += onde(note, note, duree, "carre", volume)
    return echantillons


def charger():
    """Prépare tous les bruitages. À appeler une fois, après pygame.init()."""
    try:
        pygame.mixer.quit()
        # allowedchanges=0 : la carte son s'adapte à notre format, pas l'inverse
        pygame.mixer.init(ECHANTILLONS_PAR_SECONDE, -16, 1, 512, allowedchanges=0)
    except pygame.error:
        print("Pas de son disponible : le jeu continue en silence.")
        return

    pygame.mixer.set_num_channels(16)  # pour entendre plusieurs sons en même temps
    recettes = {
        "tir": onde(950, 450, 0.07, "carre", 0.08),
        "tir_ennemi": onde(420, 240, 0.12, "sinus", 0.18),
        "anneau": onde(700, 140, 0.35, "sinus", 0.3),
        "touche": onde(0, 0, 0.05, "bruit", 0.15),
        "mort": onde(320, 70, 0.2, "carre", 0.16) + onde(0, 0, 0.1, "bruit", 0.15),
        "degat": onde(220, 50, 0.3, "carre", 0.3),
        "charge": onde(140, 520, 0.4, "sinus", 0.25),
        "invocation": onde(200, 900, 0.3, "carre", 0.12),
        "mort_boss": onde(500, 30, 0.8, "carre", 0.25) + onde(0, 0, 0.5, "bruit", 0.3),
        "porte": melodie([330, 440, 554], 0.09),
        "choix": melodie([523, 659, 784], 0.08),
        "pouvoir": melodie([784, 1047], 0.1),
        "victoire": melodie([523, 659, 784, 1047, 784, 1047], 0.14),
        "defaite": melodie([392, 330, 262, 196], 0.2),
    }
    for nom, echantillons in recettes.items():
        _sons[nom] = pygame.mixer.Sound(buffer=echantillons.tobytes())


def jouer(nom):
    # Le dictionnaire reste vide s'il n'y a pas de carte son : on ne joue alors rien
    if nom in _sons:
        _sons[nom].play()
