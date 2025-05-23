import streamlit as st
import requests
import pandas as pd
import json
import os
from typing import Dict, Any
from bs4 import BeautifulSoup
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time

#########################################
# Custom CSS voor moderne UI
#########################################
def load_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Dark Theme Base */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    
    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 2rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        margin-bottom: 1.5rem;
    }
    
    /* Gradient Text */
    .gradient-text {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    /* Modern Metrics */
    .metric-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-radius: 15px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #fff;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: rgba(255, 255, 255, 0.7);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Status Pills */
    .status-pill {
        display: inline-block;
        padding: 0.25rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 500;
        margin: 0.25rem;
    }
    
    .status-success {
        background: rgba(72, 187, 120, 0.2);
        color: #48bb78;
        border: 1px solid rgba(72, 187, 120, 0.3);
    }
    
    .status-warning {
        background: rgba(237, 137, 54, 0.2);
        color: #ed8936;
        border: 1px solid rgba(237, 137, 54, 0.3);
    }
    
    .status-danger {
        background: rgba(245, 101, 101, 0.2);
        color: #f56565;
        border: 1px solid rgba(245, 101, 101, 0.3);
    }
    
    /* Modern Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        color: white;
        padding: 0.75rem;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: rgba(15, 12, 41, 0.8);
        backdrop-filter: blur(10px);
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Loading Animation */
    .loading-wave {
        display: inline-block;
        width: 80px;
        height: 40px;
    }
    
    .loading-wave div {
        display: inline-block;
        width: 8px;
        height: 100%;
        margin: 0 2px;
        background: #667eea;
        animation: wave 1.2s infinite ease-in-out;
    }
    
    .loading-wave div:nth-child(1) { animation-delay: -0.24s; }
    .loading-wave div:nth-child(2) { animation-delay: -0.12s; }
    .loading-wave div:nth-child(3) { animation-delay: 0; }
    
    @keyframes wave {
        0%, 40%, 100% {
            transform: scaleY(0.4);
            opacity: 0.5;
        }
        20% {
            transform: scaleY(1);
            opacity: 1;
        }
    }
    
    /* Table Styling */
    .dataframe {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

#########################################
# Functies voor persistente opslag
#########################################

DATA_FILE = "data.json"

def load_persistent_data():
    """Laad data uit een lokaal JSON-bestand en zet deze in de session_state."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        st.session_state.overrides = data.get("overrides", {})
        st.session_state.cars_info = data.get("cars_info", {})
        st.session_state.rdw_cache = data.get("rdw_cache", {})
        st.session_state.wegenbelasting_cache = data.get("wegenbelasting_cache", {})
        st.session_state.stamdata = data.get("stamdata", {})
    else:
        st.session_state.overrides = {}
        st.session_state.cars_info = {}
        st.session_state.rdw_cache = {}
        st.session_state.wegenbelasting_cache = {}
        st.session_state.stamdata = {}

def save_persistent_data():
    """Sla de data uit de session_state veilig op in een JSON-bestand."""
    data = {
        "overrides": st.session_state.overrides,
        "cars_info": st.session_state.cars_info,
        "rdw_cache": st.session_state.rdw_cache,
        "wegenbelasting_cache": st.session_state.wegenbelasting_cache,
        "stamdata": st.session_state.stamdata,
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

#########################################
# Moderne Login Screen
#########################################
def show_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="glass-card" style="text-align: center; margin-top: 5rem;">
            <h1 class="gradient-text">AutoPonti</h1>
            <p style="color: rgba(255, 255, 255, 0.7); font-size: 1.1rem; margin-bottom: 2rem;">
                Autokosten Calculator
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        password = st.text_input("Voer wachtwoord in", type="password", key="password_input")
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        with col_btn2:
            if st.button("🔓 Login", use_container_width=True):
                if password == "AutoPonti":
                    st.session_state.authenticated = True
                    load_persistent_data()
                    st.success("✅ Succesvol ingelogd!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Onjuist wachtwoord")

#########################################
# Python-functies (geoptimaliseerd)
#########################################

def get_all_rdw_data(kenteken: str) -> Dict[str, Any]:
    """Haal ALLE RDW-gegevens voor een kenteken op in één keer (gecached)."""
    kenteken = kenteken.upper().replace("-", "").strip()
    if kenteken in st.session_state.rdw_cache:
        return st.session_state.rdw_cache[kenteken]
    try:
        url_basis = f"https://opendata.rdw.nl/resource/m9d7-ebf2.json?kenteken={kenteken}"
        response_basis = requests.get(url_basis)
        response_basis.raise_for_status()
        data_basis = response_basis.json()
        if not data_basis:
            st.session_state.rdw_cache[kenteken] = {"error": "Geen data gevonden"}
            return {"error": "Geen data gevonden"}
        data_basis = data_basis[0]
        url_brandstof = f"https://opendata.rdw.nl/resource/8ys7-d773.json?kenteken={kenteken}"
        response_brandstof = requests.get(url_brandstof)
        response_brandstof.raise_for_status()
        data_brandstof = response_brandstof.json()
        if data_brandstof:
            data_basis.update(data_brandstof[0])
        for date_field in ["datum_eerste_toelating", "vervaldatum_apk"]:
            if data_basis.get(date_field):
                try:
                    data_basis[date_field] = pd.to_datetime(data_basis[date_field], dayfirst=True).strftime('%d-%m-%Y')
                except ValueError:
                    pass
        if data_basis.get("datum_eerste_toelating"):
            try:
                data_basis["datum_eerste_toelating"] = str(pd.to_datetime(data_basis["datum_eerste_toelating"], dayfirst=True).year)
            except ValueError:
                pass
        st.session_state.rdw_cache[kenteken] = data_basis
        return data_basis
    except requests.RequestException as e:
        st.session_state.rdw_cache[kenteken] = {"error": f"Error: {e}"}
        return {"error": f"Error: {e}"}

def get_rdw_data(kenteken: str, veld: str) -> Any:
    """Haal een specifiek RDW-veld op, gebruikmakend van de gecachede data."""
    all_data = get_all_rdw_data(kenteken)
    if "error" in all_data:
        return all_data["error"]
    return all_data.get(veld)

def get_rdw_brandstof(kenteken: str) -> str:
    """Haal brandstoftype op."""
    return get_rdw_data(kenteken, "brandstof_omschrijving")

def get_rdw_brandstof_verbruik(kenteken: str, brandstof_type_keuze: str = None) -> float:
    """
    Haal brandstofverbruik op, met WLTP-voorkeur en correctie/fallback voor elektrische auto's.
    """
    brandstof = get_rdw_brandstof(kenteken)
    if brandstof_type_keuze == "ELEKTRICITEIT" or (brandstof and "ELEKTR" in brandstof.upper()):
        verbruik = get_rdw_data(kenteken, "elektrisch_verbruik_enkel_elektrisch_wltp")
        if verbruik is None or verbruik == "Veld niet gevonden":
            verbruik = 170
        try:
            numeric_verbruik = float(verbruik)
        except (ValueError, TypeError):
            numeric_verbruik = 0.0
        return numeric_verbruik / 10
    else:
        verbruik = get_rdw_data(kenteken, "brandstof_verbruik_gecombineerd_wltp")
        if verbruik is None or verbruik == "Veld niet gevonden":
            verbruik = get_rdw_data(kenteken, "brandstofverbruik_gecombineerd")
        try:
            numeric_verbruik = float(verbruik)
        except (ValueError, TypeError):
            numeric_verbruik = 0.0
        return numeric_verbruik

def get_overijssel_price(kenteken: str) -> str:
    """Haal wegenbelasting op van wegenbelasting.net (webscraping, gecached)."""
    if kenteken in st.session_state.wegenbelasting_cache:
        return st.session_state.wegenbelasting_cache[kenteken]
    url = "https://www.wegenbelasting.net/kenteken-check/"
    post_data = {"submit_berekenen_kenteken": "1", "k": kenteken}
    try:
        response = requests.post(url, data=post_data)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find("table", class_="wb-resultaat")
        if table:
            for row in table.find_all("tr"):
                if "Overijssel" in row.text:
                    cells = row.find_all("td")
                    if len(cells) >= 2:
                        price_overijssel = cells[1].text.strip()
                        st.session_state.wegenbelasting_cache[kenteken] = price_overijssel
                        return price_overijssel
        st.session_state.wegenbelasting_cache[kenteken] = "Niet gevonden"
        return "Niet gevonden"
    except requests.RequestException as e:
        st.session_state.wegenbelasting_cache[kenteken] = f"Error: {e}"
        return f"Error: {e}"

#########################################
# Visualisatie functies
#########################################

def create_cost_comparison_chart(results):
    """Maak een moderne vergelijkingsgrafiek voor kosten."""
    fig = go.Figure()
    
    # Data prepareren
    kentekens = [r['Kenteken'] for r in results]
    koop_kosten = [float(r['Totale kosten p/m incl brandstof'].replace("€", "").replace(",", "")) for r in results]
    lease_kosten = [float(r['Leaseprijs incl brandstof'].replace("€", "").replace(",", "")) for r in results]
    
    # Bars toevoegen
    fig.add_trace(go.Bar(
        name='Koopkosten',
        x=kentekens,
        y=koop_kosten,
        marker_color='rgba(102, 126, 234, 0.8)',
        marker_line_color='rgba(102, 126, 234, 1)',
        marker_line_width=1.5,
        text=[f'€{k:,.0f}' for k in koop_kosten],
        textposition='outside',
    ))
    
    fig.add_trace(go.Bar(
        name='Leasekosten',
        x=kentekens,
        y=lease_kosten,
        marker_color='rgba(118, 75, 162, 0.8)',
        marker_line_color='rgba(118, 75, 162, 1)',
        marker_line_width=1.5,
        text=[f'€{l:,.0f}' for l in lease_kosten],
        textposition='outside',
    ))
    
    # Layout aanpassen
    fig.update_layout(
        title='Kostenvergelijking per Auto',
        xaxis_title='Kenteken',
        yaxis_title='Kosten per maand (€)',
        barmode='group',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
        legend=dict(
            bgcolor='rgba(0,0,0,0)',
            bordercolor='rgba(255,255,255,0.1)',
            borderwidth=1
        ),
        margin=dict(t=60, b=40, l=40, r=40),
        height=400
    )
    
    return fig

def create_cost_breakdown_pie(result):
    """Maak een pie chart voor kostenverdeling."""
    # Extract costs
    afschrijving = float(result['Aanschafprijs excl btw'].replace("€", "").replace(",", "")) * (float(result['Afschrijvings%'].replace("%", "")) / 100) / 12
    rente = float(result['Rente p/m'].replace("€", "").replace(",", ""))
    verzekering = float(result['Verzekering p/m'].replace("€", "").replace(",", ""))
    onderhoud = float(result['Onderhoud p/m'].replace("€", "").replace(",", ""))
    belasting = float(result['Rijtuigenbelasting'].replace("€", "").replace(",", ""))
    brandstof = float(result['Brandstof p/m'].replace("€", "").replace(",", ""))
    
    labels = ['Afschrijving', 'Rente', 'Verzekering', 'Onderhoud', 'Wegenbelasting', 'Brandstof']
    values = [afschrijving, rente, verzekering, onderhoud, belasting, brandstof]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.3,
        marker=dict(
            colors=['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe'],
            line=dict(color='white', width=2)
        ),
        textfont=dict(color='white'),
        textposition='outside',
        textinfo='label+percent'
    )])
    
    fig.update_layout(
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=0, b=0, l=0, r=0),
        height=300
    )
    
    return fig

#########################################
# Hoofdapplicatie
#########################################

st.set_page_config(
    page_title="AutoPonti - Autokosten Calculator",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Laad CSS
load_css()

# Authenticatie check
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    show_login()
    st.stop()

# Header
st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h1 class="gradient-text">🚗 AutoPonti Calculator</h1>
    <p style="color: rgba(255, 255, 255, 0.8); font-size: 1.2rem;">
        Geavanceerde autokosten analyse voor Pontifexx
    </p>
</div>
""", unsafe_allow_html=True)

# Info sectie
with st.container():
    st.markdown("""
    <div class="glass-card">
        <h3 style="color: #667eea; margin-bottom: 1rem;">📊 Over deze calculator</h3>
        <p style="color: rgba(255, 255, 255, 0.8);">
            Wij berekenen hier de autokosten voor auto's die we aanschaffen zodat het past in onze autoregeling.
            De budgetruimte per rol is in de onderstaande tabel weergegeven, aanschaf van een auto gaat altijd in overleg met Johan.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabel afbeelding met styling
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("tabel.jpg", use_column_width=True)

# Sidebar voor stamdata
with st.sidebar:
    st.markdown("""
    <div class="glass-card">
        <h3 style="color: #667eea;">⚙️ Algemene Instellingen</h3>
    </div>
    """, unsafe_allow_html=True)
    
    jaarlijkse_km = st.number_input(
        "🚗 Jaarlijkse kilometers",
        value=st.session_state.stamdata.get('jaarlijkse_km', 35000),
        min_value=0,
        key="jaarlijkse_km_global",
        help="Gemiddeld aantal kilometers per jaar"
    )
    
    brandstofprijs = st.number_input(
        "⛽ Brandstofprijs (€/L)",
        value=st.session_state.stamdata.get('brandstofprijs', 2.00),
        min_value=0.0,
        key="brandstofprijs_global",
        format="%.2f"
    )
    
    elektraprijs = st.number_input(
        "⚡ Elektriciteitsprijs (€/kWh)",
        value=st.session_state.stamdata.get('elektraprijs', 0.35),
        min_value=0.0,
        key="elektraprijs_global",
        format="%.2f"
    )
    
    rente = st.number_input(
        "💰 Rente (%)",
        value=st.session_state.stamdata.get('rente', 5.0),
        min_value=0.0,
        max_value=100.0,
        key="rente_global",
        format="%.1f"
    )
    
    # Update stamdata
    st.session_state.stamdata['jaarlijkse_km'] = jaarlijkse_km
    st.session_state.stamdata['brandstofprijs'] = brandstofprijs
    st.session_state.stamdata['elektraprijs'] = elektraprijs
    st.session_state.stamdata['rente'] = rente
    
    st.markdown("---")
    
    # Save button
    if st.button("💾 Instellingen Opslaan", use_container_width=True):
        save_persistent_data()
        st.success("✅ Opgeslagen!")

# Main content
st.markdown("""
<div class="glass-card">
    <h3 style="color: #667eea; margin-bottom: 1rem;">📝 Kenteken Invoer</h3>
    <p style="color: rgba(255, 255, 255, 0.7); margin-bottom: 1rem;">
        Voer hieronder één of meerdere kentekens in (één per regel) voor analyse.
    </p>
</div>
""", unsafe_allow_html=True)

kentekens = st.text_area("", height=100, placeholder="Bijvoorbeeld:\nAB-123-CD\nEF-456-GH")

if kentekens:
    with st.spinner('🔄 Data ophalen en berekeningen uitvoeren...'):
        kenteken_list = [k.strip().upper() for k in kentekens.split('\n') if k.strip()]
        results = []
        
        # Progress bar
        progress_bar = st.progress(0)
        
        for idx, kenteken in enumerate(kenteken_list):
            progress_bar.progress((idx + 1) / len(kenteken_list))
            
            car_data = get_all_rdw_data(kenteken)
            if "error" in car_data:
                st.warning(f"⚠️ Fout bij ophalen data voor {kenteken}: {car_data['error']}")
                continue
            
            catalogusprijs = car_data.get("catalogusprijs")
            merk = car_data.get("merk", "Onbekend")
            model = car_data.get("handelsbenaming", "Onbekend")
            
            # Overrides en standaardwaarden
            aanschafwaarde = st.session_state.overrides.get(
                f'aanschaf_{kenteken}', 
                float(catalogusprijs) if catalogusprijs and catalogusprijs != "Geen data gevonden" else 15000.00
            )
            afschrijving_percentage = st.session_state.overrides.get(f'afschrijving_{kenteken}', 15.0)
            verzekering_per_maand = st.session_state.overrides.get(f'verzekering_{kenteken}', 200.0)
            leaseprijs = st.session_state.overrides.get(f'lease_{kenteken}', 0.0)
            onderhoud_per_maand = st.session_state.overrides.get(f'onderhoud_{kenteken}', 80.0)
            
            bouwjaar = car_data.get("datum_eerste_toelating")
            gewicht = car_data.get("massa_rijklaar")
            kleur = car_data.get("eerste_kleur")
            apk = car_data.get("vervaldatum_apk")
            brandstof = car_data.get("brandstof_omschrijving")
            co2 = car_data.get("co2_uitstoot_gecombineerd")
            if co2 is None or co2 == "Veld niet gevonden":
                co2 = car_data.get("co2_uitstoot_nettomax")
            fijnstof = car_data.get("uitstoot_deeltjes_licht")
            toelating = car_data.get("datum_eerste_toelating")
            
            # Rijtuigenbelasting
            wb_str = get_overijssel_price(kenteken)
            try:
                if wb_str.startswith("€"):
                    wb_numeric = float(wb_str.split(" ")[1].replace(",", "."))
                else:
                    wb_numeric = float(wb_str.replace(",", "."))
            except Exception:
                wb_numeric = 0.0
            
            # Berekeningen
            afschrijving_per_maand_calc = (aanschafwaarde * (afschrijving_percentage / 100)) / 12
            verbruik = get_rdw_brandstof_verbruik(kenteken)
            if brandstof and "ELEKTR" in brandstof.upper():
                kosten_brandstof_per_jaar = (jaarlijkse_km / 100) * verbruik * elektraprijs
            else:
                kosten_brandstof_per_jaar = (jaarlijkse_km / 100) * verbruik * brandstofprijs
            brandstof_per_maand = kosten_brandstof_per_jaar / 12
            rente_per_jaar = aanschafwaarde * (rente / 100)
            rente_per_maand = rente_per_jaar / 12
            
            kosten_excl_brandstof = afschrijving_per_maand_calc + rente_per_maand + verzekering_per_maand + onderhoud_per_maand + wb_numeric
            kosten_incl_brandstof = kosten_excl_brandstof + brandstof_per_maand
            leaseprijs_incl = leaseprijs + brandstof_per_maand
            verschil = leaseprijs_incl - kosten_incl_brandstof
            
            results.append({
                'Kenteken': kenteken,
                'Merk': merk,
                'Model': model,
                'Catalogusprijs': f"€ {float(catalogusprijs):,.2f}" if catalogusprijs and catalogusprijs != "Geen data gevonden" else "Niet gevonden",
                'Aanschafprijs excl btw': f"€ {aanschafwaarde:,.2f}",
                'Afschrijvings%': f"{afschrijving_percentage:.2f}%",
                'Rijtuigenbelasting': f"€ {wb_numeric:,.2f}",
                'Onderhoud p/m': f"€ {onderhoud_per_maand:,.2f}",
                'Brandstofverbruik': f"{verbruik:.2f} L/100km" if brandstof and "ELEKTR" not in brandstof.upper() else f"{verbruik:.2f} kWh/100km",
                'Brandstof p/m': f"€ {brandstof_per_maand:,.2f}",
                'Rente p/m': f"€ {rente_per_maand:,.2f}",
                'Verzekering p/m': f"€ {verzekering_per_maand:,.2f}",
                'Totale kosten p/m excl brandstof': f"€ {kosten_excl_brandstof:,.2f}",
                'Totale kosten p/m incl brandstof': f"€ {kosten_incl_brandstof:,.2f}",
                'Leaseprijs p/m': f"€ {leaseprijs:,.2f}",
                'Leaseprijs incl brandstof': f"€ {leaseprijs_incl:,.2f}",
                'Verschil lease-koop': f"€ {verschil:,.2f}",
                'Bouwjaar': bouwjaar,
                'Gewicht': f"{gewicht} kg" if gewicht and gewicht != "Geen data gevonden" else "Niet gevonden",
                'Kleur': kleur if kleur else "Onbekend",
                'APK': apk if apk else "Onbekend",
                'CO2': f"{co2} g/km" if co2 else "Onbekend",
                'Fijnstof': f"{fijnstof} mg/km" if fijnstof else "Onbekend",
                'Toelating': toelating
            })
        
        progress_bar.empty()
    
    if results:
        # Summary cards
        st.markdown("""
        <div class="glass-card">
            <h3 style="color: #667eea; margin-bottom: 1.5rem;">📊 Overzicht</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_koop = sum([float(r['Totale kosten p/m incl brandstof'].replace("€", "").replace(",", "")) for r in results]) / len(results)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Gem. Koopkosten</div>
                <div class="metric-value">€ {avg_koop:,.0f}</div>
                <div class="metric-label">per maand</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            avg_lease = sum([float(r['Leaseprijs incl brandstof'].replace("€", "").replace(",", "")) for r in results]) / len(results)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Gem. Leasekosten</div>
                <div class="metric-value">€ {avg_lease:,.0f}</div>
                <div class="metric-label">per maand</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            beste_deal = min(results, key=lambda x: float(x['Verschil lease-koop'].replace("€", "").replace(",", "")))
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Beste Deal</div>
                <div class="metric-value">{beste_deal['Merk']}</div>
                <div class="metric-label">{beste_deal['Kenteken']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            aantal_voordelig = len([r for r in results if float(r['Verschil lease-koop'].replace("€", "").replace(",", "")) < 0])
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Lease Voordeliger</div>
                <div class="metric-value">{aantal_voordelig}/{len(results)}</div>
                <div class="metric-label">auto's</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Visualisaties
        st.markdown("""
        <div class="glass-card" style="margin-top: 2rem;">
            <h3 style="color: #667eea; margin-bottom: 1.5rem;">📈 Visualisaties</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            fig = create_cost_comparison_chart(results)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if results:
                selected_car = st.selectbox(
                    "Selecteer auto voor kostenverdeling:",
                    [f"{r['Merk']} - {r['Model']} ({r['Kenteken']})" for r in results]
                )
                selected_idx = [f"{r['Merk']} - {r['Model']} ({r['Kenteken']})" for r in results].index(selected_car)
                fig_pie = create_cost_breakdown_pie(results[selected_idx])
                st.plotly_chart(fig_pie, use_container_width=True)
        
        # Gedetailleerde tabel
        st.markdown("""
        <div class="glass-card" style="margin-top: 2rem;">
            <h3 style="color: #667eea; margin-bottom: 1.5rem;">📋 Gedetailleerde Resultaten</h3>
        </div>
        """, unsafe_allow_html=True)
        
        df = pd.DataFrame(results)
        main_columns = [
            "Kenteken", "Merk", "Model", "Totale kosten p/m incl brandstof",
            "Leaseprijs incl brandstof", "Verschil lease-koop"
        ]
        df_display = df[main_columns]
        
        st.dataframe(
            df_display.style.applymap(
                lambda x: 'background-color: rgba(72, 187, 120, 0.2); color: #48bb78' 
                if isinstance(x, str) and x.startswith('€ -') else ''
            ),
            use_container_width=True,
            hide_index=True
        )
        
        # Auto-specifieke aanpassingen
        st.markdown("""
        <div class="glass-card" style="margin-top: 2rem;">
            <h3 style="color: #667eea; margin-bottom: 1.5rem;">⚙️ Auto-specifieke Instellingen</h3>
        </div>
        """, unsafe_allow_html=True)
        
        for idx, res in enumerate(results):
            kenteken = res['Kenteken']
            merk = res['Merk']
            model = res['Model']
            
            # Status bepalen
            verschil_val = float(res['Verschil lease-koop'].replace("€", "").replace(",", ""))
            if verschil_val < -100:
                status_class = "status-success"
                status_text = "Lease voordelig"
            elif verschil_val > 100:
                status_class = "status-danger"
                status_text = "Koop voordelig"
            else:
                status_class = "status-warning"
                status_text = "Vergelijkbaar"
            
            with st.expander(f"🚗 {merk} - {model} - {kenteken}"):
                st.markdown(f'<span class="status-pill {status_class}">{status_text}</span>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**💰 Financiële instellingen**")
                    
                    new_aanschaf = st.number_input(
                        "Aanschafprijs excl btw (€)",
                        value=st.session_state.overrides.get(
                            f'aanschaf_{kenteken}', 
                            float(res['Aanschafprijs excl btw'].replace("€", "").replace(",", "")) if res['Aanschafprijs excl btw'] != "Niet gevonden" else 15000.00
                        ),
                        key=f"aanschaf_{kenteken}_exp",
                        format="%.2f"
                    )
                    st.session_state.overrides[f'aanschaf_{kenteken}'] = new_aanschaf
                    
                    new_afschrijving = st.number_input(
                        "Afschrijvingspercentage per jaar (%)",
                        value=st.session_state.overrides.get(
                            f'afschrijving_{kenteken}', 
                            float(res['Afschrijvings%'].replace("%", "")) if res['Afschrijvings%'] != "Onbekend" else 15.0
                        ),
                        min_value=0.0,
                        max_value=100.0,
                        key=f"afschrijving_{kenteken}_exp",
                        format="%.1f"
                    )
                    st.session_state.overrides[f'afschrijving_{kenteken}'] = new_afschrijving
                    
                    new_leaseprijs = st.number_input(
                        "Leaseprijs p/m (€)",
                        value=st.session_state.overrides.get(
                            f'lease_{kenteken}', 
                            float(res['Leaseprijs p/m'].replace("€", "").replace(",", "")) if res['Leaseprijs p/m'] != "Niet gevonden" else 0.0
                        ),
                        min_value=0.0,
                        key=f"lease_{kenteken}_exp",
                        format="%.2f"
                    )
                    st.session_state.overrides[f'lease_{kenteken}'] = new_leaseprijs
                
                with col2:
                    st.markdown("**🛡️ Verzekering & Onderhoud**")
                    
                    new_verzekering = st.number_input(
                        "Verzekering p/m (€)",
                        value=st.session_state.overrides.get(
                            f'verzekering_{kenteken}', 
                            float(res['Verzekering p/m'].replace("€", "").replace(",", "")) if res['Verzekering p/m'] != "Niet gevonden" else 200.0
                        ),
                        min_value=0.0,
                        key=f"verzekering_{kenteken}_exp",
                        format="%.2f"
                    )
                    st.session_state.overrides[f'verzekering_{kenteken}'] = new_verzekering
                    
                    new_onderhoud = st.number_input(
                        "Onderhoud p/m (€)",
                        value=st.session_state.overrides.get(
                            f'onderhoud_{kenteken}', 
                            80.0
                        ),
                        min_value=0.0,
                        key=f"onderhoud_{kenteken}_exp",
                        format="%.2f"
                    )
                    st.session_state.overrides[f'onderhoud_{kenteken}'] = new_onderhoud
                    
                    if st.button("💾 Aanpassingen opslaan", key=f"save_{kenteken}"):
                        save_persistent_data()
                        st.success("✅ Opgeslagen!")
                        time.sleep(0.5)
                        st.rerun()
                
                # Extra details in een mooie tabel
                st.markdown("---")
                st.markdown("**📄 Voertuigdetails**")
                
                detail_col1, detail_col2, detail_col3 = st.columns(3)
                with detail_col1:
                    st.metric("Bouwjaar", res['Bouwjaar'])
                    st.metric("Kleur", res['Kleur'])
                with detail_col2:
                    st.metric("Gewicht", res['Gewicht'])
                    st.metric("APK", res['APK'])
                with detail_col3:
                    st.metric("CO2 Uitstoot", res['CO2'])
                    st.metric("Fijnstof", res['Fijnstof'])
    else:
        st.warning("⚠️ Geen geldige resultaten gevonden voor de ingevoerde kentekens.")

# Auto-save
if st.session_state.authenticated:
    save_persistent_data()

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 4rem; padding: 2rem; color: rgba(255, 255, 255, 0.5);">
    <p>AutoPonti Calculator © 2024 | Ontwikkeld voor Pontifexx</p>
</div>
""", unsafe_allow_html=True)
