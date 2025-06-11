import streamlit as st
import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_URL = os.getenv("API_URL")

st.set_page_config(page_title="Quiz App", layout="centered")

if "token" not in st.session_state:
    st.session_state.token = None
if "selected_section" not in st.session_state:
    st.session_state.selected_section = None

st.title("Quiz App")

def signup():
    st.subheader("Sign Up")
    username = st.text_input("Username", key="signup_user")
    password = st.text_input("Password", type="password", key="signup_pass")
    if st.button("Sign Up"):
        res = requests.post(f"{API_URL}/signup", json={"username": username, "password": password})
        if res.status_code == 200:
            st.success("Account created. Please login.")
        else:
            st.error(res.json()["detail"])

def login():
    st.subheader("Login")
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")
    if st.button("Login"):
        res = requests.post(f"{API_URL}/login", data={"username": username, "password": password})
        if res.status_code == 200:
            st.session_state.token = res.json()["access_token"]
            st.rerun()
        else:
            st.error("Invalid credentials")
def show_question():
    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    if not st.session_state.selected_section:
        section = st.selectbox("Select Section", ["Python", "Java", "C"])
        if st.button("Start Quiz"):
            st.session_state.selected_section = section
            st.session_state.show_leaderboard_after_quiz = False  # Reset
            st.rerun()
        return

    section = st.session_state.selected_section

    res = requests.get(f"{API_URL}/question?section={section}", headers=headers)
    
    # If quiz is completed
    if res.status_code != 200 or "question" not in res.json():
        st.info(res.json().get("message", f"{section} quiz completed!"))

        # Show leaderboard after last question
        show_leaderboard()

        if st.button("Change Section"):
            del st.session_state.selected_section
            st.rerun()
        return

    question = res.json()
    st.subheader(f"{section} Quiz")
    st.markdown(f"**Q: {question['question']}**")
    selected = st.radio("Choose an option:", question["options"], index=0, key=question["id"])

    if st.button("Submit Answer"):
        payload = {
            "question_id": question["id"],
            "selected_option": selected,
            "section": section
        }
        res = requests.post(f"{API_URL}/submit", headers=headers, json=payload)
        if res.status_code == 200:
            st.success("Answer submitted!")
            st.rerun()  # move to next question or completion
        else:
            st.error("Submission failed")


def show_leaderboard(key_suffix="default"):
    st.subheader("Leaderboard")

    section_options = ["Overall", "Python", "Java", "C"]
    selected_section = st.selectbox(
        "Select Leaderboard Type",
        section_options,
        key=f"leaderboard_section_{key_suffix}"
    )

    if selected_section == "Overall":
        res = requests.get(f"{API_URL}/leaderboard")
    else:
        res = requests.get(f"{API_URL}/leaderboard?section={selected_section}")

    if res.status_code == 200:
        leaderboard = res.json()
        for i, entry in enumerate(leaderboard, 1):
            st.write(f"{i}. {entry['username']} - {entry['score']} pts")
    else:
        st.error("Could not load leaderboard")

if not st.session_state.token:
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        login()
    with tab2:
        signup()
else:
    tab1, tab2 = st.tabs(["Play Quiz", "Leaderboard"])
    with tab1:
        show_question()
    with tab2:
        show_leaderboard("tab")

    if st.button("Logout"):
        st.session_state.token = None
        if "selected_section" in st.session_state:
            del st.session_state.selected_section
        st.rerun()