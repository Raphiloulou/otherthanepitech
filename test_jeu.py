"""Vérifie les règles du jeu sans ouvrir de fenêtre. Lancer avec : py test_jeu.py"""
import os
import random
from collections import defaultdict

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from pygame import Vector2

import jeu
import sons
from ameliorations import AMELIORATIONS, tirer_trois_choix
from ennemis import Boss, Tireur
from joueur import Joueur
from objets import Tir
from reglages import ARENE, ORANGE, PORTE, SALLE_FINALE, VIE_JOUEUR, VITESSE_JOUEUR, VITESSE_TIR_ENNEMI

DT = 1 / 60
BAS_GAUCHE = (0, 700)   # un curseur qui ne vise pas les ennemis


def touches(*appuyees):
    etat = defaultdict(bool)
    for touche in appuyees:
        etat[touche] = True
    return etat


def partie_calme():
    """Une salle sans obstacle où les ennemis, loin du joueur, ne tirent pas."""
    random.seed(2)
    partie = jeu.Partie()
    partie.obstacles = []
    for ennemi in partie.ennemis:
        ennemi.attente_tir = 999
        ennemi.pos = Vector2(ARENE.centerx, ARENE.top + 40)
    return partie


def test_diagonale_meme_vitesse():
    joueur = Joueur()
    depart = Vector2(joueur.pos)
    joueur.deplacer(touches(pygame.K_RIGHT, pygame.K_UP), DT, [])
    assert abs(joueur.pos.distance_to(depart) - VITESSE_JOUEUR * DT) < 0.001


def test_reste_dans_arene():
    joueur = Joueur()
    for _ in range(300):
        joueur.deplacer(touches(pygame.K_LEFT), DT, [])
    assert joueur.pos.x == ARENE.left + joueur.rayon


def test_obstacle_bloque_le_joueur():
    joueur = Joueur()
    mur = pygame.Rect(joueur.pos.x - 100, joueur.pos.y - 100, 200, 40)
    for _ in range(120):
        joueur.deplacer(touches(pygame.K_UP), DT, [mur])
    assert joueur.pos.y == mur.bottom + joueur.rayon


def test_les_fleches_vont_vers_le_curseur():
    partie = partie_calme()
    joueur = partie.joueur
    curseur = (joueur.pos.x + 100, joueur.pos.y)
    partie.mettre_a_jour(touches(), curseur, False, DT)
    assert len(partie.tirs_joueur) == 1
    assert partie.tirs_joueur[0].deplacement.x > 0
    assert abs(partie.tirs_joueur[0].deplacement.y) < 0.001


def test_quand_le_joueur_tire():
    partie = partie_calme()
    partie.mettre_a_jour(touches(pygame.K_LEFT), BAS_GAUCHE, False, DT)
    assert len(partie.tirs_joueur) == 0     # il bouge sans cliquer : pas de tir

    partie.mettre_a_jour(touches(), BAS_GAUCHE, False, DT)
    assert len(partie.tirs_joueur) == 1     # immobile : tir automatique

    for commande, clic in [(touches(pygame.K_LEFT), True), (touches(pygame.K_LEFT, pygame.K_SPACE), False)]:
        partie = partie_calme()
        partie.mettre_a_jour(commande, BAS_GAUCHE, clic, DT)
        assert len(partie.tirs_joueur) == 1  # clic ou Espace : tir en bougeant


def test_esquive():
    for commande, vie_attendue in [(touches(pygame.K_LEFT), VIE_JOUEUR), (touches(), VIE_JOUEUR - 1)]:
        partie = partie_calme()
        origine = partie.joueur.pos + Vector2(0, -200)
        partie.tirs_ennemis.append(Tir(origine, Vector2(0, 1), VITESSE_TIR_ENNEMI, 7, ORANGE))
        for _ in range(60):
            partie.mettre_a_jour(commande, BAS_GAUCHE, False, DT)
        assert partie.joueur.vie == vie_attendue


def test_invincibilite():
    joueur = Joueur()
    assert joueur.blesser() is True
    assert joueur.blesser() is False
    assert joueur.vie == VIE_JOUEUR - 1


def test_obstacle_arrete_un_tir():
    mur = pygame.Rect(200, 200, 60, 60)
    tir = Tir((230, 300), Vector2(0, -1), 300, 5, ORANGE)
    for _ in range(60):
        tir.avancer(DT, [mur])
    assert not tir.vivant


def test_rebond():
    tir = Tir((ARENE.left + 5, 300), Vector2(-1, 0), 600, 5, ORANGE, rebonds=1)
    for _ in range(3):
        tir.avancer(DT, [])
    assert tir.vivant and tir.deplacement.x > 0


def test_tir_percant_ne_blesse_qu_une_fois():
    partie = partie_calme()
    ennemi = partie.ennemis[0]
    ennemi.vie = 3
    fleche = Tir(ennemi.pos, Vector2(0, 1), 0, 5, ORANGE, percant=True)
    partie.tirs_joueur.append(fleche)
    partie.gerer_collisions()
    partie.gerer_collisions()
    assert ennemi.vie == 2 and fleche.vivant


def test_porte_pouvoir_salle_suivante():
    partie = partie_calme()
    partie.ennemis = []
    partie.mettre_a_jour(touches(pygame.K_LEFT), BAS_GAUCHE, False, DT)
    assert partie.porte_ouverte and partie.salle == 1

    partie.joueur.pos = Vector2(PORTE.centerx, ARENE.top + 20)
    partie.mettre_a_jour(touches(pygame.K_LEFT), BAS_GAUCHE, False, DT)
    assert partie.etat == "choix" and len(partie.choix) == 3

    partie.clic((5, 5))
    assert partie.etat == "choix"           # un clic hors des cartes ne choisit rien
    partie.clic(jeu.CARTES[1].center)
    assert partie.etat == "combat" and partie.salle == 2
    assert partie.choix[1] in partie.ameliorations_prises


def test_pouvoir_unique_jamais_repropose():
    uniques = [a for a in AMELIORATIONS if a["unique"]]
    for _ in range(200):
        assert not set(a["nom"] for a in tirer_trois_choix(uniques)) & set(a["nom"] for a in uniques)


def test_ennemis_hors_des_obstacles():
    for _ in range(50):
        partie = jeu.Partie()
        for ennemi in partie.ennemis:
            assert not any(rect.collidepoint(ennemi.pos) for rect in partie.obstacles)


def test_boss_et_victoire():
    partie = partie_calme()
    partie.salle = 4
    partie.entrer_dans_salle_suivante()
    assert isinstance(partie.ennemis[0], Boss) and partie.obstacles == []

    partie.salle = SALLE_FINALE - 1
    partie.entrer_dans_salle_suivante()
    partie.ennemis[0].vie = 0
    partie.mettre_a_jour(touches(pygame.K_LEFT), BAS_GAUCHE, False, DT)
    assert partie.etat == "victoire"


def test_sons_generes():
    sons.charger()
    assert len(sons._sons) > 0
    for nom, son in sons._sons.items():
        assert son.get_length() > 0, nom


def test_aventure_complete_sans_plantage():
    """Traverse les 15 salles avec des commandes au hasard, en dessinant chaque image."""
    random.seed(1)
    ecran = pygame.Surface((jeu.LARGEUR, jeu.HAUTEUR))
    polices = jeu.creer_polices()
    partie = jeu.Partie()
    possibles = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_SPACE]
    commande = touches()
    for salle_attendue in range(1, SALLE_FINALE + 1):
        assert partie.salle == salle_attendue
        for image in range(400):
            if image % 20 == 0:
                commande = touches(*random.sample(possibles, random.randint(0, 3)))
            partie.joueur.invincible = 10   # pour atteindre toutes les salles
            curseur = (random.randint(0, 539), random.randint(0, 719))
            partie.mettre_a_jour(commande, curseur, image % 2 == 0, DT)
            partie.dessiner(ecran, polices, curseur)

        for ennemi in partie.ennemis:
            ennemi.vie = 0
        partie.mettre_a_jour(commande, (0, 0), False, DT)
        if salle_attendue < SALLE_FINALE:
            partie.joueur.pos = Vector2(PORTE.centerx, ARENE.top + 20)
            partie.mettre_a_jour(touches(), (0, 0), False, DT)
            assert partie.etat == "choix"
            partie.dessiner(ecran, polices, (0, 0))
            partie.clic(jeu.CARTES[0].center)
    assert partie.etat == "victoire"
    partie.dessiner(ecran, polices, (0, 0))


if __name__ == "__main__":
    pygame.init()
    for nom, test in list(globals().items()):
        if nom.startswith("test_"):
            test()
            print("OK", nom)
    print("Tous les tests passent.")
