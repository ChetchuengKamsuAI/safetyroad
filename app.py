import streamlit as st
import sqlite3
import pandas as pd
import folium
from folium import plugins
import matplotlib.pyplot as plt
import seaborn as sns
from openai import OpenAI

# Initialisation de la clé API OpenAI
api_key = "sk-..."  # Remplacez par votre clé API OpenAI
client = OpenAI(api_key=api_key)

# Vérification de la clé API
if not client.api_key:
    raise ValueError("Clé API OpenAI manquante.")

# Configuration Streamlit
st.set_page_config(page_title="Application d'Infrastructure Routière", page_icon="🦺", layout="wide")
st.title("Application d'Infrastructure Routière")

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

# Fonction pour obtenir une réponse du chatbot OpenAI
def get_chatgpt_response(user_input):
    try:
        response = client.completions.create(
            model="gpt-3.5-turbo",
            prompt=user_input,
            max_tokens=150
        )
        if 'choices' in response and len(response['choices']) > 0:
            return response['choices'][0]['message']['content']
        return "Aucune réponse valide reçue."
    except Exception as e:
        st.error(f"Erreur : {e}")
        return "Une erreur est survenue. Veuillez réessayer."

# Onglets principaux
tabs = st.tabs(["Dashboard", "Carte", "Signalement", "Chatbot"])

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

# Onglet Chatbot
with tabs[3]:
    st.header("Chatbot")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("Posez votre question :")
    if st.button("Envoyer"):
        if user_input:
            st.session_state.chat_history.append(("Vous", user_input))
            response = get_chatgpt_response(user_input)
            st.session_state.chat_history.append(("Chatbot", response))

    for speaker, message in st.session_state.chat_history:
        st.write(f"**{speaker}:** {message}")
