import json
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, simpledialog
from plyer import notification

# Load existing data or initialize a new data structure
def load_data():
    try:
        with open('data.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"expenses": []}

# Save data to JSON file
def save_data(data):
    with open('data.json', 'w') as file:
        json.dump(data, file)

# Clear data function
def clear_data():
    with open('data.json', 'w') as file:
        json.dump({"expenses": []}, file)
    messagebox.showinfo("Clear Data", "Data has been cleared!")

# Add an expense
def add_expense(amount, category, date=None):
    if amount is None or category is None:
        return  # Exit if input is None
    data = load_data()
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    data["expenses"].append({"amount": amount, "category": category, "date": date})
    save_data(data)
    check_notification_threshold(amount)

# Generate weekly report
def generate_weekly_report():
    data = load_data()
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    weekly_expenses = [expense for expense in data["expenses"] if datetime.strptime(expense["date"], "%Y-%m-%d") >= week_start]
    
    report = {}
    for expense in weekly_expenses:
        category = expense["category"]
        report[category] = report.get(category, 0) + expense["amount"]
    
    return report

# Function to show expense history
def show_expense_history():
    data = load_data()
    history = "\n".join(f"{expense['date']}: {expense['category']} - ${expense['amount']}" for expense in data["expenses"])
    messagebox.showinfo("Expense History", history if history else "No expenses recorded.")

# Function to open settings window
def load_settings():
    try:
        with open('settings.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "notifications_enabled": False,
            "deletion_frequency": "weekly",
            "threshold": 1000.0,
            "period": "weekly"
        }

def open_settings():
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    
    current_settings = load_settings()

    # Checkbox for notifications
    notifications_var = tk.BooleanVar(value=current_settings.get("notifications_enabled", False))
    tk.Checkbutton(settings_window, text="Enable Notifications", variable=notifications_var).pack()

    # Notification threshold settings
    tk.Label(settings_window, text="Notification Threshold:").pack()
    threshold_var = tk.DoubleVar(value=current_settings.get("threshold", 1000.0))
    tk.Entry(settings_window, textvariable=threshold_var).pack()

    tk.Label(settings_window, text="Time Period:").pack()
    period_var = tk.StringVar(value=current_settings.get("period", "weekly"))
    tk.Radiobutton(settings_window, text="Weekly", variable=period_var, value="weekly").pack()
    tk.Radiobutton(settings_window, text="Monthly", variable=period_var, value="monthly").pack()

    # Options for data deletion frequency
    tk.Label(settings_window, text="Delete Data Frequency:").pack()
    deletion_var = tk.StringVar(value=current_settings.get("deletion_frequency", "weekly"))
    tk.Radiobutton(settings_window, text="Weekly", variable=deletion_var, value="weekly").pack()
    tk.Radiobutton(settings_window, text="Daily", variable=deletion_var, value="daily").pack()
    tk.Radiobutton(settings_window, text="Monthly", variable=deletion_var, value="monthly").pack()
    tk.Radiobutton(settings_window, text="Yearly", variable=deletion_var, value="yearly").pack()

    tk.Button(settings_window, text="Save", command=lambda: save_settings(
        notifications_var.get(), 
        deletion_var.get(),
        threshold_var.get(),
        period_var.get()
    )).pack()
    tk.Button(settings_window, text="Clear Data", command=clear_data).pack()
    
# Function to save settings
def save_settings(notifications_enabled, deletion_frequency, threshold=None, period=None):
    settings = {
        "notifications_enabled": notifications_enabled,
        "deletion_frequency": deletion_frequency,
        "threshold": threshold,
        "period": period
    }
    with open('settings.json', 'w') as f:
        json.dump(settings, f)
    messagebox.showinfo("Settings", "Settings saved successfully!")

# Main function to run the app
def check_notification_threshold(new_amount):
    try:
        with open('settings.json', 'r') as f:
            settings = json.load(f)
            if not settings.get('notifications_enabled', False):
                return

            threshold = settings.get('threshold', 1000.0)
            period = settings.get('period', 'weekly')
            
            data = load_data()
            today = datetime.now()
            
            if period == 'weekly':
                start_date = today - timedelta(days=today.weekday())
            else:  # monthly
                start_date = today.replace(day=1)
                
            period_expenses = [expense for expense in data["expenses"] 
                             if datetime.strptime(expense["date"], "%Y-%m-%d") >= start_date]
            total = sum(expense['amount'] for expense in period_expenses) + new_amount
            
            if total >= threshold:
                notification.notify(
                    title="Expense Alert",
                    message=f"You've reached your {period} spending limit of ${threshold}",
                    timeout=10
                )
    except Exception as e:
        print(f"Error checking notifications: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Expenses Tracker")

    tk.Label(root, text="Expenses Tracker!").pack()

    tk.Button(root, text="Add Expense", command=lambda: add_expense(float(simpledialog.askstring("Input", "Enter amount:") or 0), simpledialog.askstring("Input", "Enter category:"))).pack()
    tk.Button(root, text="View Expenses", command=show_expense_history).pack()
    tk.Button(root, text="Generate Report", command=lambda: messagebox.showinfo("Weekly Report", generate_weekly_report())).pack()
    tk.Button(root, text="Settings", command=open_settings).pack()
    tk.Button(root, text="Exit", command=root.quit).pack()

    root.mainloop()
