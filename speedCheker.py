import customtkinter as ctk
import speedtest
import threading
import json  # We'll use JSON to store history
import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- History File ---
HISTORY_FILE = "speed_history.json"


class HistoryWindow(ctk.CTkToplevel):
    """
    A new window to display the speed test history graph.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Speed Test History")
        self.geometry("600x400")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Load history data
        history = self.load_history()

        # --- Prepare data for plotting ---
        # Get the last 10 test results
        recent_tests = history[-10:]
        timestamps = [test['timestamp'] for test in recent_tests]
        downloads = [test['download'] for test in recent_tests]
        uploads = [test['upload'] for test in recent_tests]

        # --- Create Matplotlib Figure ---
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)

        ax.plot(timestamps, downloads, 'o-', label='Download (Mbps)')
        ax.plot(timestamps, uploads, 's-', label='Upload (Mbps)')

        ax.set_title("Recent Speed Tests")
        ax.set_ylabel("Speed (Mbps)")
        ax.set_xlabel("Test Time")
        ax.legend()
        fig.autofmt_xdate()  # Automatically format dates nicely

        # --- Embed the graph in the Tkinter window ---
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    def load_history(self):
        if not os.path.exists(HISTORY_FILE):
            return []
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []


class SpeedTestApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Modern Wi-Fi Speed Tester")
        self.geometry("500x400")  # Made window a bit taller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Frame
        self.grid_rowconfigure(1, weight=0)  # Progress
        self.grid_rowconfigure(2, weight=0)  # Button

        # --- Create a Frame for controls ---
        self.control_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.control_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.control_frame.grid_columnconfigure((0, 1), weight=1)

        # --- Theme Switcher ---
        self.theme_menu = ctk.CTkOptionMenu(
            self.control_frame,
            values=["System", "Light", "Dark"],
            command=self.change_appearance_mode
        )
        self.theme_menu.grid(row=0, column=0, padx=10, sticky="w")

        # --- History Button ---
        self.history_button = ctk.CTkButton(
            self.control_frame,
            text="Show History",
            command=self.open_history_window
        )
        self.history_button.grid(row=0, column=1, padx=10, sticky="e")

        self.history_win = None  # To hold the history window

        # ... (Rest of the __init__ code from the previous example) ...
        # (Ping, Download, Upload frames, Progress Bar, Start Button)

        # --- Create a Frame for the Results ---
        self.results_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.results_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.results_frame.grid_columnconfigure((0, 1, 2), weight=1)  # 3 columns

        # --- 1. Ping Result "Card" ---
        self.ping_frame = ctk.CTkFrame(self.results_frame)
        self.ping_frame.grid(row=0, column=0, padx=10, sticky="ew")
        self.ping_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.ping_frame, text="Ping 📍", font=("Arial", 16)).grid(row=0, column=0, pady=(10, 5))
        self.ping_label = ctk.CTkLabel(self.ping_frame, text="-- ms", font=("Arial", 24, "bold"))
        self.ping_label.grid(row=1, column=0, pady=(5, 10))

        # --- 2. Download Result "Card" ---
        self.download_frame = ctk.CTkFrame(self.results_frame)
        self.download_frame.grid(row=0, column=1, padx=10, sticky="ew")
        self.download_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.download_frame, text="Download ⬇️", font=("Arial", 16)).grid(row=0, column=0, pady=(10, 5))
        self.download_label = ctk.CTkLabel(self.download_frame, text="-- Mbps", font=("Arial", 24, "bold"))
        self.download_label.grid(row=1, column=0, pady=(5, 10))

        # --- 3. Upload Result "Card" ---
        self.upload_frame = ctk.CTkFrame(self.results_frame)
        self.upload_frame.grid(row=0, column=2, padx=10, sticky="ew")
        self.upload_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.upload_frame, text="Upload ⬆️", font=("Arial", 16)).grid(row=0, column=0, pady=(10, 5))
        self.upload_label = ctk.CTkLabel(self.upload_frame, text="-- Mbps", font=("Arial", 24, "bold"))
        self.upload_label.grid(row=1, column=0, pady=(5, 10))

        # --- Progress Bar (initially hidden) ---
        self.progress_bar = ctk.CTkProgressBar(self, mode='indeterminate')

        # --- Start Button ---
        self.start_button = ctk.CTkButton(
            self,
            text="Run Speed Test",
            font=("Arial", 18, "bold"),
            command=self.start_test_thread,
            fg_color="#0088CC",
            hover_color="#00AADD"
        )
        self.start_button.grid(row=2, column=0, padx=20, pady=20, ipady=10, sticky="ew")

    def change_appearance_mode(self, new_mode):
        ctk.set_appearance_mode(new_mode)

    def open_history_window(self):
        if self.history_win is None or not self.history_win.winfo_exists():
            self.history_win = HistoryWindow(self)  # create window if its None or destroyed
        else:
            self.history_win.focus()  # if window exists focus it

    # --- Function to save results ---
    def save_result(self, ping, download, upload):
        history = self.load_history()

        new_result = {
            "timestamp": ctk.datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "ping": ping,
            "download": download,
            "upload": upload
        }
        history.append(new_result)

        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)

    def load_history(self):
        if not os.path.exists(HISTORY_FILE):
            return []
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def start_test_thread(self):
        self.start_button.configure(text="Running Test...", state="disabled")
        self.history_button.configure(state="disabled")  # Disable history button too

        self.ping_label.configure(text="-- ms")
        self.download_label.configure(text="-- Mbps")
        self.upload_label.configure(text="-- Mbps")

        self.progress_bar.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.progress_bar.start()

        test_thread = threading.Thread(target=self.run_speed_test)
        test_thread.start()

    def run_speed_test(self):
        try:
            s = speedtest.Speedtest()
            s.get_best_server()
            s.download()
            s.upload()
            results = s.results.dict()

            ping = results["ping"]
            download_speed = results["download"] / 1_000_000
            upload_speed = results["upload"] / 1_000_000

            self.ping_label.configure(text=f"{ping:.0f} ms")
            self.download_label.configure(text=f"{download_speed:.2f} Mbps")
            self.upload_label.configure(text=f"{upload_speed:.2f} Mbps")

            # Save the result
            self.save_result(ping, download_speed, upload_speed)

        except speedtest.SpeedtestException as e:
            self.download_label.configure(text="Error")
            print(f"Speed test error: {e}")

        finally:
            self.progress_bar.stop()
            self.progress_bar.grid_forget()

            self.start_button.configure(text="Run Speed Test", state="normal")
            self.history_button.configure(state="normal")  # Re-enable history button


# --- Run the Application ---
if __name__ == "__main__":
    app = SpeedTestApp()
    app.mainloop()