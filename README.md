# 🎬 Movie Recommendation System

A full-featured **content-based movie recommendation web app** built using **Streamlit**, with user authentication, personalized features, and an interactive dashboard.

---

## 🚀 Live Features

✨ Search movies and get recommendations
❤️ Like movies and save favorites
⏰ Add movies to Watch Later
📊 Personal dashboard with activity analytics
🔐 User authentication (Login/Register)
🎥 Movie details with posters, cast, crew & trailers

---

## 🧠 How It Works

This project uses **Content-Based Filtering**:

* Combines movie features like **genres, keywords, cast, crew**
* Converts text data into vectors using **CountVectorizer**
* Calculates similarity using **Cosine Similarity**
* Recommends top similar movies

---

## 🛠️ Tech Stack

* **Frontend/UI**: Streamlit
* **Backend**: Python
* **Database**: SQLite
* **Libraries**:

  * Pandas
  * NumPy
  * Scikit-learn
  * Plotly
  * Requests

---

## 📂 Project Structure

```id="ps1"
Movie-recommendation-system/
│── app.py
│── requirements.txt
│── .gitignore
│── users.db (auto-created)
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone Repository

```id="ps2"
git clone https://github.com/kushali-kanvitha/Movie-recommendation-system.git
cd Movie-recommendation-system
```

### 2️⃣ Install Dependencies

```id="ps3"
pip install -r requirements.txt
```

### 3️⃣ Run Application

```id="ps4"
streamlit run app.py
```

---

## 🔑 API Configuration

This project uses the **TMDB API**.

👉 Replace API key inside the code:

```id="ps5"
api_key = "YOUR_API_KEY"
```

Get your API key from: https://www.themoviedb.org/

---

## 📊 Dataset

Dataset used: **TMDB 5000 Movies Dataset**

Download from:
https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata

---

## ⚠️ Important Note

Large files are not included in this repository:

* `.csv` dataset files
* `.pkl` model files
* `.db` database files

👉 You need to generate them manually or download separately.

---

## 📸 Screenshots

<img width="1600" height="486" alt="WhatsApp Image 2026-04-26 at 09 56 59" src="https://github.com/user-attachments/assets/c0d03d34-ff4e-4f22-b33e-dd6c819e71cd" />
<img width="1600" height="690" alt="image" src="https://github.com/user-attachments/assets/924c2cb6-5552-44b1-90dd-95a40fe78684" />

<img width="1326" height="751" alt="image" src="https://github.com/user-attachments/assets/f6c82188-a1c2-408b-9245-30a0e3d26d6a" />

<img width="1206" height="736" alt="image" src="https://github.com/user-attachments/assets/f37db1c4-bb4e-4f09-b5e0-f55492910eeb" />

---

## 📈 Future Enhancements

* Add collaborative filtering
* Deploy on cloud (Streamlit Cloud / Render)
* Improve recommendation accuracy
* Add real Google OAuth login
* Add search filters (year, rating, language)

---


