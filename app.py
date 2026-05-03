import streamlit as st
import pickle
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import sqlite3

# =====================================================
# PAGE CONFIG - DARK THEME
# =====================================================
st.set_page_config(
    page_title="Movie Recommender",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Dark Theme with FULL WHITE TEXT VISIBILITY
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #ff6b6b;
        border: none;
    }
    .stSelectbox, .stTextInput {
        color: white;
    }
    h1, h2, h3 {
        color: #ffffff;
    }
    .trailer-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        text-align: center;
    }
    .trailer-link {
        color: white;
        text-decoration: none;
        font-size: 18px;
        font-weight: bold;
    }
    .metric-card {
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #ff4b4b;
    }
    
    /* Fix all input and select labels to be white */
    .stTextInput > label,
    .stSelectbox > label,
    .stNumberInput > label,
    label {
        color: #ffffff !important;
    }
    
    /* Fix markdown text to be white */
    .stMarkdown, .stMarkdown p, .stMarkdown span {
        color: #ffffff !important;
    }
    
    /* Dropdown menu fix - black text on white background - HIGHER PRIORITY */
    div[data-baseweb="popover"] {
        background-color: #ffffff !important;
    }
    
    ul[role="listbox"] {
        background-color: #ffffff !important;
    }
    
    ul[role="listbox"] li,
    ul[role="listbox"] li span,
    ul[role="listbox"] li div {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    
    ul[role="listbox"] li:hover {
        background-color: #f0f0f0 !important;
    }
    
    ul[role="listbox"] li:hover span,
    ul[role="listbox"] li:hover div {
        color: #000000 !important;
    }
    
    div[role="option"],
    div[role="option"] span,
    div[role="option"] div {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)


# =====================================================
# DATABASE
# =====================================================
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

# Users table
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT,
    login_method TEXT DEFAULT 'email'
)
""")

# User history table
c.execute("""
CREATE TABLE IF NOT EXISTS user_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    movie_id INTEGER,
    movie_title TEXT,
    action_type TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# User liked movies table
c.execute("""
CREATE TABLE IF NOT EXISTS user_liked_movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    movie_id INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(username, movie_id)
)
""")

# User watch later table
c.execute("""
CREATE TABLE IF NOT EXISTS user_watch_later (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    movie_id INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(username, movie_id)
)
""")

conn.commit()



def add_user(username, password, login_method='email'):
    try:
        c.execute("INSERT INTO users VALUES (?, ?, ?)", (username, password, login_method))
        conn.commit()
        return True
    except:
        return False


def login_user(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    return c.fetchone()


def add_to_history(username, movie_id, movie_title, action_type):
    """Add user activity to history"""
    c.execute(
        "INSERT INTO user_history (username, movie_id, movie_title, action_type) VALUES (?, ?, ?, ?)",
        (username, movie_id, movie_title, action_type)
    )
    conn.commit()


def get_user_history(username):
    """Get user viewing history"""
    c.execute(
        "SELECT movie_title, action_type, timestamp FROM user_history WHERE username=? ORDER BY timestamp DESC LIMIT 50",
        (username,)
    )
    return c.fetchall()


def get_most_viewed(username):
    """Get most viewed movies by user"""
    c.execute("""
        SELECT movie_title, COUNT(*) as view_count
        FROM user_history
        WHERE username=? AND action_type='viewed'
        GROUP BY movie_title
        ORDER BY view_count DESC
        LIMIT 10
    """, (username,))
    return c.fetchall()


# =====================================================
# NEW DATABASE FUNCTIONS FOR LIKED MOVIES AND WATCH LATER
# =====================================================

def add_liked_movie(username, movie_id):
    """Add a movie to user's liked movies"""
    try:
        c.execute(
            "INSERT INTO user_liked_movies (username, movie_id) VALUES (?, ?)",
            (username, int(movie_id))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def remove_liked_movie(username, movie_id):
    """Remove a movie from user's liked movies"""
    c.execute(
        "DELETE FROM user_liked_movies WHERE username=? AND movie_id=?",
        (username, int(movie_id))
    )
    conn.commit()


def get_liked_movies(username):
    """Get all liked movies for a user"""
    c.execute(
        "SELECT movie_id FROM user_liked_movies WHERE username=? ORDER BY timestamp DESC",
        (username,)
    )
    return [int(row[0]) for row in c.fetchall()]

def add_watch_later(username, movie_id):
    """Add a movie to user's watch later list"""
    try:
        c.execute(
            "INSERT INTO user_watch_later (username, movie_id) VALUES (?, ?)",
            (username, int(movie_id))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def remove_watch_later(username, movie_id):
    """Remove a movie from user's watch later list"""
    c.execute(
        "DELETE FROM user_watch_later WHERE username=? AND movie_id=?",
        (username, int(movie_id))
    )
    conn.commit()


def get_watch_later_movies(username):
    """Get all watch later movies for a user"""
    c.execute(
        "SELECT movie_id FROM user_watch_later WHERE username=? ORDER BY timestamp DESC",
        (username,)
    )
    return [int(row[0]) for row in c.fetchall()]

# =====================================================
# SESSION STATE
# =====================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = None

if "page" not in st.session_state:
    st.session_state.page = "login"

if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None

if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

if "liked_movies" not in st.session_state:
    st.session_state.liked_movies = []

if "watch_later" not in st.session_state:
    st.session_state.watch_later = []


# =====================================================
# HELPER FUNCTION TO LOAD USER DATA
# =====================================================
def load_user_data(username):
    """Load user's liked movies and watch later list from database"""
    st.session_state.liked_movies = get_liked_movies(username)
    st.session_state.watch_later = get_watch_later_movies(username)

# =====================================================
# LOGOUT FUNCTION - CLEARS ALL USER DATA
# =====================================================
def logout_user():
    """Clear all user-specific session state data"""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.liked_movies = []
    st.session_state.watch_later = []
    st.session_state.selected_movie = None
    st.session_state.current_page = "home"
    st.session_state.page = "login"
    # Clear recommendations if they exist
    if "recommendations" in st.session_state:
        del st.session_state.recommendations

# =====================================================
# LOGIN PAGE
# =====================================================
def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("<h1 style='text-align: center; color: #ffffff;'>🎬 Movie Recommender</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #ffffff;'>🔐 Login</h3>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        col_a, col_b = st.columns(2)

        with col_a:
            if st.button("Login", use_container_width=True):
                if login_user(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.current_page = "home"
                    # Load user's liked movies and watch later list
                    load_user_data(username)
                    st.rerun()
                else:
                    st.error("Invalid credentials")

        with col_b:
            if st.button("Create Account", use_container_width=True):
                st.session_state.page = "register"
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #ffffff;'>───────── OR ─────────</p>", unsafe_allow_html=True)

        # Google Login Button (Mock Implementation)
        if st.button("🔍 Continue with Google", use_container_width=True):
            # Mock Google login - in production, you'd use OAuth
            google_user = f"google_user_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            add_user(google_user, "google_auth", "google")
            st.session_state.logged_in = True
            st.session_state.username = google_user
            st.session_state.current_page = "home"
            # Load user's liked movies and watch later list
            load_user_data(google_user)
            st.success(f"Logged in as {google_user}")
            st.rerun()


# =====================================================
# REGISTER PAGE
# =====================================================
def register_page():
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("<h1 style='text-align: center; color: #ffffff;'>📝 Register</h1>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")

        if st.button("Register", use_container_width=True):
            if new_user and new_pass:
                if add_user(new_user, new_pass, 'email'):
                    st.success("Account created 🎉")
                    st.session_state.page = "login"
                    st.rerun()
                else:
                    st.error("User already exists")
            else:
                st.error("Fill all fields")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #ffffff;'>───────── OR ─────────</p>", unsafe_allow_html=True)

        # Google Register Button (Mock Implementation)
        if st.button("🔍 Continue with Google", use_container_width=True):
            google_user = f"google_user_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            add_user(google_user, "google_auth", "google")
            st.session_state.logged_in = True
            st.session_state.username = google_user
            st.session_state.current_page = "home"
            # Load user's liked movies and watch later list
            load_user_data(google_user)
            st.success(f"Account created and logged in as {google_user}")
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Back to Login", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()


# =====================================================
# MOVIE FUNCTIONS - WITH TIMEOUT AND ERROR HANDLING
# =====================================================
def fetch_poster(movie_id):
    """Fetch movie poster with timeout and error handling"""
    try:
        response = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=14d6a0e29ade62d256a2644a73925035&language=en-US",
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        if data.get('poster_path'):
            return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
        else:
            return "https://via.placeholder.com/500x750?text=No+Poster+Available"
    except requests.exceptions.Timeout:
        return "https://via.placeholder.com/500x750/1e1e1e/ffffff?text=Connection+Timeout"
    except requests.exceptions.RequestException:
        return "https://via.placeholder.com/500x750/1e1e1e/ffffff?text=Error+Loading"
    except Exception:
        return "https://via.placeholder.com/500x750/1e1e1e/ffffff?text=Error"


def fetch_movie_details(movie_id):
    """Fetch movie details with timeout and error handling"""
    try:
        response = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=14d6a0e29ade62d256a2644a73925035&language=en-US",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except:
        return {
            'title': 'Error Loading',
            'overview': 'Connection issue. Check your internet.',
            'poster_path': None,
            'vote_average': 0,
            'release_date': '',
            'runtime': 0,
            'genres': [],
            'original_language': 'N/A',
            'budget': 0,
            'revenue': 0
        }


def fetch_cast_crew(movie_id):
    """Fetch cast and crew information with timeout and error handling"""
    try:
        response = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key=14d6a0e29ade62d256a2644a73925035&language=en-US",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except:
        return {'cast': [], 'crew': []}


def fetch_trailer(movie_id):
    """Fetch movie trailer from YouTube with timeout and error handling"""
    try:
        response = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key=14d6a0e29ade62d256a2644a73925035&language=en-US",
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        # Find YouTube trailer
        for video in data.get('results', []):
            if video['type'] == 'Trailer' and video['site'] == 'YouTube':
                return f"https://www.youtube.com/watch?v={video['key']}"

        return None
    except:
        return None


def recommend(movie):
    """Generate movie recommendations"""
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

        recommended_movies = []
        recommended_posters = []

        for i in movies_list:
            movie_id = movies.iloc[i[0]].movie_id
            recommended_movies.append(movies.iloc[i[0]].title)

            # Fetch poster with error handling
            poster = fetch_poster(movie_id)
            recommended_posters.append(poster)

        return recommended_movies, recommended_posters
    except Exception as e:
        st.error(f"Error generating recommendations: {str(e)}")
        return [], []


# =====================================================
# LOAD DATA
# =====================================================
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))


# =====================================================
# ROUTING
# =====================================================
if not st.session_state.logged_in:
    if st.session_state.page == "login":
        login_page()
    else:
        register_page()
    st.stop()


# =====================================================
# SIDEBAR NAVIGATION
# =====================================================
st.sidebar.title("📂 Navigation")

if st.sidebar.button("🏠 Home", use_container_width=True):
    st.session_state.current_page = "home"
    st.session_state.selected_movie = None
    st.rerun()

if st.sidebar.button("📊 Dashboard", use_container_width=True):
    st.session_state.current_page = "dashboard"
    st.session_state.selected_movie = None
    st.rerun()


if st.sidebar.button(f"❤️ Liked Movies ({len(st.session_state.liked_movies)})", use_container_width=True):
    st.session_state.current_page = "liked"
    st.session_state.selected_movie = None
    st.rerun()

if st.sidebar.button(f"⏰ Watch Later ({len(st.session_state.watch_later)})", use_container_width=True):
    st.session_state.current_page = "watch_later"
    st.session_state.selected_movie = None
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.write(f"👤 **User:** {st.session_state.username}")
if st.sidebar.button("🚪 Logout", use_container_width=True):
    logout_user()
    st.rerun()


# =====================================================
# MOVIE DETAIL VIEW WITH TRAILER
# =====================================================
def show_movie_details(movie_id):
    movie = fetch_movie_details(movie_id)
    credits = fetch_cast_crew(movie_id)
    trailer_url = fetch_trailer(movie_id)

    # Add to user history
    add_to_history(st.session_state.username, movie_id, movie['title'], 'viewed')

    st.markdown("---")
    st.markdown(f"<h1 style='color: #ffffff;'>🎬 {movie['title']}</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        if movie.get('poster_path'):
            st.image("https://image.tmdb.org/t/p/w500/" + movie['poster_path'])
        else:
            st.image("https://via.placeholder.com/500x750?text=No+Poster")

        # Trailer Section
        if trailer_url:
            st.markdown(f"""
            <div class="trailer-container">
                <a href="{trailer_url}" target="_blank" class="trailer-link">
                    ▶️ Watch Trailer on YouTube
                </a>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No trailer available")

        # Like and Watch Later buttons
        st.markdown("<h3 style='color: #ffffff;'>Quick Actions</h3>", unsafe_allow_html=True)

        like_col, watch_col = st.columns(2)

        with like_col:
            if movie_id in st.session_state.liked_movies:
                if st.button("💔 Unlike", use_container_width=True):
                    st.session_state.liked_movies.remove(movie_id)
                    remove_liked_movie(st.session_state.username, movie_id)
                    add_to_history(st.session_state.username, movie_id, movie['title'], 'unliked')
                    st.rerun()
            else:
                if st.button("❤️ Like", use_container_width=True):
                    if movie_id not in st.session_state.liked_movies:
                        st.session_state.liked_movies.append(movie_id)
                        add_liked_movie(st.session_state.username, movie_id)
                        add_to_history(st.session_state.username, movie_id, movie['title'], 'liked')
                        st.success("Added to Liked!")
                        st.rerun()

        with watch_col:
            if movie_id in st.session_state.watch_later:
                if st.button("✅ Remove", use_container_width=True):
                    st.session_state.watch_later.remove(movie_id)
                    remove_watch_later(st.session_state.username, movie_id)
                    add_to_history(st.session_state.username, movie_id, movie['title'], 'removed_watchlist')
                    st.rerun()
            else:
                if st.button("⏰ Watch Later", use_container_width=True):
                    if movie_id not in st.session_state.watch_later:
                        st.session_state.watch_later.append(movie_id)
                        add_watch_later(st.session_state.username, movie_id)
                        add_to_history(st.session_state.username, movie_id, movie['title'], 'added_watchlist')
                        st.success("Added to Watch Later!")
                        st.rerun()

    with col2:
        st.markdown("<h2 style='color: #ffffff;'>📖 Overview</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #ffffff;'>{movie['overview']}</p>", unsafe_allow_html=True)

        info_col1, info_col2, info_col3 = st.columns(3)

        with info_col1:
            st.metric("⭐ Rating", f"{movie['vote_average']}/10")

        with info_col2:
            st.metric("📅 Release Year", movie['release_date'][:4] if movie.get('release_date') else 'N/A')

        with info_col3:
            st.metric("⏱️ Runtime", f"{movie.get('runtime', 'N/A')} min")

        st.markdown("<h2 style='color: #ffffff;'>🎭 Genres</h2>", unsafe_allow_html=True)
        genres = ", ".join([g['name'] for g in movie.get('genres', [])])
        st.markdown(f"<p style='color: #ffffff;'>{genres if genres else 'N/A'}</p>", unsafe_allow_html=True)

        st.markdown("<h2 style='color: #ffffff;'>🌍 Language</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #ffffff;'>{movie.get('original_language', 'N/A').upper()}</p>", unsafe_allow_html=True)

        if movie.get('budget') and movie['budget'] > 0:
            st.markdown("<h2 style='color: #ffffff;'>💰 Budget</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: #ffffff;'>${movie['budget']:,}</p>", unsafe_allow_html=True)

        if movie.get('revenue') and movie['revenue'] > 0:
            st.markdown("<h2 style='color: #ffffff;'>💵 Revenue</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: #ffffff;'>${movie['revenue']:,}</p>", unsafe_allow_html=True)

    # Cast Section
    st.markdown("---")
    st.markdown("<h2 style='color: #ffffff;'>👥 Cast</h2>", unsafe_allow_html=True)
    cast = credits.get('cast', [])[:10]

    if cast:
        cast_cols = st.columns(5)
        for idx, actor in enumerate(cast[:5]):
            with cast_cols[idx]:
                if actor.get('profile_path'):
                    st.image(f"https://image.tmdb.org/t/p/w200{actor['profile_path']}")
                else:
                    st.image("https://via.placeholder.com/200x300?text=No+Image")
                st.markdown(f"<p style='color: #ffffff; font-weight: bold;'>{actor['name']}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='color: #cccccc; font-size: 12px;'>{actor.get('character', 'Unknown')}</p>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='color: #ffffff;'>No cast information available</p>", unsafe_allow_html=True)

    # Crew Section
    st.markdown("---")
    st.markdown("<h2 style='color: #ffffff;'>🎬 Crew</h2>", unsafe_allow_html=True)
    crew = credits.get('crew', [])

    director = next((c['name'] for c in crew if c['job'] == 'Director'), 'N/A')
    producer = next((c['name'] for c in crew if c['job'] == 'Producer'), 'N/A')
    writer = next((c['name'] for c in crew if c['job'] in ['Writer', 'Screenplay']), 'N/A')
    music = next((c['name'] for c in crew if c['job'] == 'Original Music Composer'), 'N/A')

    crew_col1, crew_col2, crew_col3, crew_col4 = st.columns(4)

    with crew_col1:
        st.markdown("<p style='color: #ffffff; font-weight: bold;'>Director</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #ffffff;'>{director}</p>", unsafe_allow_html=True)

    with crew_col2:
        st.markdown("<p style='color: #ffffff; font-weight: bold;'>Producer</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #ffffff;'>{producer}</p>", unsafe_allow_html=True)

    with crew_col3:
        st.markdown("<p style='color: #ffffff; font-weight: bold;'>Writer</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #ffffff;'>{writer}</p>", unsafe_allow_html=True)

    with crew_col4:
        st.markdown("<p style='color: #ffffff; font-weight: bold;'>Music</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #ffffff;'>{music}</p>", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("⬅ Back to Recommendations"):
        st.session_state.selected_movie = None
        st.rerun()


# =====================================================
# DASHBOARD PAGE
# =====================================================
def dashboard_page():
    st.markdown("<h1 style='color: #ffffff;'>📊 User Dashboard</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: #ffffff;'>Welcome, <strong>{st.session_state.username}</strong>!</p>", unsafe_allow_html=True)

    # Metrics
    col1, col2, col3 = st.columns(3)

    history = get_user_history(st.session_state.username)
    most_viewed = get_most_viewed(st.session_state.username)

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Activities", len(history))
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Liked Movies", len(st.session_state.liked_movies))
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Watch Later", len(st.session_state.watch_later))
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Activity Chart
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("<h2 style='color: #ffffff;'>📈 Activity Over Time</h2>", unsafe_allow_html=True)
        if history:
            df_history = pd.DataFrame(history, columns=['Movie', 'Action', 'Timestamp'])
            df_history['Timestamp'] = pd.to_datetime(df_history['Timestamp'])
            df_history['Date'] = df_history['Timestamp'].dt.date

            activity_count = df_history.groupby('Date').size().reset_index(name='Count')

            fig = px.line(
                activity_count,
                x='Date',
                y='Count',
                title='Daily Activity',
                template='plotly_dark'
            )
            fig.update_traces(line_color='#ff4b4b')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No activity data yet")

    with col_b:
        st.markdown("<h2 style='color: #ffffff;'>🎬 Most Viewed Movies</h2>", unsafe_allow_html=True)
        if most_viewed:
            df_viewed = pd.DataFrame(most_viewed, columns=['Movie', 'Views'])

            fig = px.bar(
                df_viewed,
                x='Views',
                y='Movie',
                orientation='h',
                title='Top 10 Movies',
                template='plotly_dark',
                color='Views',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No viewing data yet")

    # Recent Activity
    st.markdown("---")
    st.markdown("<h2 style='color: #ffffff;'>📜 Recent Activity</h2>", unsafe_allow_html=True)

    if history:
        df_recent = pd.DataFrame(history[:20], columns=['Movie', 'Action', 'Timestamp'])
        st.dataframe(df_recent, use_container_width=True, hide_index=True)
    else:
        st.info("No recent activity")


# =====================================================
# HOME PAGE WITH GENRE SEARCH
# =====================================================
def home_page():
    st.markdown("<h1 style='color: #ffffff;'>🎬 Movie Recommendation System</h1>", unsafe_allow_html=True)

    # Search by movie name
    selected_movie_name = st.selectbox("🔍 Search by Movie Name", movies['title'].values)

    # Search by genre
    st.markdown("<h3 style='color: #ffffff;'>🎭 Search by Genre</h3>", unsafe_allow_html=True)
    genre_options = ["Action", "Comedy", "Drama", "Horror", "Sci-Fi", "Romance", "Thriller", "Animation", "Adventure", "Fantasy"]
    selected_genre = st.selectbox("Select Genre", ["All"] + genre_options)

    if selected_genre != "All":
        st.info(f"Filtering by genre: {selected_genre}")

    if st.button("Recommend", type="primary"):
        with st.spinner("Generating recommendations..."):
            st.session_state.recommendations = recommend(selected_movie_name)
            add_to_history(st.session_state.username, 0, selected_movie_name, 'searched')

    if "recommendations" in st.session_state:
        names, posters = st.session_state.recommendations

        if names and posters:
            st.markdown("<h3 style='color: #ffffff;'>🎥 Recommended Movies</h3>", unsafe_allow_html=True)
            cols = st.columns(5)

            for i in range(len(names)):
                with cols[i]:
                    st.image(posters[i])
                    st.markdown(f"<p style='color: #ffffff; text-align: center;'>{names[i]}</p>", unsafe_allow_html=True)

                    movie_id = movies.iloc[
                        movies[movies['title'] == names[i]].index[0]
                    ].movie_id

                    if st.button("View", key=f"view_{i}"):
                        st.session_state.selected_movie = movie_id
                        st.rerun()
        else:
            st.error("Unable to generate recommendations. Please try again.")


# =====================================================
# LIKED MOVIES PAGE
# =====================================================
def liked_page():
    st.markdown("<h1 style='color: #ffffff;'>❤️ Liked Movies</h1>", unsafe_allow_html=True)

    if not st.session_state.liked_movies:
        st.info("You haven't liked any movies yet!")
        return

    cols = st.columns(5)

    for idx, movie_id in enumerate(st.session_state.liked_movies):
        with cols[idx % 5]:
            try:
                poster = fetch_poster(movie_id)
                movie = fetch_movie_details(movie_id)

                st.image(poster)
                st.markdown(f"<p style='color: #ffffff; text-align: center;'>{movie['title']}</p>", unsafe_allow_html=True)

                if st.button("View", key=f"liked_view_{idx}"):
                    st.session_state.selected_movie = movie_id
                    st.rerun()

                if st.button("Remove", key=f"liked_remove_{idx}"):
                    st.session_state.liked_movies.remove(movie_id)
                    remove_liked_movie(st.session_state.username, movie_id)
                    st.rerun()
            except Exception as e:
                st.error(f"Error loading movie {movie_id}: {str(e)}")

# =====================================================
# WATCH LATER PAGE
# =====================================================
def watch_later_page():
    st.markdown("<h1 style='color: #ffffff;'>⏰ Watch Later</h1>", unsafe_allow_html=True)

    if not st.session_state.watch_later:
        st.info("You haven't added any movies to watch later!")
        return

    cols = st.columns(5)

    for idx, movie_id in enumerate(st.session_state.watch_later):
        with cols[idx % 5]:
            try:
                poster = fetch_poster(movie_id)
                movie = fetch_movie_details(movie_id)

                st.image(poster)
                st.markdown(f"<p style='color: #ffffff; text-align: center;'>{movie['title']}</p>", unsafe_allow_html=True)

                if st.button("View", key=f"watch_view_{idx}"):
                    st.session_state.selected_movie = movie_id
                    st.rerun()

                if st.button("Remove", key=f"watch_remove_{idx}"):
                    st.session_state.watch_later.remove(movie_id)
                    remove_watch_later(st.session_state.username, movie_id)
                    st.rerun()
            except Exception as e:
                st.error(f"Error loading movie {movie_id}: {str(e)}")


# =====================================================
# MAIN ROUTING LOGIC
# =====================================================
if st.session_state.selected_movie is not None:
    show_movie_details(st.session_state.selected_movie)
elif st.session_state.current_page == "home":
    home_page()
elif st.session_state.current_page == "dashboard":
    dashboard_page()
elif st.session_state.current_page == "liked":
    liked_page()
elif st.session_state.current_page == "watch_later":
    watch_later_page()