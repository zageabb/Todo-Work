import streamlit as st
import sqlite3
import datetime

# Database functions
def init_db():
    conn = sqlite3.connect("todo_list.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            department TEXT,
            contact_person TEXT,
            status TEXT,
            created_at TEXT,
            timer_start TEXT,
            time_spent REAL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def add_task(title, description, department, contact_person, status):
    conn = sqlite3.connect("todo_list.db")
    cursor = conn.cursor()
    created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO todos (title, description, department, contact_person, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title, description, department, contact_person, status, created_at))
    conn.commit()
    conn.close()

def fetch_tasks():
    conn = sqlite3.connect("todo_list.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM todos WHERE status != 'Completed' ORDER BY created_at")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_task(task_id, **kwargs):
    conn = sqlite3.connect("todo_list.db")
    cursor = conn.cursor()
    for key, value in kwargs.items():
        if value is not None:
            cursor.execute(f"UPDATE todos SET {key} = ? WHERE id = ?", (value, task_id))
    conn.commit()
    conn.close()

def fetch_task_by_id(task_id):
    conn = sqlite3.connect("todo_list.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM todos WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    return row

# Streamlit app
st.title("To-Do List Manager")
init_db()

# Navigation
menu = st.sidebar.selectbox("Menu", ["View Tasks", "Add Task", "Edit Task"])

# Add Task
if menu == "Add Task":
    st.header("Add New Task")
    with st.form("add_task_form"):
        title = st.text_input("Title")
        description = st.text_area("Description")
        department = st.text_input("Department")
        contact_person = st.text_input("Contact Person")
        status = st.selectbox("Status", ["Pending", "In Progress", "Completed"])
        submitted = st.form_submit_button("Add Task")
        if submitted:
            add_task(title, description, department, contact_person, status)
            st.success(f"Task '{title}' added successfully!")

# View Tasks
elif menu == "View Tasks":
    st.header("Outstanding Tasks")
    tasks = fetch_tasks()
    for task in tasks:
        task_id, title, description, department, contact_person, status, created_at, timer_start, time_spent = task
        with st.expander(f"{title} (Status: {status})"):
            st.write(f"**Description:** {description}")
            st.write(f"**Department:** {department}")
            st.write(f"**Contact Person:** {contact_person}")
            st.write(f"**Created At:** {created_at}")
            st.write(f"**Time Spent:** {time_spent:.2f} hours")

            # Timer logic
            if st.button(f"Start Timer ({title})", key=f"start_{task_id}"):
                update_task(task_id, timer_start=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                #st.experimental_rerun()
            if st.button(f"Stop Timer ({title})", key=f"stop_{task_id}"):
                current_time = datetime.datetime.now()
                task = fetch_task_by_id(task_id)
                timer_start = task[7]
                if timer_start:
                    timer_start = datetime.datetime.strptime(timer_start, "%Y-%m-%d %H:%M:%S")
                    elapsed = (current_time - timer_start).total_seconds() / 3600
                    update_task(task_id, time_spent=task[8] + elapsed, timer_start=None)
                    #st.experimental_rerun()
                    rerun()

            # Update status
            new_status = st.selectbox(f"Update Status ({title})", ["Pending", "In Progress", "Completed"], index=["Pending", "In Progress", "Completed"].index(status), key=f"status_{task_id}")
            if st.button(f"Update Status ({title})", key=f"update_status_{task_id}"):
                update_task(task_id, status=new_status)
                st.success("Status updated!")
                #st.experimental_rerun()
                rerun()

# Edit Task
elif menu == "Edit Task":
    st.header("Edit Task")
    task_id = st.number_input("Enter Task ID to Edit", min_value=1, step=1)
    task = fetch_task_by_id(task_id)
    if task:
        with st.form("edit_task_form"):
            title = st.text_input("Title", value=task[1])
            description = st.text_area("Description", value=task[2])
            department = st.text_input("Department", value=task[3])
            contact_person = st.text_input("Contact Person", value=task[4])
            status = st.selectbox("Status", ["Pending", "In Progress", "Completed"], index=["Pending", "In Progress", "Completed"].index(task[5]))
            submitted = st.form_submit_button("Save Changes")
            if submitted:
                update_task(task_id, title=title, description=description, department=department, contact_person=contact_person, status=status)
                st.success(f"Task '{title}' updated successfully!")
    else:
        st.warning("Task not found.")
