"""Les petites fonctions de géométrie, les tirs et les particules."""
import pygame
from pygame import Vector2

from reglages import ARENE, BLANC


def se_touchent(a, b):
    """Deux cercles se touchent si leurs centres sont plus proches que la somme des rayons."""
    return a.pos.distance_to(b.pos) < a.rayon + b.rayon


def direction_vers(depart, arrivee):
    """Renvoie un vecteur de longueur 1 qui va de depart vers arrivee."""
    direction = Vector2(arrivee) - depart
    # normalize() plante sur un vecteur nul (deux points exactement au même endroit)
    if direction.length() == 0:
        return Vector2(0, -1)
    return direction.normalize()


def pousser_hors_du_decor(objet, obstacles):
    """Empêche un personnage (un cercle) de traverser les obstacles et les murs."""
    for rect in obstacles:
        # Le point de l'obstacle le plus proche du centre du personnage
        plus_proche = Vector2(
            max(rect.left, min(objet.pos.x, rect.right)),
            max(rect.top, min(objet.pos.y, rect.bottom)),
        )
        ecart = objet.pos - plus_proche
        if ecart.length() == 0:
            # Le centre est dans l'obstacle : on le ressort par le haut
            objet.pos.y = rect.top - objet.rayon
        elif ecart.length() < objet.rayon:
            objet.pos = plus_proche + ecart.normalize() * objet.rayon

    objet.pos.x = max(ARENE.left + objet.rayon, min(ARENE.right - objet.rayon, objet.pos.x))
    objet.pos.y = max(ARENE.top + objet.rayon, min(ARENE.bottom - objet.rayon, objet.pos.y))


def dessiner_ombre(ecran, pos, rayon):
    rect = pygame.Rect(0, 0, rayon * 2, rayon)
    rect.center = (pos.x, pos.y + rayon)
    pygame.draw.ellipse(ecran, (20, 22, 28), rect)


class Tir:
    def __init__(self, pos, direction, vitesse, rayon, couleur,
                 degats=1, rebonds=0, percant=False, fleche=False):
        self.pos = Vector2(pos)
        self.deplacement = direction * vitesse
        self.rayon = rayon
        self.couleur = couleur
        self.degats = degats
        self.rebonds = rebonds
        self.percant = percant
        self.fleche = fleche
        self.vivant = True
        self.deja_touches = []  # un tir perçant ne blesse qu'une fois le même ennemi

    def avancer(self, dt, obstacles):
        ancienne_pos = Vector2(self.pos)
        self.pos += self.deplacement * dt

        if not ARENE.collidepoint(self.pos):
            est_sorti_sur_le_cote = not ARENE.left <= self.pos.x < ARENE.right
            self.heurter(ancienne_pos, est_sorti_sur_le_cote)
            return

        for rect in obstacles:
            if rect.collidepoint(self.pos):
                arrive_par_le_cote = not rect.left <= ancienne_pos.x <= rect.right
                self.heurter(ancienne_pos, arrive_par_le_cote)
                return

    def heurter(self, ancienne_pos, inverser_x):
        """Le tir a touché le décor : il rebondit s'il le peut, sinon il disparaît."""
        if self.rebonds == 0:
            self.vivant = False
            return
        self.rebonds -= 1
        self.pos = ancienne_pos
        self.deja_touches.clear()
        if inverser_x:
            self.deplacement.x *= -1
        else:
            self.deplacement.y *= -1

    def dessiner(self, ecran):
        if self.fleche:
            queue = self.pos - self.deplacement * 0.03
            pygame.draw.line(ecran, self.couleur, queue, self.pos, 3)
            pygame.draw.circle(ecran, BLANC, self.pos, 3)
        else:
            pygame.draw.circle(ecran, self.couleur, self.pos, self.rayon)
            pygame.draw.circle(ecran, BLANC, self.pos, self.rayon / 2)


class Particule:
    """Un petit point qui bouge puis rétrécit : explosions, feuilles, braises..."""

    def __init__(self, pos, vitesse, duree, couleur, taille):
        self.pos = Vector2(pos)
        self.vitesse = Vector2(vitesse)
        self.duree_totale = duree
        self.duree = duree
        self.couleur = couleur
        self.taille = taille

    def mettre_a_jour(self, dt):
        self.pos += self.vitesse * dt
        self.duree -= dt

    def dessiner(self, ecran):
        rayon = self.taille * self.duree / self.duree_totale
        pygame.draw.circle(ecran, self.couleur, self.pos, rayon)
