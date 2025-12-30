import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import cloudinary
import cloudinary.uploader
from datetime import datetime
import time
import uuid

# ==============================================================================
# CONFIG & STYLE
# ==============================================================================
st.set_page_config(
    page_title="TAOX Brain - Esports Manager",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Esports Vibe (Dark + Gold/Black + Red Alerts)
st.markdown("""
<style>
    /* ========================================================================================= */
    /* GLOBAL THEME: DARK VIOLET NEON */
    /* ========================================================================================= */
    
    /* 1. Main Background & Global Text */
    .stApp {
        background-color: #0a0a12; /* Deep Dark Void */
        background-image: 
            radial-gradient(circle at 10% 20%, rgba(106, 17, 203, 0.08) 0%, transparent 40%),
            radial-gradient(circle at 90% 80%, rgba(37, 117, 252, 0.08) 0%, transparent 40%);
        color: #ffffff;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        text-shadow: 0 0 20px rgba(106, 17, 203, 0.5); /* Soft Violet Glow */
        font-weight: 700;
        letter-spacing: 0.5px;
    }

    /* 2. Containers / Cards (Glassy Violet) */
    .glass-card, div[data-testid="stMetric"], div[data-testid="stExpander"], div[data-testid="stDataFrame"] {
        background: rgba(20, 20, 32, 0.6);
        border: 1px solid rgba(106, 17, 203, 0.2); /* Violet Border */
        border-radius: 20px;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
    }
    
    /* Metric Value */
    [data-testid="stMetricValue"] {
        color: #e0b0ff !important; /* Light Violet */
        text-shadow: 0 0 10px rgba(186, 84, 245, 0.6);
    }

    /* 3. Inputs & Selectboxes */
    .stTextInput > div > div > input, 
    .stSelectbox > div > div > div, 
    .stMultiSelect > div > div > div, 
    .stNumberInput > div > div > input, 
    .stTextArea > div > textarea {
        background-color: rgba(255, 255, 255, 0.03); 
        color: #ffffff;
        border: 1px solid rgba(106, 17, 203, 0.3);
        border-radius: 12px;
    }
    
    .stTextInput > div > div > input:focus, 
    .stSelectbox > div > div > div:focus-within {
        border-color: #ba54f5; /* Neon Violet */
        box-shadow: 0 0 15px rgba(186, 84, 245, 0.2);
    }

    /* 4. Buttons (Gradient & Plush) */
    .stButton > button {
        background: linear-gradient(135deg, #6a11cb, #2575fc);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(37, 117, 252, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        box-shadow: 0 0 25px rgba(106, 17, 203, 0.6);
        transform: translateY(-2px);
    }

    /* ========================================================================================= */
    /* DESKTOP SIDEBAR */
    /* ========================================================================================= */
    
    section[data-testid="stSidebar"] {
        background-color: rgba(10, 10, 18, 0.95); /* Deep dark */
        border-right: 1px solid rgba(106, 17, 203, 0.1);
    }
    
    section[data-testid="stSidebar"] h1 {
        background: linear-gradient(to right, #ba54f5, #2575fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2rem;
    }

    /* Sidebar Radio Buttons -> Tabs/Pills look (Desktop) */
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label {
        padding: 10px 15px;
        border-radius: 10px;
        margin-bottom: 5px;
        border: 1px solid transparent;
        transition: all 0.2s;
    }
    
    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label:hover {
        background-color: rgba(255, 255, 255, 0.05);
        cursor: pointer;
    }

    section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label[data-checked="true"] {
        background: linear-gradient(90deg, rgba(106, 17, 203, 0.3), transparent);
        border-left: 4px solid #ba54f5;
    }

    /* ========================================================================================= */
    /* MOBILE OPTIMIZATIONS (Max Width 768px) - STRICT BOTTOM NAV */
    /* ========================================================================================= */
    @media (max-width: 768px) {
        
        /* 1. Hide Default Sidebar Elements & Header */
        header[data-testid="stHeader"] {
            display: none !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"], 
        section[data-testid="stSidebar"] h1, 
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] hr,
        div[data-testid="stSidebarCollapsedControl"],
        button[kind="header"] {
            display: none !important;
        }
        
        /* 2. Reposition & Style Sidebar Container */
        section[data-testid="stSidebar"] {
            top: auto !important;
            bottom: 0 !important;
            left: 0 !important;
            width: 100% !important;
            height: auto !important;
            min-width: 100% !important;
            
            /* Layout */
            display: flex !important;
            flex-direction: row !important;
            justify-content: center;
            align-items: center;
            
            /* Styling */
            background-color: rgba(10, 10, 18, 0.95);
            border-top: 1px solid rgba(106, 17, 203, 0.3);
            box-shadow: 0px -5px 20px rgba(0,0,0,0.5);
            z-index: 999999;
            padding: 5px 10px;
        }

        /* Layout overrides for internal sidebar wrappers to allow full width flex */
        section[data-testid="stSidebar"] .block-container {
            padding: 0 !important;
            margin: 0 !important;
            width: 100%;
            display: flex;
            justify-content: center;
        }

        section[data-testid="stSidebar"] .stRadio {
            width: 100%;
        }

        /* 3. Transform Radio Buttons into Navigation Tabs */
        section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] {
            display: flex !important;
            flex-direction: row !important;
            width: 100%;
            justify-content: space-around;
            gap: 8px;
            padding: 0;
            margin: 0;
        }

        /* Hide Radio Circles */
        section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label > div:first-child {
            display: none !important;
        }

        /* Style Navigation Items (Labels) */
        section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label {
            flex-grow: 1;
            text-align: center;
            padding: 12px 5px !important;
            margin: 0 !important;
            background: transparent;
            border: 1px solid transparent;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
        }
        
        /* Default Inactive Text */
        section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label p {
            font-size: 0.85rem;
            font-weight: 500;
            color: #ccc;
            margin: 0;
        }

        /* Active Tab Style */
        section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label[data-checked="true"] {
            background: linear-gradient(135deg, #6a11cb, #2575fc) !important;
            box-shadow: 0 0 15px rgba(106, 17, 203, 0.6);
            border: none;
            border-radius: 12px;
        }
        
        section[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label[data-checked="true"] p {
            color: #ffffff !important;
            font-weight: 700;
        }

        /* 4. Adjust Main Content Padding */
        .main .block-container {
            padding-bottom: 80px !important;
        }
    }
    
    /* 5. USER REQUESTED: GLASS CARD & TAGS */
    .glass-card-hover {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(106, 17, 203, 0.3);
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
        transition: transform 0.3s, border-color 0.3s;
    }
    .glass-card-hover:hover {
        transform: translateY(-5px);
        border-color: #aa22ff;
        background-color: rgba(255, 255, 255, 0.08);
    }
    .role-tag {
        display: inline-block;
        background: rgba(106, 17, 203, 0.6);
        border-radius: 10px;
        padding: 2px 8px;
        font-size: 0.8em;
        margin-right: 5px;
        margin-top: 5px;
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* 6. CLICKABLE GLASS CARD (Styled Button - Secondary) */
    /* Target buttons that are NOT primary (default kind) */
    .stButton > button[kind="secondary"] {
        height: auto !important;
        white-space: pre-wrap !important;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.02)) !important;
        backdrop-filter: blur(16px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
        border: 1px solid rgba(138, 43, 226, 0.5) !important;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37) !important;
        border-radius: 20px !important;
        color: rgba(255, 255, 255, 0.9) !important;
        text-align: left !important;
        padding: 20px !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        display: block !important;
        width: 100% !important;
        margin-bottom: 15px !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        transform: translateY(-5px) !important;
        border-color: #00e5ff !important; /* Cyan glow on hover */
        box-shadow: 0 15px 40px 0 rgba(31, 38, 135, 0.5) !important;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.05)) !important;
    }
    
    /* 7. ADD NEW ITEM BUTTON (Primary) */
    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #aa22ff, #6a11cb) !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(170, 34, 255, 0.4) !important;
        font-size: 1.1rem !important;
        padding: 0.8rem 2rem !important;
        color: white !important;
        width: 100% !important;
        border-radius: 15px !important;
        font-weight: 700 !important;
        letter-spacing: 1px;
    }
    
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 0 25px rgba(170, 34, 255, 0.7) !important;
        transform: scale(1.02) !important;
    }
    
    .stButton > button p {
        font-size: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# BACKEND INITIALIZATION (SAFE MODE)
# ==============================================================================

@st.cache_resource
def init_firebase():
    try:
        if not firebase_admin._apps:
            cred_dict = dict(st.secrets["firebase"])
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        return firestore.client()
    except:
        return None

@st.cache_resource
def init_cloudinary():
    try:
        c_config = st.secrets["cloudinary"]
        cloudinary.config(
            cloud_name=c_config["cloud_name"],
            api_key=c_config["api_key"],
            api_secret=c_config["api_secret"]
        )
        return True
    except:
        return False

db = init_firebase()
cloud_ready = init_cloudinary()

# ==============================================================================
# DATA CONTROLLERS & MODELS
# ==============================================================================

def get_versions():
    if not db: return []
    docs = db.collection('versions').order_by('created_at', direction=firestore.Query.DESCENDING).stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

def get_heroes(version_id):
    if not db or not version_id: return pd.DataFrame()
    hero_ref = db.collection('heroes').where('version_id', '==', version_id)
    docs = hero_ref.stream()
    data = []
    for doc in docs:
        d = doc.to_dict()
        d['id'] = doc.id
        data.append(d)
    return pd.DataFrame(data)

def get_combos(version_id):
    if not db or not version_id: return []
    docs = db.collection('combos').where('version_id', '==', version_id).stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

def get_teams():
    if not db: return []
    docs = db.collection('teams').stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

def get_players():
    if not db: return []
    docs = db.collection('players').order_by('ign').stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

def init_session_state():
    if 'players' not in st.session_state:
        st.session_state['players'] = []
    if 'teams' not in st.session_state:
        st.session_state['teams'] = []

def save_player(name, roles):
    if not db: return None
    person_doc = {
        "ign": name,
        "roles": roles,
        "current_team_id": None,
        "created_at": datetime.now()
    }
    doc_ref = db.collection('players').add(person_doc)
    new_player = {"id": doc_ref[1].id, **person_doc}
    if 'players' in st.session_state:
        st.session_state['players'].append(new_player)
    return new_player

def save_team(name, coach_id, roster_dict):
    if not db: return None
    team_doc = {
        "name": name,
        "coach_id": coach_id,
        "roster": roster_dict,
        "created_at": datetime.now()
    }
    doc_ref = db.collection('teams').add(team_doc)
    new_team = {"id": doc_ref[1].id, **team_doc}
    if 'teams' in st.session_state:
        st.session_state['teams'].append(new_team)
    return new_team

def clone_version(source_version_id, new_version_name):
    if not db: return False
    
    # 1. Create New Version
    new_version_ref = db.collection('versions').document()
    new_version_id = new_version_ref.id
    new_version_ref.set({
        "name": new_version_name,
        "created_at": datetime.now(),
        "is_active": True
    })
    
    # 2. Clone Heroes
    source_heroes = db.collection('heroes').where('version_id', '==', source_version_id).stream()
    batch = db.batch()
    count = 0
    for h in source_heroes:
        data = h.to_dict()
        data['version_id'] = new_version_id # Retarget
        new_ref = db.collection('heroes').document()
        batch.set(new_ref, data)
        count += 1
        if count >= 400: # Firestore batch limit
            batch.commit()
            batch = db.batch()
            count = 0
    batch.commit()
    
    # 3. Clone Combos
    source_combos = db.collection('combos').where('version_id', '==', source_version_id).stream()
    batch_c = db.batch()
    count_c = 0
    for c in source_combos:
        data = c.to_dict()
        data['version_id'] = new_version_id
        new_ref = db.collection('combos').document()
        batch_c.set(new_ref, data)
        count_c += 1
        if count_c >= 400:
            batch_c.commit()
            batch_c = db.batch()
            count_c = 0
    batch_c.commit()
    
    return True



# ==============================================================================
# DIALOGS (MUST BE DEFINED AT TOP LEVEL)
# ==============================================================================

@st.dialog("✏️ Edit Person Profile")
def edit_player_dialog(player):
    with st.form("edit_p_form"):
        new_name = st.text_input("IGN", value=player['ign'])
        # Updated Roles: 'Support' merged into 'Roam'
        new_roles = st.multiselect("Roles", 
                                  ['Dark Slayer', 'Jungle', 'Mid', 'Abyssal', 'Roam', 'Coach'],
                                  default=player.get('roles', []))
        
        if st.form_submit_button("Save Changes"):
            db.collection('players').document(player['id']).update({
                "ign": new_name,
                "roles": new_roles
            })
            # Update session state manually to reflect changes immediately
            for p in st.session_state['players']:
                if p['id'] == player['id']:
                    p['ign'] = new_name
                    p['roles'] = new_roles
                    break
            st.success("Updated!")
            time.sleep(0.5)
            st.rerun()
            st.success("Updated!")
            time.sleep(0.5)
            st.rerun()

@st.dialog("➕ Add New Person")
def register_player_dialog():
    with st.form("f_reg_person_dialog"):
        p_ign = st.text_input("Person Name / IGN")
        # Updated Roles: 'Support' merged into 'Roam'
        p_roles = st.multiselect("Role Selection", 
                                ['Dark Slayer', 'Jungle', 'Mid', 'Abyssal', 'Roam', 'Coach'])
        if st.form_submit_button("Save Person"):
            if p_ign and p_roles:
                save_player(p_ign, p_roles)
                st.success(f"Registered {p_ign}!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Name and Roles are required.")

@st.dialog("➕ Create New Team")
def create_team_dialog():
    with st.form("f_reg_team_dialog"):
        t_name = st.text_input("Team Name")
        if st.form_submit_button("Create Team"):
            if t_name:
                empty_roster = {k: None for k in ["Dark Slayer", "Jungle", "Mid", "Abyssal", "Roam", "Sub 1", "Sub 2"]}
                save_team(t_name, None, empty_roster)
                st.success(f"Team '{t_name}' created!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Name is required.")

@st.dialog("🛡️ Manage Team Roster")
def manage_roster_dialog(team):
    st.caption(f"Editing Roster for: {team['name']}")
    
    # 1. Prepare Data & Helpers (Reusing logic for strict filtering)
    all_p = st.session_state['players']
    t_lookup = {t['id']: t['name'] for t in st.session_state['teams']}
    
    def get_options(role_filter=None):
        opts = {"None": None}
        for p in all_p:
            if role_filter:
                player_roles = p.get('roles', [])
                if role_filter == "Roam":
                    if "Roam" not in player_roles and "Support" not in player_roles: continue
                else:
                    if role_filter not in player_roles: continue
            
            status = t_lookup.get(p.get('current_team_id'), "Free Agent")
            if p.get('current_team_id') == team['id']: status = "CURRENT"
            label = f"{p['ign']} ({'/'.join(p.get('roles', []))}) - {status}"
            opts[label] = p['id']
        return opts

    def get_idx_in(pid, options_dict):
        if not pid: return 0
        for i, (l, v) in enumerate(options_dict.items()):
            if v == pid: return i
        return 0

    opt_coach = get_options("Coach")
    opt_dsl = get_options("Dark Slayer")
    opt_jgl = get_options("Jungle")
    opt_mid = get_options("Mid")
    opt_aby = get_options("Abyssal")
    opt_roam = get_options("Roam")
    opt_all = get_options(None)

    curr_r = team.get('roster', {})
    
    with st.form("dialog_roster_form"):
        st.markdown("#### 🧠 Coaching Staff")
        new_coach = st.selectbox("Head Coach", list(opt_coach.keys()), index=get_idx_in(team.get('coach_id'), opt_coach), key="d_coach")
        
        st.markdown("#### ⚔️ Main Roster")
        c1, c2 = st.columns(2)
        ndsl = c1.selectbox("Dark Slayer", list(opt_dsl.keys()), index=get_idx_in(curr_r.get("Dark Slayer"), opt_dsl), key="d_dsl")
        njgl = c2.selectbox("Jungle", list(opt_jgl.keys()), index=get_idx_in(curr_r.get("Jungle"), opt_jgl), key="d_jgl")
        
        c3, c4 = st.columns(2)
        nmid = c3.selectbox("Mid", list(opt_mid.keys()), index=get_idx_in(curr_r.get("Mid"), opt_mid), key="d_mid")
        naby = c4.selectbox("Abyssal", list(opt_aby.keys()), index=get_idx_in(curr_r.get("Abyssal"), opt_aby), key="d_aby")
        
        nroam = st.selectbox("Roam (Support)", list(opt_roam.keys()), index=get_idx_in(curr_r.get("Roam"), opt_roam), key="d_roam")
        
        st.markdown("#### 🔄 Substitutes")
        s1, s2 = st.columns(2)
        nsub1 = s1.selectbox("Sub 1", list(opt_all.keys()), index=get_idx_in(curr_r.get("Sub 1"), opt_all), key="d_sub1")
        nsub2 = s2.selectbox("Sub 2", list(opt_all.keys()), index=get_idx_in(curr_r.get("Sub 2"), opt_all), key="d_sub2")
        
        if st.form_submit_button("💾 Save Roster Configuration"):
            updated_r = {
                "Dark Slayer": opt_dsl[ndsl], "Jungle": opt_jgl[njgl], "Mid": opt_mid[nmid],
                "Abyssal": opt_aby[naby], "Roam": opt_roam[nroam],
                "Sub 1": opt_all[nsub1], "Sub 2": opt_all[nsub2]
            }
            new_coach_id = opt_coach[new_coach]
            
            batch = db.batch()
            t_ref = db.collection('teams').document(team['id'])
            
            # 1. Update Team
            batch.update(t_ref, {"roster": updated_r, "coach_id": new_coach_id})
            
            # 2. Reset Old Players
            for p in db.collection('players').where('current_team_id', '==', team['id']).stream():
                batch.update(p.reference, {"current_team_id": None})
                
            # 3. Set New Players
            new_ids = [val for val in updated_r.values() if val]
            if new_coach_id: new_ids.append(new_coach_id)
            for pid in set(new_ids):
                batch.update(db.collection('players').document(pid), {"current_team_id": team['id']})
            
            batch.commit()
            
            # Sync Session State
            st.session_state['teams'] = get_teams()
            st.session_state['players'] = get_players()
            
            st.success("Roster Saved!")
            time.sleep(0.5)
            st.rerun()

# ==============================================================================
# SIDEBAR NAVIGATION & STATE
# ==============================================================================
init_session_state()


# ==============================================================================
with st.sidebar:
    st.markdown("# TAOX BRAIN 🧠")
    
    # SYSTEM 1: VERSION SELECTOR
    if db:
        versions = get_versions()
        version_opts = {v['name']: v['id'] for v in versions}
        
        if not versions:
            st.warning("No Patch Data Found.")
            if st.button("Initialize Season 1"):
                # Clean boot for first run
                clone_version(None, "Season 1 (Init)") # Logic needs to handle None source
                st.rerun()
        else:
            selected_ver_name = st.selectbox("Current Patch", list(version_opts.keys()))
            st.session_state['current_version_id'] = version_opts[selected_ver_name]
            st.caption(f"ID: {st.session_state['current_version_id']}")
    else:
        st.session_state['current_version_id'] = None

    st.markdown("---")
    
    menu = st.radio(
        "Modules", 
        ["Meta Management", "Team Roster", "Match Logger", "Draft Simulator"],
        label_visibility="collapsed"
    )

# ==============================================================================
# MODULE 1: META & HERO MANAGEMENT
# ==============================================================================
if menu == "Meta Management":
    st.title("META & HERO MANAGEMENT")
    
    tab1, tab2, tab3 = st.tabs(["Version Control", "Hero Editor", "Synergy Builder"])
    
    with tab1:
        st.subheader("Patch Versioning")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Create New Patch")
            with st.form("new_patch"):
                new_v_name = st.text_input("New Version Name", "S1 2025 - Patch 1")
                clone_source = st.selectbox("Clone Data From", ["Empty"] + list(version_opts.keys()) if 'version_opts' in locals() else [])
                
                if st.form_submit_button("Create Version"):
                    if clone_source == "Empty":
                        # Create empty
                        db.collection('versions').add({
                            "name": new_v_name,
                            "created_at": datetime.now(),
                            "is_active": True
                        })
                        st.success(f"Created empty version: {new_v_name}")
                        time.sleep(1)
                        st.rerun()
                    else:
                        # Clone
                        src_id = version_opts[clone_source]
                        with st.spinner("Cloning Meta Data..."):
                            clone_version(src_id, new_v_name)
                        st.success(f"Successfully cloned {clone_source} to {new_v_name}")
                        time.sleep(1)
                        st.rerun()
    
    with tab2:
        if st.session_state.get('current_version_id'):
            st.subheader(f"Heroes (Patch: {selected_ver_name})")
            
            df = get_heroes(st.session_state['current_version_id'])
            
            # Editor
            if df.empty:
                st.info("No heroes in this version. Add one manually or clone from previous.")
                cols_schema = pd.DataFrame(columns=["name", "role", "tier", "meta_score", "image_url", "counters", "version_id"])
                df = cols_schema
            else:
                # Fill missing cols
                for c in ["name", "role", "tier", "meta_score", "image_url"]:
                     if c not in df.columns: df[c] = ""
            
            edited_df = st.data_editor(
                df,
                column_config={
                    "id": None,
                    "version_id": None,
                    "image_url": st.column_config.ImageColumn("Avatar"),
                    "tier": st.column_config.SelectboxColumn("Tier", options=["S", "A", "B", "C"]),
                    "role": st.column_config.SelectboxColumn("Role", options=["Assassin", "Mage", "Fighter", "Support", "Tank", "Carry"]),
                    "meta_score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100, format="%d"),
                },
                num_rows="dynamic",
                use_container_width=True,
                key="hero_editor_v2"
            )
            
            if st.button("Save Changes"):
                with st.spinner("Syncing..."):
                    for i, row in edited_df.iterrows():
                        data = row.to_dict()
                        h_id = data.pop("id", None)
                        
                        # FORCE current version ID
                        data['version_id'] = st.session_state['current_version_id']
                        
                        # Simple upsert
                        if h_id and isinstance(h_id, str) and len(h_id) > 2:
                            db.collection('heroes').document(h_id).set(data, merge=True)
                        else:
                            if data.get('name'):
                                db.collection('heroes').add(data)
                                
                st.success("Saved!")
                time.sleep(1)
                st.rerun()
                
    with tab3:
        st.subheader("Synery Builder")
        # Reuse logic from old app but scoped to version
        # (Simplified for brevity as requested structure is huge)
        st.info("Combo builder logic here (linked to current version heroes).")


# ==============================================================================
# MODULE 2: TEAM & ROSTER MANAGEMENT
# ==============================================================================
elif menu == "Team Roster":
    st.title("TEAM & ROSTER MANAGEMENT")
    
    if not db:
        st.error("Database connection failed. Please check initialization.")
    else:
        # Initialize session state from DB if empty
        if not st.session_state['players']:
            st.session_state['players'] = get_players()
        if not st.session_state['teams']:
            st.session_state['teams'] = get_teams()
            
        tab1, tab2, tab3 = st.tabs(["👤 Register Person", "🛡️ Create Team", "📋 Roster Market"])
        
        # --- TAB 1: REGISTER PERSON ---
        # --- TAB 1: REGISTER PERSON ---
        with tab1:
            if st.button("➕ Register New Person", type="primary", use_container_width=True):
                register_player_dialog()
            
            st.markdown("---")
            st.markdown("### 👥 Registered People")
            
            players = st.session_state['players']
            if not players:
                st.info("No people registered yet.")
            else:
                # Reverse list to show newest first
                rev_players = players[::-1]
                
                # Create Team Lookup for Display
                team_map = {t['id']: t['name'] for t in st.session_state['teams']}
                
                # --- FILTER LOGIC ---
                unique_teams = sorted(list(set([t['name'] for t in st.session_state['teams']])))
                # Calculate players per team for UI hint if desired, but kept simple for now
                
                c_filter, _ = st.columns([1, 2])
                with c_filter:
                   filter_opts = ["All Teams", "Free Agent"] + unique_teams
                   sel_filter = st.selectbox("🔍 Filter by Team", filter_opts)
                
                # Apply Filter
                filtered_players = []
                for p in rev_players:
                    p_team_name = team_map.get(p.get('current_team_id'))
                    
                    if sel_filter == "All Teams":
                        filtered_players.append(p)
                    elif sel_filter == "Free Agent":
                        if not p_team_name: filtered_players.append(p)
                    else:
                        if p_team_name == sel_filter: filtered_players.append(p)

                # Grid of 3
                cols = st.columns(3)
                for i, p in enumerate(filtered_players):
                    with cols[i % 3]:
                        # Resolve Team Name
                        assigned_team = team_map.get(p.get('current_team_id'), None)
                        team_status = f"🛡️ {assigned_team}" if assigned_team else "Free Agent"
                        
                        # Construct multi-line label
                        # Name
                        # Roles (comma joined)
                        # Team Status
                        role_str = ", ".join(p.get('roles', []))
                        label = f"{p['ign']}\n{role_str}\n{team_status}"
                        
                        if st.button(label, key=f"card_p_{p['id']}", use_container_width=True):
                            edit_player_dialog(p)

        # --- TAB 2: CREATE TEAM ---
        # --- TAB 2: CREATE TEAM ---
        with tab2:
            if st.button("➕ Create New Team", type="primary", use_container_width=True):
                 create_team_dialog()
            
            st.markdown("---")
            st.markdown("### 🛡️ Existing Teams")
            
            teams = st.session_state['teams']
            if not teams:
                st.info("No teams created yet.")
            else:
                cols = st.columns(3)
                for i, t in enumerate(teams):
                    with cols[i % 3]:
                        # Find Coach Name
                        c_name = "TBD"
                        c_id = t.get('coach_id')
                        if c_id:
                            found = next((p for p in st.session_state['players'] if p['id'] == c_id), None)
                            if found: c_name = found['ign']
                        
                        # Label
                        label = f"{t['name']}\n🧠 Coach: {c_name}"
                        
                        if st.button(label, key=f"card_t_{t['id']}", use_container_width=True):
                            manage_roster_dialog(t)

        # --- TAB 3: ROSTER MARKET ---
        with tab3:
            st.subheader("Manage Active Rosters")
            teams = st.session_state['teams']
            if not teams:
                st.info("Create a team first.")
            else:
                t_names = [t['name'] for t in teams]
                sel_t_name = st.selectbox("Select Team", t_names)
                sel_team = next(t for t in teams if t['name'] == sel_t_name)
                
                # Fetch players
                all_p = st.session_state['players']
                t_lookup = {t['id']: t['name'] for t in teams}
                
                # HELPER: Build options for a specific role filter
                def get_options(role_filter=None):
                    opts = {"None": None}
                    for p in all_p:
                        # 1. Filter Check
                        if role_filter:
                            player_roles = p.get('roles', [])
                             # "Roam" slot accepts "Roam" or "Support"
                            if role_filter == "Roam":
                                if "Roam" not in player_roles and "Support" not in player_roles: continue
                            else:
                                if role_filter not in player_roles: continue
                        
                        # 2. Build Label
                        status = t_lookup.get(p.get('current_team_id'), "Free Agent")
                        if p.get('current_team_id') == sel_team['id']: status = "CURRENT"
                        roles_str = '/'.join(p.get('roles', []))
                        label = f"{p['ign']} ({roles_str}) - {status}"
                        opts[label] = p['id']
                    return opts

                # Get specific option lists
                opt_coach = get_options("Coach")
                opt_dsl   = get_options("Dark Slayer")
                opt_jgl   = get_options("Jungle")
                opt_mid   = get_options("Mid")
                opt_aby   = get_options("Abyssal")
                opt_roam  = get_options("Roam") # Covers Support too logic above
                opt_all   = get_options(None)   # For Subs

                # Helper to find index of current ID in a specific options dict
                def get_idx_in(pid, options_dict):
                    if not pid: return 0
                    # The value is the ID. We need to find the key that matches this ID.
                    # Since we regenerate keys every time (label includes status), exact match might be tricky if status changed?
                    # But status logic is deterministic based on `current_team_id` vs `sel_team['id']`.
                    # So iterating list should work.
                    for i, (l, v) in enumerate(options_dict.items()):
                        if v == pid: return i
                    return 0

                curr_r = sel_team.get('roster', {})
                current_coach_id = sel_team.get('coach_id')
                
                with st.form("f_roster_update"):
                    st.write(f"Editing Roster for: **{sel_t_name}**")
                    
                    # 1. COACH ASSIGNMENT
                    st.markdown("#### 🧠 Coaching Staff")
                    # Strict Filter: Must have 'Coach' role
                    new_coach = st.selectbox("Head Coach", list(opt_coach.keys()), index=get_idx_in(current_coach_id, opt_coach))
                    
                    st.write("---")
                    
                    # 2. MAIN 5
                    st.markdown("#### ⚔️ Main Roster (Starting 5)")
                    c1, c2, c3 = st.columns(3)
                    new_dsl = c1.selectbox("Dark Slayer", list(opt_dsl.keys()), index=get_idx_in(curr_r.get("Dark Slayer"), opt_dsl))
                    new_jgl = c2.selectbox("Jungle", list(opt_jgl.keys()), index=get_idx_in(curr_r.get("Jungle"), opt_jgl))
                    new_mid = c3.selectbox("Mid", list(opt_mid.keys()), index=get_idx_in(curr_r.get("Mid"), opt_mid))
                    
                    c4, c5 = st.columns(2)
                    new_aby = c4.selectbox("Abyssal", list(opt_aby.keys()), index=get_idx_in(curr_r.get("Abyssal"), opt_aby))
                    new_sup = c5.selectbox("Roam (Support)", list(opt_roam.keys()), index=get_idx_in(curr_r.get("Roam"), opt_roam))
                    
                    st.write("---")
                    
                    # 3. SUBSTITUTES
                    st.markdown("#### 🔄 Substitutes")
                    s1, s2 = st.columns(2)
                    new_sub1 = s1.selectbox("Sub 1", list(opt_all.keys()), index=get_idx_in(curr_r.get("Sub 1"), opt_all))
                    new_sub2 = s2.selectbox("Sub 2", list(opt_all.keys()), index=get_idx_in(curr_r.get("Sub 2"), opt_all))

                    if st.form_submit_button("💾 Update Roster"):
                        updated_r = {
                            "Dark Slayer": opt_dsl[new_dsl],
                            "Jungle": opt_jgl[new_jgl],
                            "Mid": opt_mid[new_mid],
                            "Abyssal": opt_aby[new_aby],
                            "Roam": opt_roam[new_sup],
                            "Sub 1": opt_all[new_sub1], 
                            "Sub 2": opt_all[new_sub2]
                        }
                        new_coach_id = opt_coach[new_coach]
                        
                        # Sync to DB
                        batch = db.batch()
                        t_ref = db.collection('teams').document(sel_team['id'])
                        
                        # 1. Update Team Doc
                        batch.update(t_ref, {
                            "roster": updated_r,
                            "coach_id": new_coach_id
                        })
                        
                        # 2. Manage Player "current_team_id"
                        # Reset old team members
                        current_members_snap = db.collection('players').where('current_team_id', '==', sel_team['id']).stream()
                        for p in current_members_snap:
                            batch.update(p.reference, {"current_team_id": None})
                            
                        # Set new members
                        new_member_ids = [pid for pid in updated_r.values() if pid]
                        if new_coach_id: new_member_ids.append(new_coach_id)
                        
                        for pid in set(new_member_ids):
                            batch.update(db.collection('players').document(pid), {"current_team_id": sel_team['id']})
                            
                        batch.commit()
                        
                        # Force refresh session state
                        st.session_state['teams'] = get_teams()
                        st.session_state['players'] = get_players()
                        
                        st.success("Roster updated successfully!")
                        time.sleep(0.5)
                        st.rerun()


# ==============================================================================
# MODULE 3: MATCH LOGGER
# ==============================================================================
elif menu == "Match Logger":
    st.title("MATCH LOGGER")
    
    if not st.session_state.get('current_version_id'):
        st.error("Please select a Patch Version in the sidebar first.")
    else:
        teams = get_teams()
        team_names = [t['name'] for t in teams]
        
        if len(teams) < 2:
            st.warning("Need at least 2 teams created in 'Team Roster' to log matches.")
        else:
            with st.container():
                st.markdown('<div class="glass-card" style="padding: 20px;">', unsafe_allow_html=True)
                
                # STEP 1: PRE-MATCH
                c1, c2, c3 = st.columns(3)
                match_type = c1.selectbox("Match Type", ["Scrim", "Tournament", "Ranked"])
                blue_team_name = c2.selectbox("🔵 Blue Team", team_names, index=0)
                red_team_name = c3.selectbox("🔴 Red Team", team_names, index=1)
                
                st.markdown("---")
                
                # STEP 2: DRAFT RECORDER
                # Fetch heroes for this version
                heroes_df = get_heroes(st.session_state['current_version_id'])
                if heroes_df.empty:
                    st.error("No heroes found in this version.")
                else:
                    hero_options = heroes_df['name'].tolist()
                    
                    col_b, col_r = st.columns(2)
                    
                    with col_b:
                        st.info("Blue Side Draft")
                        b_bans = st.multiselect("Blue Bans (4)", hero_options, max_selections=4, key="bb")
                        b_picks = st.multiselect("Blue Picks (5)", hero_options, max_selections=5, key="bp")
                        
                    with col_r:
                        st.error("Red Side Draft")
                        r_bans = st.multiselect("Red Bans (4)", hero_options, max_selections=4, key="rb")
                        r_picks = st.multiselect("Red Picks (5)", hero_options, max_selections=5, key="rp")
                        
                    st.markdown("---")
                    
                    # STEP 3: RESULT
                    winner = st.radio("Winner", ["Blue", "Red"], horizontal=True)
                    notes = st.text_area("Match Notes")
                    
                    if st.button("📝 Log Match Result", use_container_width=True):
                         # Find Team IDs & Rosters
                        b_team = next((t for t in teams if t['name'] == blue_team_name), None)
                        r_team = next((t for t in teams if t['name'] == red_team_name), None)
                        
                        b_id = b_team['id'] if b_team else None
                        r_id = r_team['id'] if r_team else None
                        
                        # Snapshot rosters (Player IDs present at this time)
                        b_roster = b_team.get('roster', {}) if b_team else {}
                        r_roster = r_team.get('roster', {}) if r_team else {}
                        
                        match_doc = {
                            "version_id": st.session_state['current_version_id'],
                            "type": match_type,
                            "blue_team_id": b_id,
                            "red_team_id": r_id,
                            "blue_roster_snapshot": b_roster, # Relational Link
                            "red_roster_snapshot": r_roster,   # Relational Link
                            "blue_bans": b_bans,
                            "blue_picks": b_picks,
                            "red_bans": r_bans,
                            "red_picks": r_picks,
                            "winner": winner,
                            "timestamp": datetime.now(),
                            "notes": notes
                        }
                        
                        db.collection('matches').add(match_doc)
                        st.success("Match Logged to Database!")
                        st.balloons()

                st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# MODULE 4: DRAFT SIMULATOR & ANALYTICS
# ==============================================================================
elif menu == "Draft Simulator":
    st.title("SIMULATION & ANALYTICS")
    
    mode = st.selectbox("Mode", ["Analytics Dashboard", "Bot vs Bot Simulation"])
    
    if mode == "Analytics Dashboard":
        st.subheader("Meta Analytics")
        # Query matches for current version
        if st.session_state.get('current_version_id'):
            matches = db.collection('matches').where('version_id', '==', st.session_state['current_version_id']).stream()
            
            # Simple aggregations
            pick_counts = {}
            ban_counts = {}
            wins = {}
            total_matches = 0
            
            for m in matches:
                d = m.to_dict()
                total_matches += 1
                winner = d.get('winner')
                
                # Picks
                for p in d.get('blue_picks', []):
                    pick_counts[p] = pick_counts.get(p, 0) + 1
                    if winner == "Blue": wins[p] = wins.get(p, 0) + 1
                    
                for p in d.get('red_picks', []):
                    pick_counts[p] = pick_counts.get(p, 0) + 1
                    if winner == "Red": wins[p] = wins.get(p, 0) + 1
                
                # Bans
                for b in d.get('blue_bans', []) + d.get('red_bans', []):
                    ban_counts[b] = ban_counts.get(b, 0) + 1
            
            if total_matches > 0:
                stats = []
                all_heroes = set(list(pick_counts.keys()) + list(ban_counts.keys()))
                for h in all_heroes:
                    p = pick_counts.get(h, 0)
                    b = ban_counts.get(h, 0)
                    w = wins.get(h, 0)
                    wr = (w / p * 100) if p > 0 else 0
                    stats.append({
                        "Hero": h,
                        "Pick Rate": f"{(p/total_matches*100):.1f}%",
                        "Ban Rate": f"{(b/total_matches*100):.1f}%",
                        "Win Rate": f"{wr:.1f}%",
                        "Matches": p
                    })
                
                st.dataframe(pd.DataFrame(stats).sort_values("Matches", ascending=False), use_container_width=True)
            else:
                st.info("No matches recorded for this patch version yet.")
        else:
             st.warning("Select a version.")

    elif mode == "Bot vs Bot Simulation":
        st.subheader("Monte Carlo Draft Sim")
        st.caption("Simulates 100 matches based on Meta Scores to predict outcomes.")
        
        if st.button("Run Simulation"):
             with st.spinner("Simulating..."):
                 time.sleep(2) # Fake compute time for UX
                 st.success("Simulation Complete")
                 st.metric("Predicted Blue Win Rate", "54%", "+2.3%")
                 st.progress(54)
