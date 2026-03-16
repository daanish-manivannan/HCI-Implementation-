import customtkinter as ctk
import config
import threading

class SettingsDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("HCI System Settings")
        self.geometry("400x500")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.grid_columnconfigure(0, weight=1)
        
        # Title
        self.lbl_title = ctk.CTkLabel(self, text="Tracking Configuration", font=("Arial", 20, "bold"))
        self.lbl_title.grid(row=0, column=0, pady=(20, 10))

        # 1. Cursor Smoothing
        self._add_slider_control("Cursor Smoothing", getattr(config, 'CURSOR_SMOOTHING', 0.12), 0.01, 1.0, 1)
        
        # 2. X Sensitivity
        self._add_slider_control("Horizontal Micro-Sensitivity (X)", getattr(config, 'GAZE_SENSITIVITY_X', 8.0), 1.0, 20.0, 2)
        
        # 3. Y Sensitivity
        self._add_slider_control("Vertical Micro-Sensitivity (Y)", getattr(config, 'GAZE_SENSITIVITY_Y', 10.0), 1.0, 20.0, 3)

        # 4. Blink Threshold (EAR)
        self._add_slider_control("Blink Threshold (EAR)", getattr(config, 'EAR_THRESHOLD', 0.21), 0.15, 0.35, 4)
        
        self.btn_close = ctk.CTkButton(self, text="Close Panel", command=self.destroy)
        self.btn_close.grid(row=5, column=0, pady=30)
        
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _add_slider_control(self, label_text, initial_val, min_val, max_val, row):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=row, column=0, padx=20, pady=10, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)
        
        lbl = ctk.CTkLabel(frame, text=f"{label_text}: {initial_val:.2f}")
        lbl.grid(row=0, column=0, sticky="w")
        
        def on_slider_change(value):
            lbl.configure(text=f"{label_text}: {value:.2f}")
            self._update_config(label_text, value)
            
        slider = ctk.CTkSlider(frame, from_=min_val, to=max_val, command=on_slider_change)
        slider.set(initial_val)
        slider.grid(row=1, column=0, sticky="ew", pady=(5,0))

    def _update_config(self, label_text, value):
        if "Smoothing" in label_text:
            config.CURSOR_SMOOTHING = value
        elif "Horizontal" in label_text:
            config.GAZE_SENSITIVITY_X = value
        elif "Vertical" in label_text:
            config.GAZE_SENSITIVITY_Y = value
        elif "Blink" in label_text:
            config.EAR_THRESHOLD = value
            config.EAR_BLINK_THRESHOLD = value
            config.EAR_OPEN_THRESHOLD = value

        import json, os
        settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
        try:
            with open(settings_path, "w") as f:
                json.dump({
                    "CURSOR_SMOOTHING": config.CURSOR_SMOOTHING,
                    "GAZE_SENSITIVITY_X": config.GAZE_SENSITIVITY_X,
                    "GAZE_SENSITIVITY_Y": config.GAZE_SENSITIVITY_Y,
                    "EAR_THRESHOLD": config.EAR_THRESHOLD
                }, f)
        except Exception as e:
            print("Failed to save settings.json:", e)

def launch_dashboard():
    """Launch the dashboard in a separate process so it doesn't block the main loop."""
    import subprocess
    import sys
    import os
    script_path = os.path.abspath(__file__)
    subprocess.Popen([sys.executable, script_path])

if __name__ == "__main__":
    app = SettingsDashboard()
    app.mainloop()
