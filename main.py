import json
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta, timezone
import requests
import os
import ctypes

# Hide the app from the taskbar on Windows
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("CountdownTaskManager")

# Get current time from online or local
def get_current_time():
    try:
        response = requests.get("http://worldtimeapi.org/api/ip", timeout=1)
        response.raise_for_status()
        time_data = response.json()
        return datetime.fromisoformat(time_data["datetime"]).astimezone(timezone.utc)
    except (requests.RequestException, KeyError, ValueError):
        return datetime.now(timezone.utc)

# Load and save task utilities
def load_tasks():
    tasks = []
    try:
        with open("tasks.json", "r") as file:
            tasks = json.load(file)
            tasks = [
                task for task in tasks 
                if isinstance(task, dict) and "name" in task and "due_date" in task
            ]
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return tasks

def save_tasks(tasks):
    with open("tasks.json", "w") as file:
        json.dump(tasks, file, indent=4)

# Load completed tasks from JSON file
def load_completed_tasks():
    completed_tasks = []
    try:
        with open("completed_tasks.json", "r") as file:
            completed_tasks = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return completed_tasks

# Save completed tasks to JSON file
def save_completed_tasks(completed_tasks):
    with open("completed_tasks.json", "w") as file:
        json.dump(completed_tasks, file, indent=4)

# Countdown Task Manager class with optimized code and unified input dialog
class CountdownTaskManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Countdown Task Manager")
        self.root.geometry("+{}+{}".format(self.root.winfo_screenwidth() - 650, 30))  # Adjusted position to fit in top-right corner
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", False)  # On top of other applications

        self.tasks = load_tasks()
        self.completed_tasks = load_completed_tasks()

        # Add Task Button
        self.add_task_button = tk.Button(root, text="Add Task", command=self.show_task_dialog, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), relief=tk.RAISED, padx=10, pady=5)
        self.add_task_button.pack(pady=10)

        # Completed Task List Frame
        self.completed_task_list_frame = tk.Frame(root, bg="lightgray", width=200)
        self.completed_task_list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.completed_task_list_label = tk.Label(self.completed_task_list_frame, text="Completed Tasks", font=("Arial", 8, "bold"), bg="white")
        self.completed_task_list_label.pack(pady=5)

        # Task display area
        self.task_list_frame = tk.Frame(root, bg="white")
        self.task_list_frame.pack(pady=5, fill=tk.BOTH, expand=True, side=tk.RIGHT)

        self.update_task_display()
        self.update_completed_task_display()

    def show_task_dialog(self, task=None):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add/Edit Task")

        # Center the dialog on screen
        dialog_width, dialog_height = 300, 350
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        dialog.geometry(f"{dialog_width}x{dialog_height}+{(screen_width - dialog_width) // 2}+{(screen_height - dialog_height) // 2}")
        dialog.transient(self.root)

        tk.Label(dialog, text="Task Name:").pack(pady=5)
        task_name_entry = tk.Entry(dialog)
        task_name_entry.pack()
        if task:
            task_name_entry.insert(0, task["name"])

        tk.Label(dialog, text="Years:").pack()
        year_entry = tk.Entry(dialog)
        year_entry.pack()
        tk.Label(dialog, text="Months:").pack()
        month_entry = tk.Entry(dialog)
        month_entry.pack()
        tk.Label(dialog, text="Days:").pack()
        day_entry = tk.Entry(dialog)
        day_entry.pack()
        tk.Label(dialog, text="Hours:").pack()
        hour_entry = tk.Entry(dialog)
        hour_entry.pack()
        tk.Label(dialog, text="Minutes:").pack()
        minute_entry = tk.Entry(dialog)
        minute_entry.pack()

        def save_task():
            task_name = task_name_entry.get()
            years = int(year_entry.get()) if year_entry.get().strip() else 0
            months = int(month_entry.get()) if month_entry.get().strip() else 0
            days = int(day_entry.get()) if day_entry.get().strip() else 0
            hours = int(hour_entry.get()) if hour_entry.get().strip() else 0
            minutes = int(minute_entry.get()) if minute_entry.get().strip() else 0

            # Calculate due date based on current time + entered time intervals
            due_date = get_current_time() + timedelta(days=days + (years * 365) + (months * 30), hours=hours, minutes=minutes)
            due_date_iso = due_date.isoformat()

            if task:
                task["name"] = task_name
                task["due_date"] = due_date_iso
            else:
                self.tasks.append({"name": task_name, "due_date": due_date_iso})

            save_tasks(self.tasks)
            dialog.destroy()
            self.update_task_display()

        action_button_text = "Save Task" if not task else "Update Task"
        save_button = tk.Button(dialog, text=action_button_text, command=save_task, bg="#4CAF50", fg="white", relief=tk.RAISED, padx=5, pady=5)
        save_button.pack(pady=10)

    def update_task_display(self):
        for widget in self.task_list_frame.winfo_children():
            widget.destroy()

        screen_width = self.root.winfo_screenwidth()
        task_frame_width = int(screen_width * 0.24)

        for idx, task in enumerate(self.tasks):
            frame = tk.Frame(self.task_list_frame, bd=2, relief=tk.RIDGE, bg="white", width=task_frame_width, height=100, padx=10, pady=5, highlightbackground="grey", highlightthickness=1)
            frame.pack_propagate(False)
            frame.pack(pady=(0, 10), padx=10)

            # Task Name
            task_name_label = tk.Label(frame, text=task["name"], font=("Arial", 10, "bold"), bg="white")
            task_name_label.pack(anchor="w", padx=5)

            # Countdown Timer Display
            countdown_label = tk.Label(frame, text="", font=("Arial", 14, "bold"), fg="black", bg="#f0f0f0", relief=tk.GROOVE, padx=10, pady=10)
            countdown_label.pack(fill=tk.BOTH, expand=True)
            countdown_label.config(highlightthickness=0, borderwidth=2)

            edit_button = tk.Button(frame, text="Edit", command=lambda t=task: self.show_task_dialog(t), bg="#2196F3", fg="white", font=("Arial", 8, "bold"), relief=tk.RAISED, padx=5, pady=5)
            edit_button.pack(side=tk.LEFT, padx=5)

            delete_button = tk.Button(frame, text="Delete", command=lambda t=task: self.delete_task(t), bg="#f44336", fg="white", font=("Arial", 8, "bold"), relief=tk.RAISED, padx=5, pady=5)
            delete_button.pack(side=tk.RIGHT, padx=5)

            self.update_timer(task, countdown_label)

    def delete_task(self, task):
        if messagebox.askyesno("Delete Task", f"Are you sure you want to delete the task '{task['name']}'?"):
            self.tasks.remove(task)
            save_tasks(self.tasks)
            self.update_task_display()

    def delete_completed_task(self, completed_task):
        if messagebox.askyesno("Delete Completed Task", f"Are you sure you want to delete the completed task '{completed_task['name']}'?"):
            self.completed_tasks.remove(completed_task)
            save_completed_tasks(self.completed_tasks)
            self.update_completed_task_display()

    def update_completed_task_display(self):
        for widget in self.completed_task_list_frame.winfo_children():
            if widget != self.completed_task_list_label:
                widget.destroy()

        for completed_task in self.completed_tasks:
            task_frame = tk.Frame(self.completed_task_list_frame, bg="lightgray", width=20, pady=2, padx=2)
            task_frame.pack(fill=tk.X, anchor="w", padx=5, pady=2)

            # Format and display the date in the label
            task_label = tk.Label(
                task_frame,
                text=f"{completed_task['name']}\n{datetime.strptime(completed_task['due_date'], '%Y-%m-%dT%H:%M:%S.%f%z').strftime('%d %b %Y, %I:%M %p')}",
                font=("Arial", 10),
                bg="lightgray"
            )
            task_label.pack(side=tk.LEFT, padx=5)

            delete_button = tk.Button(task_frame, text="Delete", command=lambda t=completed_task: self.delete_completed_task(t), bg="#f44336", fg="white", font=("Arial", 8, "bold"), relief=tk.RAISED, padx=5, pady=5)
            delete_button.pack(side=tk.RIGHT)

    def update_timer(self, task, countdown_label):
        try:
            # Check if the countdown label still exists in the widget hierarchy
            if not countdown_label.winfo_exists():
                print(f"Warning: Label for task '{task['name']}' no longer exists.")
                return

            due_date = datetime.fromisoformat(task["due_date"]).astimezone(timezone.utc)
            remaining_time = due_date - get_current_time()

            if remaining_time.total_seconds() <= 0:
                countdown_label.config(text="Time's Up!", fg="red")
                # Add the task to completed tasks if not already there
                if task not in self.completed_tasks:
                    self.completed_tasks.append(task)
                    if task in self.tasks:
                        self.tasks.remove(task)  # Remove from tasks
                    save_completed_tasks(self.completed_tasks)
                    save_tasks(self.tasks)
                    self.update_completed_task_display()
                    self.update_task_display()  # Ensure tasks are refreshed on display
            else:
                days = remaining_time.days
                hours, remainder = divmod(remaining_time.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                countdown_label.config(text=f"{days}d {hours}h {minutes}m {seconds}s")
                self.root.after(1000, lambda: self.update_timer(task, countdown_label))
        except Exception as e:
            print(f"Error updating timer for task: {task['name']}. Error: {str(e)}")


# App initialization
if __name__ == "__main__":
    root = tk.Tk()
    app = CountdownTaskManager(root)
    root.mainloop()
