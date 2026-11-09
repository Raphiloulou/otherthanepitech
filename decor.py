"""
Tout ce qui concerne le décor : thèmes, sol, murs, obstacles, torches et porte.

Le décor immobile est dessiné une seule fois par salle sur une image (le « fond »),
puis on recopie cette image à chaque frame : c'est bien plus rapide.
"""
import math
import random

import pygame
from pygame import Vector2

from objets import Particule
from reglages import ARENE, BOIS, GRIS, HAUTEUR, JAUNE, LARGEUR, NOIR, ORANGE, PORTE, SALLES_PAR_THEME, VERT

THEMES = [
    {
        "nom": "Forêt", "sol_a": (62, 98, 60), "sol_b": (55, 89, 55),
        "mur": (82, 64, 46), "joint": (54, 42, 32), "obstacle": "arbre",
        "details": ["herbe", "herbe", "fleur", "caillou"],
        "flamme": (255, 190, 80), "ambiance": (160, 210, 90), "derive": 30,
    },
    {
        "nom": "Crypte", "sol_a": (66, 66, 82), "sol_b": (58, 58, 73),
        "mur": (50, 48, 70), "joint": (32, 30, 46), "obstacle": "tombe",
        "details": ["fissure", "os", "caillou"],
        "flamme": (110, 200, 255), "ambiance": (175, 175, 210), "derive": -15,
    },
    {
        "nom": "Volcan", "sol_a": (68, 44, 40), "sol_b": (59, 38, 36),
        "mur": (42, 30, 30), "joint": (120, 50, 25), "obstacle": "rocher",
        "details": ["braise", "fissure", "caillou"],
        "flamme": (255, 120, 50), "ambiance": (255, 140, 50), "derive": -45,
    },
]

TORCHES = [
    (15, 220), (15, 420), (15, 620), (LARGEUR - 15, 220), (LARGEUR - 15, 420), (LARGEUR - 15, 620),
    (LARGEUR // 2 - 130, 65), (LARGEUR // 2 + 130, 65),
]


def theme_de_la_salle(salle):
    return THEMES[(salle - 1) // SALLES_PAR_THEME % len(THEMES)]


def creer_halo(couleur):
    """Une image de lumière ronde : plus claire au centre, noire sur les bords."""
    halo = pygame.Surface((140, 140))
    for rayon in range(70, 0, -7):
        force = (70 - rayon) / 70 * 0.4
        teinte = [int(canal * force) for canal in couleur]
        pygame.draw.circle(halo, teinte, (70, 70), rayon)
    return halo


for theme in THEMES:
    theme["halo"] = creer_halo(theme["flamme"])


def creer_obstacles():
    """Place des obstacles sur une grille. Jamais plus de 2 par ligne : on peut toujours passer."""
    obstacles = []
    for ligne in random.sample(range(4), 3):
        for colonne in random.sample(range(5), random.randint(1, 2)):
            obstacles.append(pygame.Rect(ARENE.left + colonne * 96 + 18, 185 + ligne * 90, 60, 60))
    return obstacles


def creer_fond(theme, obstacles):
    """Dessine une fois pour toutes le décor immobile de la salle."""
    fond = pygame.Surface((LARGEUR, HAUTEUR))
    dessiner_murs(fond, theme)
    dessiner_sol(fond, theme)
    for _ in range(110):
        x = random.randint(ARENE.left + 8, ARENE.right - 8)
        y = random.randint(ARENE.top + 14, ARENE.bottom - 8)
        DETAILS[random.choice(theme["details"])](fond, x, y)
    for rect in obstacles:
        OBSTACLES[theme["obstacle"]](fond, rect)
    return fond


def dessiner_murs(fond, theme):
    fond.fill(theme["joint"])
    for ligne, y in enumerate(range(50, HAUTEUR, 15)):
        decalage = 0 if ligne % 2 == 0 else -15
        for x in range(decalage, LARGEUR, 30):
            pygame.draw.rect(fond, theme["mur"], (x + 1, y + 1, 28, 13))
    pygame.draw.rect(fond, NOIR, (0, 0, LARGEUR, 50))


def dessiner_sol(fond, theme):
    fond.set_clip(ARENE)
    for colonne in range(11):
        for ligne in range(14):
            couleur = theme["sol_a"] if (colonne + ligne) % 2 == 0 else theme["sol_b"]
            pygame.draw.rect(fond, couleur, (ARENE.left + colonne * 48, ARENE.top + ligne * 48, 48, 48))
    # L'ombre portée du mur du haut donne une impression de profondeur
    pygame.draw.rect(fond, theme["joint"], (ARENE.left, ARENE.top, ARENE.width, 10))
    fond.set_clip(None)


# --- Les petits détails posés sur le sol ---

def detail_herbe(fond, x, y):
    for decalage in (-3, 0, 3):
        pygame.draw.line(fond, (95, 150, 75), (x, y), (x + decalage, y - 7), 1)


def detail_fleur(fond, x, y):
    couleur = random.choice([(240, 220, 110), (235, 150, 190), (220, 220, 245)])
    for point in ((x - 3, y), (x + 3, y), (x, y - 3), (x, y + 3)):
        pygame.draw.circle(fond, couleur, point, 2)
    pygame.draw.circle(fond, ORANGE, (x, y), 1)


def detail_caillou(fond, x, y):
    pygame.draw.ellipse(fond, (118, 118, 125), (x, y, random.randint(5, 10), random.randint(4, 6)))


def detail_fissure(fond, x, y):
    points = [(x, y)]
    for _ in range(4):
        x += random.randint(-8, 8)
        y += random.randint(3, 9)
        points.append((x, y))
    pygame.draw.lines(fond, (38, 34, 42), False, points, 1)


def detail_os(fond, x, y):
    pygame.draw.line(fond, (205, 200, 185), (x - 5, y), (x + 5, y), 2)
    for bout in ((x - 6, y - 1), (x - 6, y + 1), (x + 6, y - 1), (x + 6, y + 1)):
        pygame.draw.circle(fond, (205, 200, 185), bout, 2)


def detail_braise(fond, x, y):
    pygame.draw.circle(fond, (130, 45, 20), (x, y), 4)
    pygame.draw.circle(fond, ORANGE, (x, y), 2)


DETAILS = {
    "herbe": detail_herbe, "fleur": detail_fleur, "caillou": detail_caillou,
    "fissure": detail_fissure, "os": detail_os, "braise": detail_braise,
}


# --- Les obstacles : ils arrêtent les personnages et les tirs ---

def dessiner_ombre_obstacle(fond, rect):
    pygame.draw.ellipse(fond, (25, 28, 30), (rect.left, rect.bottom - 16, rect.width, 22))


def obstacle_arbre(fond, rect):
    dessiner_ombre_obstacle(fond, rect)
    pygame.draw.rect(fond, BOIS, (rect.centerx - 7, rect.centery, 14, rect.height // 2))
    pygame.draw.circle(fond, (34, 90, 48), (rect.centerx, rect.centery - 2), 30)
    pygame.draw.circle(fond, (48, 120, 60), (rect.centerx - 9, rect.centery - 9), 18)
    pygame.draw.circle(fond, (70, 150, 78), (rect.centerx + 8, rect.centery - 14), 11)


def obstacle_tombe(fond, rect):
    dessiner_ombre_obstacle(fond, rect)
    corps = pygame.Rect(rect.left + 8, rect.top + 4, 44, 54)
    pygame.draw.rect(fond, (118, 118, 138), corps, border_top_left_radius=20, border_top_right_radius=20)
    pygame.draw.rect(fond, (85, 85, 104), corps, 3, border_top_left_radius=20, border_top_right_radius=20)
    pygame.draw.line(fond, (70, 70, 88), (rect.centerx, rect.top + 18), (rect.centerx, rect.top + 44), 4)
    pygame.draw.line(fond, (70, 70, 88), (rect.centerx - 10, rect.top + 27), (rect.centerx + 10, rect.top + 27), 4)


def obstacle_rocher(fond, rect):
    dessiner_ombre_obstacle(fond, rect)
    x, y = rect.topleft
    contour = [(x + 8, y + 58), (x, y + 30), (x + 14, y + 6), (x + 38, y), (x + 58, y + 22), (x + 54, y + 58)]
    pygame.draw.polygon(fond, (72, 58, 56), contour)
    pygame.draw.polygon(fond, (45, 34, 34), contour, 3)
    pygame.draw.lines(fond, ORANGE, False, [(x + 20, y + 14), (x + 30, y + 30), (x + 24, y + 42), (x + 38, y + 54)], 2)


OBSTACLES = {"arbre": obstacle_arbre, "tombe": obstacle_tombe, "rocher": obstacle_rocher}


# --- Ce qui bouge dans le décor ---

def dessiner_torches(ecran, theme):
    for x, y in TORCHES:
        tremble = random.randint(-2, 2)
        ecran.blit(theme["halo"], (x - 70 + tremble, y - 70 + tremble), special_flags=pygame.BLEND_RGB_ADD)
        pygame.draw.rect(ecran, BOIS, (x - 3, y, 6, 12))
        pygame.draw.circle(ecran, theme["flamme"], (x, y - 3), 6 + random.randint(0, 2))
        pygame.draw.circle(ecran, JAUNE, (x, y - 2), 3)


def dessiner_porte(ecran, ouverte, temps):
    pygame.draw.rect(ecran, GRIS, PORTE.inflate(12, 6))
    if not ouverte:
        pygame.draw.rect(ecran, BOIS, PORTE)
        for x in range(PORTE.left + 16, PORTE.right, 16):
            pygame.draw.line(ecran, (75, 50, 30), (x, PORTE.top), (x, PORTE.bottom), 2)
        pygame.draw.rect(ecran, GRIS, (PORTE.left, PORTE.centery - 3, PORTE.width, 6))
        return

    pygame.draw.rect(ecran, NOIR, PORTE)
    # Une flèche verte qui danse indique la sortie
    y = ARENE.top + 30 + math.sin(temps * 5) * 5
    x = PORTE.centerx
    pygame.draw.polygon(ecran, VERT, [(x, y - 14), (x - 16, y + 6), (x + 16, y + 6)])


def particule_ambiante(theme):
    """Feuilles qui tombent, poussière ou braises qui montent, selon le thème."""
    pos = Vector2(random.randint(ARENE.left, ARENE.right), random.randint(ARENE.top, ARENE.bottom))
    vitesse = Vector2(random.uniform(-15, 15), theme["derive"])
    return Particule(pos, vitesse, random.uniform(1.5, 3), theme["ambiance"], 3)
