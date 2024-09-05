import customtkinter as ctk
import csv
from datetime import datetime
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class TimeTrackingApp(ctk.CTk):
    def __init__(self):
        # Initialize csv_file first
        self.csv_file = "time_tracking_data.csv"

        super().__init__()

        self.title("Time Tracking App")
        self.geometry("600x400")

        # Create tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both", padx=10, pady=10)

        self.tab_add = self.tabview.add("Add Task")
        self.tab_track = self.tabview.add("Track Time")
        self.tab_progress = self.tabview.add("View Progress")

        self.setup_add_tab()
        self.setup_track_tab()
        self.setup_progress_tab()

        # Ensure CSV file exists
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Task", "Date", "Duration"])

        # Initialize timer_job
        self.timer_job = None

        # Bind the close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_add_tab(self):
        label = ctk.CTkLabel(self.tab_add, text="Add a new task:")
        label.pack(pady=10)

        self.task_entry = ctk.CTkEntry(self.tab_add, width=200)
        self.task_entry.pack(pady=10)

        add_button = ctk.CTkButton(self.tab_add, text="Add Task", command=self.add_task)
        add_button.pack(pady=10)

    def setup_track_tab(self):
        label = ctk.CTkLabel(self.tab_track, text="Select a task to track:")
        label.pack(pady=10)

        self.task_var = ctk.StringVar()
        self.task_dropdown = ctk.CTkOptionMenu(self.tab_track, variable=self.task_var)
        self.task_dropdown.pack(pady=10)

        self.update_task_dropdown()

        self.start_button = ctk.CTkButton(self.tab_track, text="Start", command=self.start_timer)
        self.start_button.pack(pady=10)

        self.stop_button = ctk.CTkButton(self.tab_track, text="Stop", command=self.stop_timer, state="disabled")
        self.stop_button.pack(pady=10)

        self.timer_label = ctk.CTkLabel(self.tab_track, text="00:00:00")
        self.timer_label.pack(pady=10)

    def setup_progress_tab(self):
        label = ctk.CTkLabel(self.tab_progress, text="Select a task to view progress:")
        label.pack(pady=10)

        self.progress_task_var = ctk.StringVar()
        self.progress_task_dropdown = ctk.CTkOptionMenu(self.tab_progress, variable=self.progress_task_var, command=self.update_progress_chart)
        self.progress_task_dropdown.pack(pady=10)

        self.update_progress_task_dropdown()

        self.chart_frame = ctk.CTkFrame(self.tab_progress)
        self.chart_frame.pack(expand=True, fill="both", padx=10, pady=10)

    def add_task(self):
        task = self.task_entry.get()
        if task:
            with open(self.csv_file, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([task, "", ""])
            self.task_entry.delete(0, 'end')
            self.update_task_dropdown()
            self.update_progress_task_dropdown()

    def update_task_dropdown(self):
        tasks = self.get_unique_tasks()
        self.task_dropdown.configure(values=tasks)
        if tasks:
            self.task_dropdown.set(tasks[0])

    def update_progress_task_dropdown(self):
        tasks = self.get_unique_tasks()
        self.progress_task_dropdown.configure(values=tasks)
        if tasks:
            self.progress_task_dropdown.set(tasks[0])

    def get_unique_tasks(self):
        tasks = set()
        
        # Check if the file exists before trying to read it
        if os.path.exists(self.csv_file):
            with open(self.csv_file, 'r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    if row:
                        tasks.add(row[0])
        return list(tasks)

    def start_timer(self):
        self.start_time = datetime.now()
        self.update_timer()
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")

    def stop_timer(self):
        self.after_cancel(self.timer_job)
        duration = datetime.now() - self.start_time
        task = self.task_var.get()
        with open(self.csv_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([task, self.start_time.date(), duration.total_seconds()])
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.timer_label.configure(text="00:00:00")

    def on_closing(self):
        # Cancel any ongoing timer jobs
        if self.timer_job:
            self.after_cancel(self.timer_job)

        # Close any open matplotlib figures
        plt.close('all')

        # Destroy the main window
        self.destroy()

    def update_timer(self):
        duration = datetime.now() - self.start_time
        self.timer_label.configure(text=str(duration).split('.')[0])
        self.timer_job = self.after(1000, self.update_timer)

    def update_progress_chart(self, task):
        # Clear the chart frame
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # Get task data (only durations)
        _, durations = self.get_task_data(task)
        
        # If no data, do not proceed with plotting
        if not durations:
            return
        
        # Create a sequence of numbers for the x-axis (1st task, 2nd task, etc.)
        task_occurrences = list(range(1, len(durations) + 1))

        # Plot durations against task occurrences
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.plot(task_occurrences, durations, marker='o', linestyle='-', color='b')
        ax.set_title(f"Progress for {task}")
        ax.set_xlabel("Task Occurrence")
        ax.set_ylabel("Duration (seconds)")
        plt.tight_layout()

        # Display the chart in the chart frame
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both")

    def get_task_data(self, task):
        dates = []
        durations = []
        
        with open(self.csv_file, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                if row and row[0] == task:
                    # Check if the date and duration fields are not empty
                    if row[1] and row[2]:
                        try:
                            dates.append(datetime.strptime(row[1], "%Y-%m-%d").date())
                            durations.append(float(row[2]))
                        except ValueError as e:
                            print(f"Error parsing row: {row} - {e}")
        return dates, durations

if __name__ == "__main__":
    app = TimeTrackingApp()
    app.mainloop()