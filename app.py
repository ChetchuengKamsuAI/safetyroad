import streamlit as st
import sqlite3
import pandas as pd
import folium
from folium import plugins
import matplotlib.pyplot as plt
import seaborn as sns

# Connexion à la base de données
def get_db_connection():
    conn = sqlite3.connect('infrastructures_routieres.db')
    return conn

# Fonction pour récupérer les défauts d'infrastructure
def get_defauts():
    conn = get_db_connection()
    query = "SELECT di.id, td.nom, di.description, di.localisation, di.latitude, di.longitude, di.gravite FROM defauts_infrastructures di JOIN types_defauts td ON di.type_defaut_id = td.id"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Titre de l'application
st.set_page_config(page_title="Application d'Infrastructure Routière",page_icon= "🦺", layout="wide")
st.title("Application d'Infrastructure Routière")

# Onglets
tabs = st.tabs(["Dashboard", "Map", "Signalement"])

# Onglet Dashboard
with tabs[0]:
    st.header("Dashboard")

    # Récupérer les défauts d'infrastructure
    defauts_df = get_defauts()

    # Ajouter des filtres
    st.sidebar.header("Filtres")
    gravite_filter = st.sidebar.multiselect("Filtrer par gravité", options=defauts_df['gravite'].unique(), default=defauts_df['gravite'].unique())
    filtered_df = defauts_df[defauts_df['gravite'].isin(gravite_filter)]

    # Afficher les graphiques dans des colonnes
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Nombre de défauts par type")
        type_counts = filtered_df['nom'].value_counts()
        sns.barplot(x=type_counts.index, y=type_counts.values, palette='Blues_d')
        plt.xticks(rotation=45)
        plt.xlabel("Type de défaut")
        plt.ylabel("Nombre de défauts")
        st.pyplot(plt)

    with col2:
        st.subheader("Nombre de défauts par gravité")
        gravite_counts = filtered_df['gravite'].value_counts()
        sns.barplot(x=gravite_counts.index, y=gravite_counts.values, palette='Reds_d')
        plt.xticks(rotation=45)
        plt.xlabel("Gravité")
        plt.ylabel("Nombre de défauts")
        st.pyplot(plt)

    with col3:
        st.subheader("Proportion de défauts par gravité (Diagramme en cercle)")
        gravite_counts.plot.pie(autopct='%1.1f%%', colors=sns.color_palette("Reds_d"), ylabel="")
        st.pyplot(plt)

    st.subheader("Proportions de défauts par localisation")
    localisation_counts = filtered_df['localisation'].value_counts().head(10)
    plt.figure(figsize=(10, 6))
    sns.barplot(x=localisation_counts.index, y=localisation_counts.values, palette='Greens_d')
    plt.xticks(rotation=45)
    plt.xlabel("Localisation")
    plt.ylabel("Nombre de défauts")
    st.pyplot(plt)

# Onglet Map
with tabs[1]:
    st.header("Carte des défauts d'infrastructure")

    # Récupérer les défauts pour la carte
    defauts_df = get_defauts()
    
    # Créer une carte Folium centrée sur le Cameroun avec un zoom plus large
    m = folium.Map(location=[4.0, 12.0], zoom_start=7)

    # Ajouter des marqueurs pour chaque défaut
    for idx, row in defauts_df.iterrows():
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=f"{row['nom']}: {row['description']}",
            icon=folium.Icon(color='red' if row['gravite'] == 'critique' else 'orange' if row['gravite'] == 'majeur' else 'green')
        ).add_to(m)

    # Ajouter une couche de contrôle
    folium.LayerControl().add_to(m)
    
    # Afficher la carte
    st.components.v1.html(m._repr_html_(), height=600)  # Agrandir la hauteur de la carte

# Onglet Signalement
with tabs[2]:
    st.header("Formulaire de Signalement")

    with st.form("signalement_form"):
        # Champ pour l'ID de l'utilisateur
        usager_id = st.number_input("ID de l'usager", min_value=1, placeholder="Entrez votre ID d'usager")
        
        # Sélection du type de défaut
        type_defaut = st.selectbox("Type de défaut", ["Nids-de-poule", "Feu de circulation cassé", "Panneau de signalisation manquant", "Route fissurée", "Éclairage public défectueux", "Glissière de sécurité endommagée", "Trottoir abîmé", "Marquage au sol effacé", "Débris sur la route", "Gouttière obstruée"])
        
        # Champ pour la description
        description = st.text_area("Description", placeholder="Décrivez le défaut")
        
        # Champ pour la localisation
        localisation = st.text_input("Localisation", placeholder="Où se trouve le défaut ?")
        
        # Sélection de la gravité
        gravite = st.selectbox("Gravité", ["mineur", "majeur", "critique"])
        
        # Champs pour latitude et longitude
        latitude = st.number_input("Latitude", format="%.6f")
        longitude = st.number_input("Longitude", format="%.6f")
        
        # Téléchargement d'une photo
        photo = st.file_uploader("Télécharger une photo", type=["jpg", "jpeg", "png"])
        
        # Bouton de soumission
        submitted = st.form_submit_button("Soumettre")
        if submitted:
            # Code pour insérer dans la base de données ici
            # Ajoutez la logique d'insertion avec l'ID d'usager, type de défaut, description, etc.
            st.success("Votre signalement a été soumis avec succès!")
            
            # Réinitialisation des champs après soumission
            st.experimental_rerun()  # Redémarre l'application pour vider le formulaire
