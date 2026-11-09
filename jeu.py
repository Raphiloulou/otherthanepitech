"""
test jeu py : un jeu de tir vu de dessus, salle après salle.
C'est le fichier à lancer.

Commandes :
  Flèches ou Z Q S D   : se déplacer
  Souris               : viser (les flèches partent vers le curseur)
  Rester immobile      : le héros tire tout seul vers le curseur
  Clic gauche ou Espace: tirer même en se déplaçant
  R                    : recommencer à la fin d'une partie
  Échap                : quitter

Organisation du code :
  reglages.py      les valeurs à modifier pour expérimenter
  objets.py        les tirs, les particules, la géométrie
  joueur.py        le héros
  ennemis.py       les types d'ennemis et le boss
  ameliorations.py les pouvoirs à choisir entre les salles
  decor.py         les thèmes, le sol, les obstacles, les torches
  sons.py          les bruitages calculés par le code
  jeu.py           les règles de la partie et la boucle principale
"""
import random

import pygame
from pygame import Vector2

import decor
import sons
from ameliorations import tirer_trois_choix
from ennemis import Boss, Chargeur, Mage, Tireur
from joueur import Joueur
from objets import Particule, Tir, direction_vers, se_touchent
from reglages import (ARENE, BLANC, BLEU, DISTANCE_APPARITION, FPS, GRIS, HAUTEUR, JAUNE, LARGEUR, NOIR, ORANGE,
                      PORTE, ROUGE, SALLE_FINALE, SALLES_PAR_THEME, VITESSE_TIR_ENNEMI)

CARTES = [pygame.Rect(45 + numero * 155, 240, 140, 230) for numero in range(3)]


class Partie:
    """
    Contient tout ce qui existe pendant une partie.
    self.etat vaut "combat", "choix", "perdu" ou "victoire".
    """

    def __init__(self):
        self.etat = "combat"
        self.joueur = Joueur()
        self.salle = 0
        self.score = 0
        self.temps = 0
        self.tremblement = 0
        self.ameliorations_prises = []
        self.choix = []
        self.entrer_dans_salle_suivante()

    # --- Préparation d'une salle ---

    def entrer_dans_salle_suivante(self):
        self.salle += 1
        self.theme = decor.theme_de_la_salle(self.salle)
        salle_de_boss = self.salle % SALLES_PAR_THEME == 0

        self.obstacles = [] if salle_de_boss else decor.creer_obstacles()
        self.fond = decor.creer_fond(self.theme, self.obstacles)
        self.joueur.pos = Vector2(ARENE.centerx, ARENE.bottom - 50)
        self.tirs_joueur = []
        self.tirs_ennemis = []
        self.particules = []
        self.porte_ouverte = False
        self.ennemis = self.creer_ennemis(salle_de_boss)

    def creer_ennemis(self, salle_de_boss):
        if salle_de_boss:
            return [Boss(Vector2(ARENE.centerx, ARENE.top + 130), self.salle)]

        # De nouveaux types d'ennemis arrivent au fil des salles
        types = [Tireur]
        if self.salle >= 2:
            types.append(Chargeur)
        if self.salle >= 3:
            types.append(Mage)

        nombre = min(2 + self.salle // 2, 8)
        return [random.choice(types)(self.position_libre(), self.salle) for _ in range(nombre)]

    def position_libre(self):
        """Cherche au hasard une place loin du joueur et hors des obstacles."""
        while True:
            pos = Vector2(random.randint(ARENE.left + 40, ARENE.right - 40),
                          random.randint(ARENE.top + 40, ARENE.bottom - 120))
            trop_pres = pos.distance_to(self.joueur.pos) < DISTANCE_APPARITION
            dans_obstacle = any(rect.inflate(60, 60).collidepoint(pos) for rect in self.obstacles)
            if not trop_pres and not dans_obstacle:
                return pos

    # --- Fonctions utilisées par les ennemis ---

    def ajouter_tir_ennemi(self, pos, direction):
        self.tirs_ennemis.append(Tir(pos, direction, VITESSE_TIR_ENNEMI, 7, ORANGE))

    def ajouter_anneau(self, pos, nombre, decalage):
        for numero in range(nombre):
            self.ajouter_tir_ennemi(pos, Vector2(1, 0).rotate(numero * 360 / nombre + decalage))

    # --- Mise à jour, appelée à chaque image ---

    def mettre_a_jour(self, touches, curseur, clic, dt):
        if self.etat != "combat":
            return

        self.temps += dt
        self.tremblement -= dt
        self.mettre_a_jour_joueur(touches, curseur, clic, dt)

        # Copie ([:]) : le boss peut ajouter des ennemis à la liste pendant la boucle
        for ennemi in self.ennemis[:]:
            ennemi.mettre_a_jour(self, dt)

        for tir in self.tirs_joueur + self.tirs_ennemis:
            tir.avancer(dt, self.obstacles)

        self.gerer_collisions()
        self.retirer_les_morts()
        self.mettre_a_jour_particules(dt)
        self.verifier_fin_de_salle()

    def mettre_a_jour_joueur(self, touches, curseur, clic, dt):
        joueur = self.joueur
        a_bouge = joueur.deplacer(touches, dt, self.obstacles)
        joueur.viser(curseur)
        joueur.invincible -= dt
        joueur.attente_tir -= dt

        # On tire tout seul à l'arrêt, ou en bougeant avec le clic gauche ou Espace
        veut_tirer = not a_bouge or clic or touches[pygame.K_SPACE]
        if self.ennemis and veut_tirer and joueur.attente_tir <= 0:
            self.tirs_joueur += joueur.tirer()
            joueur.attente_tir = joueur.delai_tir
            sons.jouer("tir")

    def gerer_collisions(self):
        for tir in self.tirs_joueur:
            for ennemi in self.ennemis:
                if ennemi not in tir.deja_touches and se_touchent(tir, ennemi):
                    ennemi.blesser(tir.degats)
                    tir.deja_touches.append(ennemi)
                    self.eclats(tir.pos, JAUNE, 4)
                    sons.jouer("touche")
                    if not tir.percant:
                        tir.vivant = False
                        break

        for tir in self.tirs_ennemis:
            if se_touchent(tir, self.joueur):
                tir.vivant = False
                self.blesser_joueur()

        for ennemi in self.ennemis:
            if se_touchent(ennemi, self.joueur):
                self.blesser_joueur()

    def blesser_joueur(self):
        if not self.joueur.blesser():
            return
        sons.jouer("degat")
        self.tremblement = 0.25
        self.eclats(self.joueur.pos, BLEU, 14)
        if self.joueur.vie <= 0:
            self.etat = "perdu"
            sons.jouer("defaite")

    def retirer_les_morts(self):
        self.tirs_joueur = [tir for tir in self.tirs_joueur if tir.vivant]
        self.tirs_ennemis = [tir for tir in self.tirs_ennemis if tir.vivant]

        for ennemi in self.ennemis:
            if ennemi.vie <= 0:
                self.score += 100 if ennemi.est_boss else 10
                self.eclats(ennemi.pos, ennemi.couleur, 60 if ennemi.est_boss else 18)
                sons.jouer("mort_boss" if ennemi.est_boss else "mort")
        self.ennemis = [ennemi for ennemi in self.ennemis if ennemi.vie > 0]

    def eclats(self, pos, couleur, nombre):
        for _ in range(nombre):
            vitesse = Vector2(random.uniform(40, 220), 0).rotate(random.uniform(0, 360))
            self.particules.append(Particule(pos, vitesse, random.uniform(0.2, 0.5), couleur, 4))

    def mettre_a_jour_particules(self, dt):
        if random.random() < 0.2:
            self.particules.append(decor.particule_ambiante(self.theme))
        for particule in self.particules:
            particule.mettre_a_jour(dt)
        self.particules = [particule for particule in self.particules if particule.duree > 0]

    def verifier_fin_de_salle(self):
        if self.ennemis or self.etat != "combat":
            return

        if not self.porte_ouverte:
            self.porte_ouverte = True
            self.tirs_ennemis.clear()
            if self.salle == SALLE_FINALE:
                self.etat = "victoire"
                sons.jouer("victoire")
            else:
                sons.jouer("porte")
        elif PORTE.inflate(0, 50).collidepoint(self.joueur.pos):
            self.choix = tirer_trois_choix(self.ameliorations_prises)
            self.etat = "choix"
            sons.jouer("choix")

    # --- Clics de souris sur les menus ---

    def clic(self, pos):
        if self.etat == "choix":
            for carte, amelioration in zip(CARTES, self.choix):
                if carte.collidepoint(pos):
                    self.choisir(amelioration)

    def choisir(self, amelioration):
        amelioration["effet"](self.joueur)
        self.ameliorations_prises.append(amelioration)
        sons.jouer("pouvoir")
        self.etat = "combat"
        self.entrer_dans_salle_suivante()

    # --- Dessin ---

    def dessiner(self, ecran, polices, curseur):
        ecran.blit(self.fond, (0, 0))
        decor.dessiner_torches(ecran, self.theme)
        decor.dessiner_porte(ecran, self.porte_ouverte, self.temps)

        for objet in self.ennemis + [self.joueur] + self.tirs_joueur + self.tirs_ennemis + self.particules:
            objet.dessiner(ecran)

        # Le tremblement : on recopie l'image un peu décalée
        if self.tremblement > 0:
            ecran.blit(ecran.copy(), (random.randint(-6, 6), random.randint(-6, 6)))

        self.dessiner_infos(ecran, polices)
        if self.etat == "choix":
            self.dessiner_choix(ecran, polices, curseur)
        elif self.etat == "perdu":
            self.dessiner_fin(ecran, polices, "Perdu !", ROUGE)
        elif self.etat == "victoire":
            self.dessiner_fin(ecran, polices, "Victoire !", JAUNE)
        dessiner_viseur(ecran, curseur)

    def dessiner_infos(self, ecran, polices):
        pygame.draw.rect(ecran, NOIR, (0, 0, LARGEUR, 50))
        for numero in range(self.joueur.vie_max):
            couleur = ROUGE if numero < self.joueur.vie else (70, 70, 80)
            dessiner_coeur(ecran, 24 + numero * 26, 20, couleur)

        texte = f"Salle {self.salle}/{SALLE_FINALE} - {self.theme['nom']}   Score {self.score}"
        image = polices["petite"].render(texte, True, BLANC)
        ecran.blit(image, image.get_rect(midright=(LARGEUR - 12, 25)))

        for ennemi in self.ennemis:
            if ennemi.est_boss:
                pygame.draw.rect(ecran, NOIR, (ARENE.left + 20, ARENE.top + 12, ARENE.width - 40, 14))
                largeur = (ARENE.width - 44) * max(ennemi.vie, 0) / ennemi.vie_max
                pygame.draw.rect(ecran, ROUGE, (ARENE.left + 22, ARENE.top + 14, largeur, 10))

    def dessiner_choix(self, ecran, polices, curseur):
        assombrir(ecran)
        ecrire_centre(ecran, polices["grande"], "Choisis un pouvoir", 170, JAUNE)
        for carte, amelioration in zip(CARTES, self.choix):
            fond_carte = (75, 80, 105) if carte.collidepoint(curseur) else (45, 48, 66)
            pygame.draw.rect(ecran, fond_carte, carte, border_radius=12)
            pygame.draw.rect(ecran, amelioration["couleur"], carte, 3, border_radius=12)
            pygame.draw.circle(ecran, amelioration["couleur"], (carte.centerx, carte.top + 55), 32)
            ecrire_centre(ecran, polices["grande"], amelioration["nom"][0], carte.top + 56, NOIR, carte.centerx)
            ecrire_centre(ecran, polices["normale"], amelioration["nom"], carte.top + 118, BLANC, carte.centerx)
            for numero, ligne in enumerate(amelioration["texte"].split("\n")):
                ecrire_centre(ecran, polices["petite"], ligne, carte.top + 158 + numero * 24, GRIS, carte.centerx)

    def dessiner_fin(self, ecran, polices, titre, couleur):
        assombrir(ecran)
        ecrire_centre(ecran, polices["grande"], titre, HAUTEUR / 2 - 50, couleur)
        ecrire_centre(ecran, polices["normale"], f"Score : {self.score}", HAUTEUR / 2, BLANC)
        ecrire_centre(ecran, polices["normale"], "Appuie sur R pour recommencer", HAUTEUR / 2 + 45, BLANC)


def assombrir(ecran):
    voile = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
    voile.fill((0, 0, 0, 175))
    ecran.blit(voile, (0, 0))


def ecrire_centre(ecran, police, texte, y, couleur, x=LARGEUR / 2):
    image = police.render(texte, True, couleur)
    ecran.blit(image, image.get_rect(center=(x, y)))


def dessiner_coeur(ecran, x, y, couleur):
    pygame.draw.circle(ecran, couleur, (x - 5, y - 2), 6)
    pygame.draw.circle(ecran, couleur, (x + 5, y - 2), 6)
    pygame.draw.polygon(ecran, couleur, [(x - 11, y), (x + 11, y), (x, y + 12)])


def dessiner_viseur(ecran, curseur):
    x, y = curseur
    pygame.draw.circle(ecran, BLANC, curseur, 10, 2)
    pygame.draw.line(ecran, BLANC, (x - 15, y), (x + 15, y), 1)
    pygame.draw.line(ecran, BLANC, (x, y - 15), (x, y + 15), 1)


def creer_polices():
    return {
        "petite": pygame.font.Font(None, 24),
        "normale": pygame.font.Font(None, 30),
        "grande": pygame.font.Font(None, 46),
    }


def main():
    pygame.init()
    sons.charger()
    # Une icône entièrement transparente remplace le logo pygame affiché par défaut
    pygame.display.set_icon(pygame.Surface((32, 32), pygame.SRCALPHA))
    ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("test jeu py")
    pygame.mouse.set_visible(False)  # le viseur dessiné par le jeu remplace la flèche
    horloge = pygame.time.Clock()
    polices = creer_polices()
    partie = Partie()

    en_cours = True
    while en_cours:
        # dt = temps écoulé depuis l'image précédente, plafonné pour éviter
        # un énorme saut quand on déplace la fenêtre
        dt = min(horloge.tick(FPS) / 1000, 0.05)
        curseur = pygame.mouse.get_pos()

        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                en_cours = False
            elif evenement.type == pygame.MOUSEBUTTONDOWN and evenement.button == 1:
                partie.clic(evenement.pos)
            elif evenement.type == pygame.KEYDOWN:
                if evenement.key == pygame.K_ESCAPE:
                    en_cours = False
                elif evenement.key == pygame.K_r and partie.etat in ("perdu", "victoire"):
                    partie = Partie()

        partie.mettre_a_jour(pygame.key.get_pressed(), curseur, pygame.mouse.get_pressed()[0], dt)
        partie.dessiner(ecran, polices, curseur)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
