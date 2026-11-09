"""Tous les réglages du jeu sont ici : change ces valeurs pour expérimenter."""
import pygame

# --- Fenêtre ---
LARGEUR = 540
HAUTEUR = 720
FPS = 60

# Le sol où l'on joue. Les murs l'entourent et le haut de la fenêtre sert aux infos.
ARENE = pygame.Rect(30, 80, 480, 610)
PORTE = pygame.Rect(LARGEUR // 2 - 40, 50, 80, 30)

# --- Aventure ---
SALLE_FINALE = 15
SALLES_PAR_THEME = 5        # le décor change et un boss apparaît toutes les 5 salles

# --- Joueur ---
VIE_JOUEUR = 5
VITESSE_JOUEUR = 260        # pixels par seconde
DELAI_TIR_JOUEUR = 0.32     # secondes entre deux tirs
VITESSE_TIR_JOUEUR = 600
DUREE_INVINCIBLE = 1.0      # secondes de protection après un coup reçu

# --- Ennemis ---
VITESSE_TIR_ENNEMI = 230
DISTANCE_APPARITION = 220   # un ennemi n'apparaît jamais collé au joueur

# --- Couleurs (rouge, vert, bleu) ---
NOIR = (15, 15, 22)
BLANC = (240, 240, 240)
GRIS = (150, 150, 165)
BLEU = (80, 170, 255)
BLEU_FONCE = (40, 90, 170)
PEAU = (245, 205, 165)
JAUNE = (255, 220, 90)
ROUGE = (235, 70, 80)
ORANGE = (255, 150, 60)
VERT = (90, 220, 120)
VIOLET = (170, 100, 230)
BOIS = (120, 80, 45)
