"""Le personnage contrôlé par le joueur."""
import pygame
from pygame import Vector2

from objets import Tir, dessiner_ombre, direction_vers, pousser_hors_du_decor
from reglages import (ARENE, BLEU, BLEU_FONCE, BOIS, DELAI_TIR_JOUEUR, DUREE_INVINCIBLE, JAUNE, PEAU,
                      VIE_JOUEUR, VITESSE_JOUEUR, VITESSE_TIR_JOUEUR)


class Joueur:
    def __init__(self):
        self.pos = Vector2(ARENE.centerx, ARENE.bottom - 50)
        self.rayon = 15
        self.visee = Vector2(0, -1)     # direction du curseur, de longueur 1
        self.attente_tir = 0
        self.invincible = 0

        # Ces valeurs sont modifiées par les pouvoirs (voir ameliorations.py)
        self.vie_max = VIE_JOUEUR
        self.vie = VIE_JOUEUR
        self.vitesse = VITESSE_JOUEUR
        self.delai_tir = DELAI_TIR_JOUEUR
        self.duree_invincible = DUREE_INVINCIBLE
        self.degats = 1
        self.nb_tirs = 1
        self.tirs_diagonaux = False
        self.rebonds = 0
        self.percant = False

    def deplacer(self, touches, dt, obstacles):
        """Déplace le joueur et renvoie True s'il a bougé."""
        droite = touches[pygame.K_RIGHT] or touches[pygame.K_d]
        gauche = touches[pygame.K_LEFT] or touches[pygame.K_q]
        bas = touches[pygame.K_DOWN] or touches[pygame.K_s]
        haut = touches[pygame.K_UP] or touches[pygame.K_z]

        direction = Vector2(droite - gauche, bas - haut)
        if direction.length() == 0:
            return False

        # normalize() : sans ça, on irait plus vite en diagonale
        self.pos += direction.normalize() * self.vitesse * dt
        pousser_hors_du_decor(self, obstacles)
        return True

    def viser(self, curseur):
        self.visee = direction_vers(self.pos, curseur)

    def tirer(self):
        """Crée les flèches, toutes orientées vers le curseur, et les renvoie."""
        directions = [self.visee]
        if self.tirs_diagonaux:
            directions += [self.visee.rotate(-35), self.visee.rotate(35)]

        # La perpendiculaire sert à placer les flèches côte à côte
        cote = self.visee.rotate(90)
        fleches = []
        for direction in directions:
            for numero in range(self.nb_tirs):
                decalage = cote * (numero - (self.nb_tirs - 1) / 2) * 12
                fleches.append(Tir(self.pos + decalage, direction, VITESSE_TIR_JOUEUR, 5, JAUNE,
                                   self.degats, self.rebonds, self.percant, fleche=True))
        return fleches

    def blesser(self):
        """Enlève une vie, sauf si le joueur est invincible. Renvoie True s'il a été blessé."""
        if self.invincible > 0:
            return False
        self.vie -= 1
        self.invincible = self.duree_invincible
        return True

    def dessiner(self, ecran):
        # La ligne de visée, en pointillés
        for distance in range(32, 130, 20):
            pygame.draw.circle(ecran, (225, 225, 235), self.pos + self.visee * distance, 2)

        # Le joueur clignote tant qu'il est invincible
        if self.invincible > 0 and int(self.invincible * 10) % 2 == 1:
            return

        dessiner_ombre(ecran, self.pos, self.rayon)
        pygame.draw.circle(ecran, BLEU_FONCE, self.pos, self.rayon)
        pygame.draw.circle(ecran, BLEU, self.pos - self.visee * 3, self.rayon - 4)
        pygame.draw.circle(ecran, PEAU, self.pos + self.visee * 4, 8)

        # L'arc tourne avec la visée
        cote = self.visee.rotate(90)
        haut_arc = self.pos + self.visee * 13 + cote * 14
        bas_arc = self.pos + self.visee * 13 - cote * 14
        pointe = self.pos + self.visee * 23
        pygame.draw.lines(ecran, BOIS, False, [haut_arc, pointe, bas_arc], 3)
        pygame.draw.line(ecran, (235, 235, 235), haut_arc, bas_arc, 1)
