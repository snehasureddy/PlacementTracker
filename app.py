import sqlite3

import streamlit as st


DATABASE_NAME = "placements.db"
STATUS_OPTIONS = [
    "Applied",
    "Shortlisted",
    "Interview Scheduled",
    "Selected",
    "Rejected",
]


# Create a database connection and always close it after the operation.
def connect_to_database():
    connection = sqlite3.connect(DATABASE_NAME)
    return connection


# Add a new application using a parameterized SQL query.
def add_application(company_name, job_role, application_date, status):
    connection = connect_to_database()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO applications
            (company_name, job_role, application_date, status)
            VALUES (?, ?, ?, ?)
            """,
            (company_name, job_role, application_date, status),
        )
        connection.commit()
        return True
    except sqlite3.Error as error:
        connection.rollback()
        st.error(f"Could not add the application: {error}")
        return False
    finally:
        connection.close()


# Retrieve every application from the database.
def get_all_applications():
    connection = connect_to_database()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT application_id, company_name, job_role, application_date, status
            FROM applications
            ORDER BY application_id DESC
            """
        )
        return cursor.fetchall()
    except sqlite3.Error as error:
        st.error(f"Could not retrieve applications: {error}")
        return []
    finally:
        connection.close()


# Count all applications in the database.
def get_total_applications():
    connection = connect_to_database()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM applications")
        return cursor.fetchone()[0]
    except sqlite3.Error as error:
        st.error(f"Could not calculate the total: {error}")
        return 0
    finally:
        connection.close()


# Find the highest-count role. If there is a tie, list roles in alphabetical order.
def get_most_applied_roles():
    connection = connect_to_database()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT job_role, COUNT(*) AS application_count
            FROM applications
            WHERE job_role IS NOT NULL AND TRIM(job_role) <> ''
            GROUP BY job_role
            """
        )
        role_counts = cursor.fetchall()

        if not role_counts:
            return [], 0

        highest_count = max(count for _, count in role_counts)
        tied_roles = [role for role, count in role_counts if count == highest_count]
        tied_roles.sort(key=lambda role: role.lower())
        return tied_roles, highest_count
    except sqlite3.Error as error:
        st.error(f"Could not calculate the most applied role: {error}")
        return [], 0
    finally:
        connection.close()


# Count applications for each status. Missing statuses have a count of zero.
def get_status_summary():
    connection = connect_to_database()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT status, COUNT(*)
            FROM applications
            WHERE status IS NOT NULL
            GROUP BY status
            """
        )
        results = cursor.fetchall()

        summary = {status: 0 for status in STATUS_OPTIONS}
        for status, count in results:
            if status in summary:
                summary[status] = count
        return summary
    except sqlite3.Error as error:
        st.error(f"Could not calculate the status summary: {error}")
        return {status: 0 for status in STATUS_OPTIONS}
    finally:
        connection.close()


# Set up the page and sidebar navigation.
st.set_page_config(page_title="Placement Application Tracker", layout="wide")
st.title("Placement Application Tracker")

menu = st.sidebar.radio(
    "Navigation",
    [
        "Add Application",
        "View Applications",
        "Total Applications",
        "Most Applied Role",
        "Status-wise Summary",
    ],
)


# Feature 1: Add Application.
if menu == "Add Application":
    st.header("Add Application")

    company_name = st.text_input("Company Name")
    job_role = st.text_input("Job Role")
    application_date = st.date_input("Application Date")
    status = st.selectbox("Status", STATUS_OPTIONS)

    if st.button("Add Application"):
        company_name = company_name.strip()
        job_role = job_role.strip()

        if not company_name:
            st.error("Company Name cannot be empty.")
        elif not job_role:
            st.error("Job Role cannot be empty.")
        else:
            added = add_application(
                company_name,
                job_role,
                application_date.strftime("%Y-%m-%d"),
                status,
            )
            if added:
                st.success("Application added successfully!")


# Feature 2: View Applications.
elif menu == "View Applications":
    st.header("All Applications")

    applications = get_all_applications()

    if applications:
        table_rows = []
        for application in applications:
            table_rows.append(
                {
                    "application_id": application[0],
                    "company_name": application[1],
                    "job_role": application[2],
                    "application_date": application[3],
                    "status": application[4],
                }
            )
        st.dataframe(table_rows, use_container_width=True, hide_index=True)
    else:
        st.info("No applications have been added yet.")


# Feature 3: Total Applications.
elif menu == "Total Applications":
    st.header("Total Applications")

    total = get_total_applications()
    st.metric("Total applications", total)


# Feature 4: Most Applied Role.
elif menu == "Most Applied Role":
    st.header("Most Applied Role")

    role_list, highest_count = get_most_applied_roles()

    if not role_list:
        st.info("No applications are available to calculate the most applied role.")
    elif len(role_list) == 1:
        st.subheader(role_list[0])
        st.write(f"Applications: {highest_count}")
    else:
        st.write("The highest count is shared by the following roles:")
        for role in role_list:
            st.write(f"- {role} ({highest_count} applications)")


# Feature 5: Status-wise Summary.
elif menu == "Status-wise Summary":
    st.header("Status-wise Summary")

    status_summary = get_status_summary()

    if get_total_applications() == 0:
        st.info("No applications are available for a status summary.")
    else:
        for status in STATUS_OPTIONS:
            st.write(f"**{status}:** {status_summary[status]}")

        st.subheader("Application Status Chart")
        st.bar_chart(status_summary)
