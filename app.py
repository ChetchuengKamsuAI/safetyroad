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
SERPAPI_API_KEY = "6328b60d23198d8e3ef25bad85cc2760b9b3fa4de8a83bdb0bfc0fc124714dcd"  # Remplacez par votre clé API
SERPAPI_URL = "https://serpapi.com/search"

# Fonction pour récupérer les actualités via SerpAPI
def fetch_news_from_serpapi(query="road infrastructure"):
    params = {
        "engine": "google_news",
        "q": query,
        "api_key": SERPAPI_API_KEY
    }
    response = requests.get(SERPAPI_URL, params=params)
    if response.status_code == 200:
        return response.json().get("articles", [])
    else:
        st.error("Erreur lors de la récupération des actualités. Veuillez vérifier votre clé API SerpAPI.")
        return []

# Fonction pour se connecter à la base de données
def get_db_connection():
    conn = sqlite3.connect('infrastructures_routieres.db')
    return conn

# Fonction pour récupérer les défauts
def get_defauts():
    conn = get_db_connection()
    query = """
        SELECT di.id, td.nom, di.description, di.localisation, 
               di.latitude, di.longitude, di.gravite 
        FROM defauts_infrastructures di 
        JOIN types_defauts td ON di.type_defaut_id = td.id
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Onglets principaux
tabs = st.tabs(["Dashboard", "Carte", "Signalement", "Actualités"])

# Onglet Dashboard
with tabs[0]:
    st.header("Dashboard")
    defauts_df = get_defauts()

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

    # Histogramme
    st.subheader("Distribution des défauts par gravité")
    plt.figure(figsize=(10, 4))
    sns.histplot(data=filtered_df, x="gravite", hue="nom", multiple="stack", palette="viridis")
    plt.title("Histogramme des défauts")
    st.pyplot(plt)

# Onglet Carte
with tabs[1]:
    st.header("Carte des défauts")
    defauts_df = get_defauts()
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
            conn.execute(
                """
                INSERT INTO defauts_infrastructures (usager_id, type_defaut_id, description, localisation, gravite, latitude, longitude)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (usager_id, type_defaut, description, localisation, gravite, latitude, longitude)
            )
            conn.commit()
            conn.close()
            st.success("Signalement enregistré avec succès.")

# Onglet Actualités
with tabs[3]:
    st.header("Actualités")
    search_query = st.text_input("Recherchez des actualités", value="road safety")
    news_results = fetch_news_from_serpapi(query=search_query)

    # Afficher les actualités
    if news_results:
        for news in news_results:
            st.subheader(news["title"])
            st.write(f"**Source :** {news['source']['name']} | **Publié le :** {news.get('published_date', 'Non spécifié')}")
            st.write(news.get("snippet", "Pas de description disponible."))  # Extrait de l'article
            if "thumbnail" in news:
                st.image(news["thumbnail"], width=700)
            st.markdown(f"[Lire l'article complet]({news['link']})", unsafe_allow_html=True)
            st.markdown("---")
    else:
        st.write("Aucune actualité disponible pour le moment.")
