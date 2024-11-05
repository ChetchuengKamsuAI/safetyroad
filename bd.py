import sqlite3

# Créer une connexion à la base de données
conn = sqlite3.connect('infrastructures_routieres.db')

# Créer un curseur
cursor = conn.cursor()

# Créer la table des usagers
cursor.execute('''
CREATE TABLE IF NOT EXISTS usagers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_telephone TEXT UNIQUE NOT NULL,
    mot_de_passe TEXT NOT NULL,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

# Créer la table des types de défauts
cursor.execute('''
CREATE TABLE IF NOT EXISTS types_defauts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT UNIQUE NOT NULL,
    description TEXT
)
''')

# Créer la table des défauts d'infrastructure
cursor.execute('''
CREATE TABLE IF NOT EXISTS defauts_infrastructures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usager_id INTEGER,
    type_defaut_id INTEGER,
    description TEXT,
    localisation TEXT,
    latitude REAL,
    longitude REAL,
    gravite TEXT CHECK(gravite IN ('mineur', 'majeur', 'critique')),
    photo TEXT,
    date_signalement DATETIME DEFAULT CURRENT_TIMESTAMP,
    statut TEXT DEFAULT 'en cours',
    date_resolution DATETIME,
    FOREIGN KEY (usager_id) REFERENCES usagers (id),
    FOREIGN KEY (type_defaut_id) REFERENCES types_defauts (id)
)
''')

# Créer la table des rapports de sécurité
cursor.execute('''
CREATE TABLE IF NOT EXISTS rapports_securite (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_rapport DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_defauts INTEGER,
    defauts_resolus INTEGER,
    defauts_en_cours INTEGER,
    gravite_mineur INTEGER,
    gravite_majeur INTEGER,
    gravite_critique INTEGER
)
''')

# Créer des index pour améliorer les performances
cursor.execute('CREATE INDEX IF NOT EXISTS idx_type_defaut ON defauts_infrastructures(type_defaut_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_localisation ON defauts_infrastructures(localisation)')

# Insérer des exemples de types de défauts
types_defauts = [
    ('Nids-de-poule', 'Des cavités sur la route causées par l’érosion ou d’autres facteurs.'),
    ('Feu de circulation cassé', 'Un feu de circulation qui ne fonctionne pas.'),
    ('Panneau de signalisation manquant', 'Un panneau essentiel pour la sécurité routière qui n’est pas présent.'),
    ('Route fissurée', 'Fissures visibles sur la surface de la route.'),
    ('Éclairage public défectueux', 'Lampadaires qui ne fonctionnent pas dans une zone donnée.'),
    ('Glissière de sécurité endommagée', 'Barrières de sécurité sur les routes qui sont brisées ou manquantes.'),
    ('Trottoir abîmé', 'Un trottoir qui est en mauvais état ou dangereux pour les piétons.'),
    ('Marquage au sol effacé', 'Les lignes ou symboles peints sur la route qui ne sont plus visibles.'),
    ('Débris sur la route', 'Des objets ou débris qui entravent la circulation.'),
    ('Gouttière obstruée', 'Une gouttière qui empêche l’écoulement de l’eau et provoque des inondations.')
]

cursor.executemany('INSERT OR IGNORE INTO types_defauts (nom, description) VALUES (?, ?)', types_defauts)

# Insérer des exemples de défauts d'infrastructure
defauts_infrastructures = [
    (1, 1, "Gros nid-de-poule sur la route de Biyem-Assi, très dangereux.", "Biyem-Assi", 3.848, 11.508, "majeur", "nid_de_poule_biyem_assi.jpg"),
    (1, 2, "Le feu de circulation est hors service au carrefour d'Akwa.", "Akwa", 4.051, 9.708, "critique", "feu_circulation_akwa.jpg"),
    (1, 3, "Panneau Stop manquant à l'entrée de Messa.", "Messa", 3.840, 11.521, "majeur", "panneau_stop_messa.jpg"),
    (1, 4, "Route fissurée sur la route de Yaoundé à Douala.", "Route Yaoundé-Douala", 4.051, 9.708, "majeur", "route_fissuree_yaounde_douala.jpg"),
    (1, 5, "Les lampadaires sont éteints sur la rue des écoles à Bastos.", "Bastos", 3.866, 11.516, "mineur", "eclairage_bastos.jpg"),
    (1, 6, "Glissière de sécurité endommagée au niveau de l'hôpital central.", "Hôpital central", 3.848, 11.506, "majeur", "glissiere_hopital_central.jpg"),
    (1, 7, "Trottoir en très mauvais état au quartier Ngousso.", "Ngousso", 3.849, 11.539, "majeur", "trottoir_ngousso.jpg"),
    (1, 8, "Marquage au sol effacé sur la route principale.", "Route principale", 3.845, 11.508, "mineur", "marquage_route_principale.jpg"),
    (1, 9, "Débris sur la route à la sortie de Yaoundé.", "Sortie de Yaoundé", 3.845, 11.516, "majeur", "debris_sortie_yaounde.jpg"),
    (1, 10, "Gouttière obstruée près de l'école de Ngousso.", "Ngousso", 3.849, 11.539, "critique", "gouttiere_ngousso.jpg"),
    
    # 15 nouveaux exemples
    (1, 1, "Nid-de-poule sur l'avenue Kennedy à Douala.", "Avenue Kennedy", 4.051, 9.708, "majeur", "nid_de_poule_avenue_kenndy.jpg"),
    (1, 2, "Feu de circulation hors service à la place de la République.", "Place de la République", 4.051, 9.708, "critique", "feu_circulation_place_republique.jpg"),
    (1, 3, "Panneau de vitesse manquant sur la route de Limbe.", "Route de Limbe", 4.000, 9.700, "majeur", "panneau_vitesse_route_limbe.jpg"),
    (1, 4, "Route fissurée près du pont sur la rivière Wouri.", "Pont sur la Wouri", 4.060, 9.700, "majeur", "route_fissuree_pont_wouri.jpg"),
    (1, 5, "Lampadaires éteints sur la route des écoles à Buea.", "Route des écoles", 4.150, 9.200, "mineur", "eclairage_buea.jpg"),
    (1, 6, "Glissière de sécurité manquante près de l'école de Mvolyé.", "Mvolyé", 3.870, 11.510, "majeur", "glissiere_mvolye.jpg"),
    (1, 7, "Trottoir effondré près de la gare routière de Yaoundé.", "Gare routière", 3.848, 11.507, "critique", "trottoir_gare_yaounde.jpg"),
    (1, 8, "Marquage au sol effacé près de l'université de Yaoundé.", "Université de Yaoundé", 3.872, 11.515, "mineur", "marquage_universite_yaounde.jpg"),
    (1, 9, "Débris de construction sur la route à Douala.", "Douala", 4.051, 9.708, "majeur", "debris_construction_douala.jpg"),
    (1, 10, "Gouttière bouchée au marché central de Yaoundé.", "Marché central", 3.858, 11.506, "critique", "gouttiere_marche_central.jpg"),
    (1, 11, "Nid-de-poule sur la route de Nkongsamba.", "Nkongsamba", 4.950, 9.600, "majeur", "nid_de_poule_nkongsamba.jpg"),
    (1, 12, "Feu de circulation cassé au carrefour de Nkol-Eton.", "Nkol-Eton", 3.870, 11.530, "critique", "feu_circulation_nkol_eton.jpg"),
    (1, 13, "Panneau de stop absent à la sortie de l'autoroute de Kribi.", "Autoroute de Kribi", 3.800, 9.800, "majeur", "panneau_stop_kribi.jpg"),
    (1, 14, "Route en mauvais état à Dschang.", "Dschang", 5.450, 9.700, "majeur", "route_dschang.jpg"),
    (1, 15, "Éclairage public défectueux au marché de Mokolo.", "Mokolo", 3.900, 11.500, "mineur", "eclairage_mokolo.jpg"),
]

cursor.executemany('INSERT INTO defauts_infrastructures (usager_id, type_defaut_id, description, localisation, latitude, longitude, gravite, photo) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', defauts_infrastructures)

# Valider les changements et fermer la connexion
conn.commit()
conn.close()

print("Base de données créée avec succès et remplie d'exemples.")
