"""
Runs my Study Planner website using Flask and SQLite.

Manages study tasks using an SQLite database, including adding, editing,
deleting, completing, filtering, sorting, searching and displaying tasks.
"""

import calendar as calendar_module
import os
import sqlite3
from datetime import datetime

from flask import Flask, redirect, render_template, request, url_for


# Creates the Flask application
app = Flask(__name__)


# Database setup

# Creates a reliable path to the database file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "flask_assement.db")


def get_db_connection():
    """Creates and returns a connection to the SQLite database."""

    # Connects Flask to the SQLite database
    conn = sqlite3.connect(DATABASE)

    # Allows database rows to be accessed using their column names
    conn.row_factory = sqlite3.Row

    return conn


# Dashboard

@app.route("/")
def dashboard():
    """Displays task statistics, upcoming deadlines and the focus task."""

    # Connects to the database
    conn = get_db_connection()

    # Counts all tasks stored in the database
    total_tasks = conn.execute(
        "SELECT COUNT(*) FROM tasks"
    ).fetchone()[0]

    # Counts tasks that have not been completed
    active_tasks = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE completed = 0"
    ).fetchone()[0]

    # Counts tasks that have been completed
    completed_tasks = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE completed = 1"
    ).fetchone()[0]

    # Counts active tasks marked as high priority
    high_priority_tasks = conn.execute(
        """
        SELECT COUNT(*)
        FROM tasks
        WHERE priority = 'High'
        AND completed = 0
        """
    ).fetchone()[0]

    # Gets the four closest active tasks that have due dates
    upcoming_tasks = conn.execute(
        """
        SELECT *
        FROM tasks
        WHERE completed = 0
        AND due_date IS NOT NULL
        AND due_date != ''
        ORDER BY due_date ASC
        LIMIT 4
        """
    ).fetchall()

    # Gets the closest active task for the Today's Focus section
    focus_task = conn.execute(
        """
        SELECT *
        FROM tasks
        WHERE completed = 0
        AND due_date IS NOT NULL
        AND due_date != ''
        ORDER BY due_date ASC
        LIMIT 1
        """
    ).fetchone()

    # Closes the database connection once the data has been collected
    conn.close()

    # Sends all dashboard information to the HTML template
    return render_template(
        "dashboard.html",
        total_tasks=total_tasks,
        active_tasks=active_tasks,
        completed_tasks=completed_tasks,
        high_priority_tasks=high_priority_tasks,
        upcoming_tasks=upcoming_tasks,
        focus_task=focus_task,
    )


# Tasks page

@app.route("/tasks")
def tasks_page():
    """Displays tasks and allows them to be filtered, searched and sorted."""

    # Gets the filter, search and sort options selected by the user
    task_filter = request.args.get("filter", "all")
    priority_filter = request.args.get("priority", "all")
    search_term = request.args.get("search", "")
    sort_order = request.args.get("sort", "none")

    # Connects to the database
    conn = get_db_connection()

    # Starts a base query that extra conditions can be added to
    query = "SELECT * FROM tasks WHERE 1=1"

    # Stores values that will be safely added to the SQL query
    params = []

    # Filters tasks depending on whether they are active or completed
    if task_filter == "completed":
        query += " AND completed = 1"
    elif task_filter == "active":
        query += " AND completed = 0"

    # Adds a priority filter if the user selects a specific priority
    if priority_filter != "all":
        query += " AND priority = ?"
        params.append(priority_filter)

    # Searches the task title and subject for the user's search
    if search_term:
        query += " AND (title LIKE ? OR subject LIKE ?)"

        # Allows the search to match part of a title or subject
        search_value = f"%{search_term}%"
        params.extend([search_value, search_value])

    # Sorts tasks from the earliest due date to the latest
    if sort_order == "oldest":
        query += " ORDER BY due_date ASC"

    # Sorts tasks from the latest due date to the earliest
    elif sort_order == "newest":
        query += " ORDER BY due_date DESC"

    # Runs the finished query and gets all matching tasks
    tasks = conn.execute(query, params).fetchall()

    # Closes the database connection
    conn.close()

    # Sends the tasks and selected options to the tasks page
    return render_template(
        "tasks.html",
        tasks=tasks,
        task_filter=task_filter,
        priority_filter=priority_filter,
        search=search_term,
        sort=sort_order,
    )


# Adding a task

@app.route("/add", methods=["POST"])
def add_task():
    """Adds a new task to the database using information from the form."""

    # Gets the task information entered by the user
    title = request.form["title"]
    subject = request.form["subject"]
    due_date = request.form["due_date"]
    priority = request.form["priority"]

    # Connects to the database
    conn = get_db_connection()

    # Inserts the new task into the tasks table
    conn.execute(
        """
        INSERT INTO tasks
        (title, subject, due_date, completed, priority)
        VALUES (?, ?, ?, ?, ?)
        """,
        (title, subject, due_date, 0, priority),
    )

    # Saves the new task and closes the database connection
    conn.commit()
    conn.close()

    # Takes the user back to the tasks page
    return redirect(url_for("tasks_page"))


# Completing a task

@app.route("/complete/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    """Marks the selected task as completed."""

    # Connects to the database
    conn = get_db_connection()

    # Changes completed to 1 for the task with the matching ID
    conn.execute(
        "UPDATE tasks SET completed = 1 WHERE id = ?",
        (task_id,),
    )

    # Saves the change and closes the database connection
    conn.commit()
    conn.close()

    # Takes the user back to the tasks page
    return redirect(url_for("tasks_page"))


# Deleting a task

@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    """Deletes the selected task from the database."""

    # Connects to the database
    conn = get_db_connection()

    # Deletes the task with the matching ID
    conn.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,),
    )

    # Saves the change and closes the database connection
    conn.commit()
    conn.close()

    # Takes the user back to the tasks page
    return redirect(url_for("tasks_page"))


# Editing a task

@app.route("/edit/<int:task_id>")
def edit_task(task_id):
    """Loads the selected task so its information can be edited."""

    # Connects to the database
    conn = get_db_connection()

    # Finds the task that matches the selected task ID
    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,),
    ).fetchone()

    # Closes the database connection
    conn.close()

    # Sends the selected task information to the edit page
    return render_template("edit.html", task=task)


# Updating a task

@app.route("/update/<int:task_id>", methods=["POST"])
def update_task(task_id):
    """Updates the selected task using information from the edit form."""

    # Gets the updated information entered by the user
    title = request.form["title"]
    subject = request.form["subject"]
    due_date = request.form["due_date"]
    priority = request.form["priority"]

    # Connects to the database
    conn = get_db_connection()

    # Updates the task that has the matching ID
    conn.execute(
        """
        UPDATE tasks
        SET title = ?,
            subject = ?,
            due_date = ?,
            priority = ?
        WHERE id = ?
        """,
        (title, subject, due_date, priority, task_id),
    )

    # Saves the changes and closes the database connection
    conn.commit()
    conn.close()

    # Takes the user back to the tasks page
    return redirect(url_for("tasks_page"))


# Calendar

@app.route("/calendar")
def calendar_page():
    """Displays active tasks in a monthly calendar view."""

    # Gets today's date so the current day can be highlighted
    today = datetime.today()

    # Gets the selected year and month from the URL
    # If none are selected, it uses the current year and month
    year = request.args.get("year", today.year, type=int)
    month = request.args.get("month", today.month, type=int)

    # Creates the weeks and days needed for the monthly calendar
    month_calendar = calendar_module.Calendar(
        firstweekday=0
    ).monthdayscalendar(year, month)

    # Works out the previous month for the calendar navigation
    if month == 1:
        previous_month = 12
        previous_year = year - 1
    else:
        previous_month = month - 1
        previous_year = year

    # Works out the next month for the calendar navigation
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    # Creates the first date of the selected month
    month_start = f"{year}-{month:02d}-01"

    # Creates the first date of the next month
    # This is used as the end point of the database query
    next_month_start = f"{next_year}-{next_month:02d}-01"

    # Connects to the database
    conn = get_db_connection()

    # Gets active tasks with due dates inside the selected month
    tasks = conn.execute(
        """
        SELECT *
        FROM tasks
        WHERE completed = 0
        AND due_date IS NOT NULL
        AND due_date != ''
        AND due_date >= ?
        AND due_date < ?
        ORDER BY due_date ASC
        """,
        (month_start, next_month_start),
    ).fetchall()

    # Closes the database connection
    conn.close()

    # Creates a dictionary for grouping tasks by their due date
    tasks_by_day = {}

    # Goes through each task found for the selected month
    for task in tasks:

        # Takes the day number from the stored YYYY-MM-DD due date
        day = int(task["due_date"][8:10])

        # Creates a list for the day if one does not already exist
        if day not in tasks_by_day:
            tasks_by_day[day] = []

        # Adds the task to the correct calendar day
        tasks_by_day[day].append(task)

    # Gets the written name of the selected month
    month_name = calendar_module.month_name[month]

    # Sends all calendar information to the HTML template
    return render_template(
        "calendar.html",
        month_calendar=month_calendar,
        tasks_by_day=tasks_by_day,
        month_name=month_name,
        month=month,
        year=year,
        previous_month=previous_month,
        previous_year=previous_year,
        next_month=next_month,
        next_year=next_year,
        today=today,
    )


# Study timer

@app.route("/timer")
def timer():
    """Displays the study timer page."""

    # Loads and displays the HTML page containing the study timer
    return render_template("timer.html")


# Starts the Flask website

if __name__ == "__main__":

    # Runs the website on port 5001 while it is being developed
    app.run(host="0.0.0.0", port=5001, debug=True)