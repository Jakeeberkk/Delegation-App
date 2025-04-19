
import streamlit as st
from difflib import SequenceMatcher

st.set_page_config(page_title="Delegation Assistant", layout="centered")

st.title("Delegation Assistant Tool")
st.write("Match your tasks to the best-fit team members based on their strengths.")

# Predefined options
default_strengths = [
    "Scheduling", "Email management", "Customer service", "Cold calling", "Data entry",
    "Reporting", "Sales follow-up", "Creative thinking", "Social media", "Inventory tracking",
    "Order processing", "Project management", "Vendor communication", "Bookkeeping"
]

default_weaknesses = [
    "Detail orientation", "Cold outreach", "Managing time", "Public speaking", "Data analysis",
    "Technical skills", "Creative thinking", "Phone communication"
]

# Session state to store employees and tasks
if "employees" not in st.session_state:
    st.session_state.employees = []

if "tasks" not in st.session_state:
    st.session_state.tasks = []

# Employee Entry
st.header("1. Add Employee")
with st.form("employee_form"):
    name = st.text_input("Name")
    role = st.text_input("Role")
    strengths = st.multiselect("Strengths", default_strengths)
    custom_strength = st.text_input("Custom Strength (optional)")
    weaknesses = st.multiselect("Weaknesses", default_weaknesses)
    custom_weakness = st.text_input("Custom Weakness (optional)")
    submitted = st.form_submit_button("Add Employee")

    if submitted and name:
        all_strengths = strengths + ([custom_strength] if custom_strength else [])
        all_weaknesses = weaknesses + ([custom_weakness] if custom_weakness else [])
        st.session_state.employees.append({
            "name": name,
            "role": role,
            "strengths": [s.strip().lower() for s in all_strengths],
            "weaknesses": [w.strip().lower() for w in all_weaknesses]
        })
        st.success(f"Added employee: {name}")

# View and Remove Employees
if st.session_state.employees:
    st.subheader("Current Employees")
    for i, emp in enumerate(st.session_state.employees):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{emp['name']}** – {emp['role']}")
        with col2:
            if st.button("Remove", key=f"remove_emp_{i}"):
                st.session_state.employees.pop(i)
                st.experimental_rerun()

# Task Entry
st.header("2. Time Audit - Add Task")
with st.form("task_form"):
    task_desc = st.text_input("Task Description")
    task_time = st.number_input("Time Spent (in minutes)", min_value=1, step=1)
    delegatable = st.radio("Would you like to delegate this task?", ("Yes", "No"))
    task_submitted = st.form_submit_button("Add Task")

    if task_submitted and task_desc:
        st.session_state.tasks.append({
            "description": task_desc.strip(),
            "time_spent": task_time,
            "delegatable": delegatable == "Yes"
        })
        st.success(f"Added task: {task_desc}")

# View and Remove Tasks
if st.session_state.tasks:
    st.subheader("Current Tasks")
    for i, task in enumerate(st.session_state.tasks):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{task['description']}** – {task['time_spent']} mins – Delegatable: {task['delegatable']}")
        with col2:
            if st.button("Remove", key=f"remove_task_{i}"):
                st.session_state.tasks.pop(i)
                st.experimental_rerun()

# Matching Logic
def find_best_match(task_desc, employees):
    best_match = None
    best_score = 0
    for emp in employees:
        for strength in emp["strengths"]:
            score = SequenceMatcher(None, task_desc.lower(), strength).ratio()
            if score > best_score:
                best_score = score
                best_match = emp
    return best_match if best_score > 0.4 else None

# Delegation Output
st.header("3. Delegation Recommendations")
if st.button("Run Delegation Match"):
    if not st.session_state.employees or not st.session_state.tasks:
        st.warning("Please add both employees and tasks before running the match.")
    else:
        for task in st.session_state.tasks:
            if task["delegatable"]:
                match = find_best_match(task["description"], st.session_state.employees)
                if match:
                    st.success(f"'{task['description']}' → {match['name']} ({match['role']})")
                else:
                    st.warning(f"No strong match found for: '{task['description']}'")
            else:
                st.info(f"Keep this task: '{task['description']}'")
