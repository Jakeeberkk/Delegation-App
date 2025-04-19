
import streamlit as st
from difflib import SequenceMatcher

st.set_page_config(page_title="Delegation Assistant", layout="centered")

st.title("Delegation Assistant Tool")
st.write("Match your tasks to the best-fit team members based on their strengths.")

# Expanded options
default_strengths = [
    "Task prioritization", "Calendar & meeting management", "CRM usage", "Invoicing & payment follow-up",
    "Vendor communication", "Managing inbox", "Taking notes during meetings", "Creating SOPs",
    "Spreadsheet building", "Data cleanup", "Travel booking", "Project tracking", "Social media scheduling",
    "Customer follow-up", "Cold calling", "Warm lead nurturing", "Quote generation", "Order processing",
    "Inventory tracking", "Creating reports", "Writing professional emails", "Problem-solving under pressure",
    "Cross-functional coordination", "File and folder organization", "Research & summarizing information"
]

default_weaknesses = [
    "Easily overwhelmed with multi-tasking", "Avoids confrontation or client follow-up", "Not detail-oriented",
    "Struggles with written communication", "Doesn’t enjoy phone calls", "Gets distracted easily",
    "Avoids complex spreadsheets or numbers", "Uncomfortable with tech tools or new software",
    "Poor time estimation", "Doesn’t take initiative", "Slow response time", "Struggles with follow-through",
    "Disorganized digital workspace", "Doesn’t document processes", "Uncomfortable giving or receiving feedback"
]

if "employees" not in st.session_state:
    st.session_state.employees = []
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# Employee form
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

# View and remove employees
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

# Task form
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
            "delegatable": delegatable == "Yes",
            "manual_override": None
        })
        st.success(f"Added task: {task_desc}")

# View and remove tasks
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

# Matching logic
def get_similarity(task_desc, strength):
    return SequenceMatcher(None, task_desc.lower(), strength).ratio()

def find_best_match(task_desc, employees):
    emp_scores = {}
    for emp in employees:
        max_score = max((get_similarity(task_desc, s) for s in emp["strengths"]), default=0)
        emp_scores[emp["name"]] = (emp, max_score)

    sorted_scores = sorted(emp_scores.values(), key=lambda x: x[1], reverse=True)
    best_match = sorted_scores[0][0] if sorted_scores and sorted_scores[0][1] > 0.4 else None
    return best_match, sorted_scores[:2]

# Delegation output
st.header("3. Delegation Recommendations")
if st.button("Run Delegation Match"):
    if not st.session_state.employees or not st.session_state.tasks:
        st.warning("Please add both employees and tasks before running the match.")
    else:
        for idx, task in enumerate(st.session_state.tasks):
            if task["delegatable"]:
                match, top_matches = find_best_match(task["description"], st.session_state.employees)
                if match:
                    st.success(f"'{task['description']}' → {match['name']} ({match['role']})")
                else:
                    st.warning(f"No strong match found for: '{task['description']}'")
                    if top_matches:
                        st.markdown("**Closest Matches:**")
                        for candidate, score in top_matches:
                            st.markdown(f"- {candidate['name']} ({candidate['role']}) – Similarity: {round(score, 2)}")
                        manual_choice = st.selectbox(
                            f"Manually assign '{task['description']}'?",
                            [None] + [emp["name"] for emp in st.session_state.employees],
                            key=f"manual_override_{idx}"
                        )
                        if manual_choice:
                            st.info(f"'{task['description']}' manually assigned to {manual_choice}")
            else:
                st.info(f"Keep this task: '{task['description']}'")
