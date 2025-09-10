import tkinter as tk
from tkinter import messagebox
import random

# -----------------------------
# Smart Trash Bin Simulator
# -----------------------------
class SmartTrashBinApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Trash Bin 🗑️")
        self.root.geometry("600x400")

        # Trash bin levels (in %)
        self.bin_levels = {
            "Bin 1": 20,
            "Bin 2": 35,
            "Bin 3": 10
        }

        # Title
        self.title_label = tk.Label(root, text="Smart Trash Bin Monitor", font=("Arial", 18, "bold"))
        self.title_label.pack(pady=10)

        # Frame for bins
        self.bins_frame = tk.Frame(root)
        self.bins_frame.pack(pady=10)

        self.bin_labels = {}
        for i, bin_name in enumerate(self.bin_levels.keys()):
            label = tk.Label(self.bins_frame, text=f"{bin_name}: {self.bin_levels[bin_name]}%", font=("Arial", 14))
            label.grid(row=i, column=0, padx=20, pady=5, sticky="w")
            self.bin_labels[bin_name] = label

            # Empty button
            empty_button = tk.Button(self.bins_frame, text=f"Empty {bin_name}", command=lambda b=bin_name: self.empty_bin(b))
            empty_button.grid(row=i, column=1, padx=10)

        # Simulate button
        self.sim_button = tk.Button(root, text="Simulate Fill", command=self.simulate_fill, bg="lightblue")
        self.sim_button.pack(pady=15)

        # Exit button
        self.exit_button = tk.Button(root, text="Exit", command=root.quit, bg="red", fg="white")
        self.exit_button.pack(pady=5)

        # Status label
        self.status_label = tk.Label(root, text="System running normally ✅", font=("Arial", 12), fg="green")
        self.status_label.pack(pady=10)

    def update_labels(self):
        """Update bin labels with current levels"""
        for bin_name, level in self.bin_levels.items():
            self.bin_labels[bin_name].config(text=f"{bin_name}: {level}%")
            if level >= 80:
                self.bin_labels[bin_name].config(fg="red")
            else:
                self.bin_labels[bin_name].config(fg="black")

    def simulate_fill(self):
        """Randomly increase bin levels"""
        for bin_name in self.bin_levels.keys():
            self.bin_levels[bin_name] += random.randint(5, 20)
            if self.bin_levels[bin_name] > 100:
                self.bin_levels[bin_name] = 100

        self.update_labels()
        self.check_alerts()

    def empty_bin(self, bin_name):
        """Empty a specific bin"""
        self.bin_levels[bin_name] = 0
        self.update_labels()
        self.status_label.config(text=f"{bin_name} emptied 🧹", fg="blue")

    def check_alerts(self):
        """Check if any bin is full and alert"""
        full_bins = [b for b, lvl in self.bin_levels.items() if lvl >= 80]
        if full_bins:
            msg = f"⚠️ ALERT: {', '.join(full_bins)} need emptying!"
            self.status_label.config(text=msg, fg="red")
            messagebox.showwarning("Bin Alert", msg)
        else:
            self.status_label.config(text="System running normally ✅", fg="green")


# -----------------------------
# Run the App
# -----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = SmartTrashBinApp(root)
    root.mainloop()
