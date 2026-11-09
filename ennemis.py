"""
Les ennemis. La classe Ennemi contient ce qu'ils ont tous en commun.
Chaque type d'ennemi en hérite et écrit sa propre méthode agir().
"""
import math
import random

import pygame
from pygame import Vector2

import sons
from objets import dessiner_ombre, direction_vers, pousser_hors_du_decor
from reglages import ARENE, BLANC, NOIR, ORANGE, ROUGE, VERT, VIOLET


class Ennemi:
    # Valeurs de base, remplacées dans chaque type d'ennemi
    vie_depart = 3
    rayon = 17
    vitesse = 70
    couleur = ROUGE
    est_boss = False

    def __init__(self, pos, salle):
        self.pos = Vector2(pos)
        self.vie_max = self.vie_depart + salle // 3     # plus on avance, plus ils résistent
        self.vie = self.vie_max
        self.flash = 0                                  # temps restant en blanc après un coup
        self.regard = Vector2(0, 1)

    def mettre_a_jour(self, partie, dt):
        self.flash -= dt
        self.regard = direction_vers(self.pos, partie.joueur.pos)
        self.agir(partie, dt)
        pousser_hors_du_decor(self, partie.obstacles)

    def agir(self, partie, dt):
        pass

    def blesser(self, degats):
        self.vie -= degats
        self.flash = 0.08

    def dessiner(self, ecran):
        dessiner_ombre(ecran, self.pos, self.rayon)
        self.dessiner_corps(ecran, BLANC if self.flash > 0 else self.couleur)
        self.dessiner_yeux(ecran)
        if not self.est_boss:
            pygame.draw.rect(ecran, NOIR, (self.pos.x - 20, self.pos.y - self.rayon - 11, 40, 5))
            largeur = 40 * max(self.vie, 0) / self.vie_max
            pygame.draw.rect(ecran, VERT, (self.pos.x - 20, self.pos.y - self.rayon - 11, largeur, 5))

    def dessiner_corps(self, ecran, couleur):
        pygame.draw.circle(ecran, couleur, self.pos, self.rayon)

    def dessiner_yeux(self, ecran):
        ecart = self.rayon * 0.4
        for cote in (-1, 1):
            oeil = self.pos + Vector2(cote * ecart, -self.rayon * 0.15)
            pygame.draw.circle(ecran, BLANC, oeil, self.rayon * 0.26)
            pygame.draw.circle(ecran, NOIR, oeil + self.regard * self.rayon * 0.1, self.rayon * 0.13)


class Tireur(Ennemi):
    """Se promène au hasard et tire vers le joueur."""

    def __init__(self, pos, salle):
        super().__init__(pos, salle)
        self.direction = Vector2(0, 0)
        self.attente_changement = 0
        self.attente_tir = random.uniform(1, 2)

    def agir(self, partie, dt):
        self.attente_changement -= dt
        if self.attente_changement <= 0:
            self.direction = Vector2(1, 0).rotate(random.uniform(0, 360))
            self.attente_changement = random.uniform(0.8, 2)
        self.pos += self.direction * self.vitesse * dt

        self.attente_tir -= dt
        if self.attente_tir <= 0:
            # Il vise la position actuelle du joueur : bouger permet d'esquiver
            partie.ajouter_tir_ennemi(self.pos, self.regard)
            sons.jouer("tir_ennemi")
            self.attente_tir = random.uniform(1.2, 2.2)


class Chargeur(Ennemi):
    """Marche vers le joueur, se prépare, puis fonce tout droit."""
    vie_depart = 4
    rayon = 16
    vitesse = 80
    couleur = VIOLET

    def __init__(self, pos, salle):
        super().__init__(pos, salle)
        self.etat = "marche"
        self.chrono = random.uniform(1.5, 2.5)
        self.direction_charge = Vector2(0, 1)

    def agir(self, partie, dt):
        # Une petite « machine à états » : l'ennemi fait une seule chose à la fois
        self.chrono -= dt
        if self.etat == "marche":
            self.pos += self.regard * self.vitesse * dt
            if self.chrono <= 0:
                self.etat = "prepare"
                self.chrono = 0.5
                sons.jouer("charge")
        elif self.etat == "prepare":
            if self.chrono <= 0:
                self.etat = "fonce"
                self.chrono = 0.45
                self.direction_charge = self.regard
        elif self.etat == "fonce":
            self.pos += self.direction_charge * 430 * dt
            if self.chrono <= 0:
                self.etat = "marche"
                self.chrono = random.uniform(1.5, 2.5)

    def dessiner_corps(self, ecran, couleur):
        if self.etat == "prepare" and self.flash <= 0:
            couleur = ORANGE
        # Une étoile : on alterne entre pointes (grand rayon) et creux (petit rayon)
        points = []
        for i in range(16):
            rayon = self.rayon + 6 if i % 2 == 0 else self.rayon - 2
            points.append(self.pos + Vector2(rayon, 0).rotate(i * 360 / 16))
        pygame.draw.polygon(ecran, couleur, points)


class Mage(Ennemi):
    """Reste immobile et lance un cercle de projectiles."""
    vie_depart = 5
    rayon = 18
    couleur = (70, 130, 220)

    def __init__(self, pos, salle):
        super().__init__(pos, salle)
        self.attente_tir = random.uniform(1.5, 2.5)

    def agir(self, partie, dt):
        self.attente_tir -= dt
        if self.attente_tir <= 0:
            partie.ajouter_anneau(self.pos, 8, random.uniform(0, 45))
            sons.jouer("anneau")
            self.attente_tir = 2.6

    def dessiner_corps(self, ecran, couleur):
        # Un cercle qui grandit prévient que le mage va attaquer
        if self.attente_tir < 0.6:
            rayon = self.rayon + (0.6 - self.attente_tir) * 40
            pygame.draw.circle(ecran, BLANC, self.pos, rayon, 2)
        x, y = self.pos
        pygame.draw.polygon(ecran, couleur, [(x, y - 30), (x - 20, y + 16), (x + 20, y + 16)])
        pygame.draw.circle(ecran, couleur, self.pos, self.rayon)


class Boss(Ennemi):
    """Va de gauche à droite et enchaîne trois attaques différentes."""
    rayon = 42
    couleur = (190, 50, 70)
    est_boss = True

    def __init__(self, pos, salle):
        super().__init__(pos, salle)
        self.vie_max = 40 + salle * 8
        self.vie = self.vie_max
        self.temps = 0
        self.attente_attaque = 2
        self.prochaine_attaque = 0

    def agir(self, partie, dt):
        self.temps += dt
        self.pos.x = ARENE.centerx + math.sin(self.temps * 0.8) * 150

        self.attente_attaque -= dt
        if self.attente_attaque <= 0:
            attaques = [self.anneau, self.eventail, self.invocation]
            attaques[self.prochaine_attaque](partie)
            self.prochaine_attaque = (self.prochaine_attaque + 1) % len(attaques)
            self.attente_attaque = 1.6

    def anneau(self, partie):
        partie.ajouter_anneau(self.pos, 16, self.temps * 40)
        sons.jouer("anneau")

    def eventail(self, partie):
        for angle in (-30, -15, 0, 15, 30):
            partie.ajouter_tir_ennemi(self.pos, self.regard.rotate(angle))
        sons.jouer("tir_ennemi")

    def invocation(self, partie):
        if len(partie.ennemis) < 5:
            for cote in (-1, 1):
                partie.ennemis.append(Chargeur(self.pos + Vector2(cote * 70, 40), partie.salle))
            sons.jouer("invocation")

    def dessiner_corps(self, ecran, couleur):
        pygame.draw.circle(ecran, couleur, self.pos, self.rayon)
        # Les cornes
        x, y = self.pos
        for cote in (-1, 1):
            pygame.draw.polygon(ecran, BLANC, [(x + cote * 34, y - 24), (x + cote * 16, y - 38),
                                               (x + cote * 44, y - 58)])
