import streamlit as st 
import sqlite3
import pandas as pd
import folium
from folium import plugins
import matplotlib.pyplot as plt
import seaborn as sns
import requests

# Configuration Streamlit
st.set_page_config(page_title="Application d'Infrastructure Routière", page_icon="🦺", layout="wide")
st.title("Application d'Infrastructure Routière")

# Configuration SerpAPI
API_KEY = '6328b60d23198d8e3ef25bad85cc2760b9b3fa4de8a83bdb0bfc0fc124714dcd'

# Fonction pour établir la connexion à la base de données
def get_db_connection():
    try:
        # Remplacez 'database_name.db' par le nom de votre fichier de base de données SQLite
        conn = sqlite3.connect("infrastructures_routieres.db")
        return conn
    except Exception as e:
        st.error(f"Erreur de connexion à la base de données: {e}")
        return None

# Fonction pour récupérer les actualités via SerpAPI
def get_agriculture_news(api_key):
    # Définir les paramètres de la requête
    params = {
        'engine': 'google_news',
        'q': 'road infrastructure in cameroon',  # Recherche sur l'agriculture au Cameroun
        'api_key': api_key,
    }

    # Effectuer la requête HTTP vers SerpApi
    response = requests.get('https://serpapi.com/search', params=params)

    # Vérifier si la requête a réussi
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Erreur {response.status_code}: Impossible d'obtenir les données.")
        return None

# Fonction pour récupérer les défauts
def get_defauts():
    conn = get_db_connection()
    if conn:
        try:
            query = """
                SELECT di.id, td.nom, di.description, di.localisation, 
                       di.latitude, di.longitude, di.gravite 
                FROM defauts_infrastructures di 
                JOIN types_defauts td ON di.type_defaut_id = td.id
            """
            df = pd.read_sql(query, conn)
            return df
        finally:
            conn.close()
    else:
        st.error("Impossible d'établir une connexion à la base de données.")
        return pd.DataFrame()  # Retourner un DataFrame vide en cas d'erreur

# Exemple d'utilisation
news_data = get_agriculture_news(API_KEY)

# Onglets principaux
tabs = st.tabs(["Dashboard", "Carte", "Signalement", "Actualités","Chatbot"])

# Onglet Dashboard
with tabs[0]:
    st.header("Dashboard")
    defauts_df = get_defauts()

    if not defauts_df.empty:
        st.sidebar.header("Filtres")
        gravite_filter = st.sidebar.multiselect(
            "Filtrer par gravité", options=defauts_df['gravite'].unique(), default=defauts_df['gravite'].unique()
        )
        filtered_df = defauts_df[defauts_df['gravite'].isin(gravite_filter)]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("Défauts par type")
            type_counts = filtered_df['nom'].value_counts()
            plt.figure(figsize=(5, 3))
            sns.barplot(x=type_counts.index, y=type_counts.values, palette="Blues_d")
            plt.xticks(rotation=45)
            st.pyplot(plt)

        with col2:
            st.subheader("Défauts par gravité")
            gravite_counts = filtered_df['gravite'].value_counts()
            plt.figure(figsize=(5, 3))
            sns.barplot(x=gravite_counts.index, y=gravite_counts.values, palette="Reds_d")
            st.pyplot(plt)

        with col3:
            st.subheader("Proportion par gravité")
            gravite_counts.plot.pie(autopct="%1.1f%%", colors=sns.color_palette("Reds_d"))
            plt.ylabel("")
            st.pyplot(plt)

        st.subheader("Distribution des défauts par gravité")
        plt.figure(figsize=(10, 4))
        sns.histplot(data=filtered_df, x="gravite", hue="nom", multiple="stack", palette="viridis")
        plt.title("Histogramme des défauts")
        st.pyplot(plt)

# Onglet Carte
with tabs[1]:
    st.header("Carte des défauts")
    defauts_df = get_defauts()
    if not defauts_df.empty:
        m = folium.Map(location=[4.0, 12.0], zoom_start=7)
        for _, row in defauts_df.iterrows():
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=f"{row['nom']}: {row['description']}",
                icon=folium.Icon(color="red" if row['gravite'] == "critique" else "orange")
            ).add_to(m)
        st.components.v1.html(m._repr_html_(), height=600)

# Onglet Signalement
with tabs[2]:
    st.header("Signalement")
    with st.form("signalement_form"):
        usager_id = st.number_input("ID de l'usager", min_value=1, placeholder="Entrez votre ID d'usager")
        type_defaut = st.selectbox("Type de défaut", ["Nids-de-poule", "Route fissurée", "Débris", "Éclairage"])
        description = st.text_area("Description")
        localisation = st.text_input("Localisation")
        gravite = st.selectbox("Gravité", ["mineur", "majeur", "critique"])
        latitude = st.number_input("Latitude", format="%.6f")
        longitude = st.number_input("Longitude", format="%.6f")
        photo = st.file_uploader("Télécharger une photo", type=["jpg", "png"])
        submitted = st.form_submit_button("Soumettre")
        if submitted:
            conn = get_db_connection()
            if conn:
                try:
                    conn.execute(
                        """
                        INSERT INTO defauts_infrastructures (usager_id, type_defaut_id, description, localisation, gravite, latitude, longitude)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (usager_id, type_defaut, description, localisation, gravite, latitude, longitude)
                    )
                    conn.commit()
                    st.success("Signalement enregistré avec succès.")
                except Exception as e:
                    st.error(f"Erreur lors de l'enregistrement: {e}")
                finally:
                    conn.close()

# Onglet Actualités
# Onglet Actualités
with tabs[3]:
    st.markdown("<h1 style='text-align: center;'>📰 Actualités sur l'Infrastructure Routière</h1>", unsafe_allow_html=True)
    if news_data and 'news_results' in news_data and len(news_data['news_results']) > 0:
        for article in news_data['news_results']:
            st.subheader(article['title'])
            st.write(f"**Source**: {article['source']['name']}")
            st.write(article.get('snippet', 'No description available.'))
            if 'icon' in article['source']:
                st.image(article['source']['icon'], width=40)
            if 'thumbnail' in article:
                st.image(article['thumbnail'], use_container_width=True)  # Modification ici
            st.write(f"**Date**: {article['date']}")
            st.write(f"[Lire la suite]({article['link']})")
            st.write("---")
    else:
        st.write("Aucun article d'actualité disponible.")
# Onglet Chatbot
with tabs[4]:
    st.header("Chatbot")
    st.write("Posez vos questions au Chatbot ci-dessous.")
    
    # Interface utilisateur pour interagir avec le chatbot
    user_input = st.text_input("Votre question :", placeholder="Entrez votre question ici...")
    
    if st.button("Envoyer"):
        if user_input.strip():  # Vérifie si l'entrée utilisateur n'est pas vide
            url = "https://infinite-gpt.p.rapidapi.com/infinite-gpt"
            payload = {
                "query": user_input,
                "sysMsg": "You are a friendly Chatbot."
            }
            headers = {
                "x-rapidapi-key": "b42adb4e32msh8d21b5255dfbcbap175e61jsn94765790282f",
                "x-rapidapi-host": "infinite-gpt.p.rapidapi.com",
                "Content-Type": "application/json"
            }
            
            try:
                response = requests.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    result = response.json()
                    st.write("### Réponse du Chatbot :")
                    st.write(result.get("response", "Désolé, aucune réponse reçue."))
                else:
                    st.error(f"Erreur {response.status_code}: Impossible de contacter le chatbot.")
            except Exception as e:
                st.error(f"Une erreur est survenue : {e}")
        else:
            st.warning("Veuillez entrer une question avant d'envoyer.")
