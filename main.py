import os
import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path

# Set appearance
ctk.set_appearance_mode("System")  # Options: "Dark", "Light", "System"
ctk.set_default_color_theme("blue")


# Format size (B, KB, MB, GB)
def format_size(size_bytes):
    if size_bytes >= 1 << 30:
        return f"{size_bytes / (1 << 30):.2f} GB"
    elif size_bytes >= 1 << 20:
        return f"{size_bytes / (1 << 20):.2f} MB"
    elif size_bytes >= 1 << 10:
        return f"{size_bytes / (1 << 10):.2f} KB"
    else:
        return f"{size_bytes} B"


# Emoji by file extension
def get_emoji(file):
    ext = file.suffix.lower()
    if ext in ['.mp3', '.wav', '.flac']:
        return "🎵"
    elif ext in ['.doc', '.docx', '.txt', '.pdf', '.xls']:
        return "📄"
    elif ext in ['.jpg', '.jpeg', '.png', '.gif']:
        return "🖼️"
    elif ext in ['.zip', '.rar', '.7z']:
        return "🗜️"
    else:
        return "📄"


# Get size of folder recursively
def get_folder_size(path):
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total += os.path.getsize(fp)
    return total


# App class
class FileExplorerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Modern Folder & File Explorer")
        self.geometry("800x600")

        # Button
        self.select_btn = ctk.CTkButton(
            self, text="Browse Folder", command=self.browse_folder
        )
        self.select_btn.pack(pady=10)

        # Text area
        self.textbox = ctk.CTkTextbox(self, font=("Consolas", 16), wrap="none")
        self.textbox.pack(expand=True, fill="both", padx=10, pady=10)

        # Total label
        self.total_label = ctk.CTkLabel(
            self, text="Total: 0 B", font=("Segoe UI", 14, "bold")
        )
        self.total_label.pack(pady=5)

    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return

        self.textbox.delete("1.0", "end")
        total_size = 0

        folder = Path(folder_path)
        for item in folder.iterdir():
            if item.is_dir():
                size = get_folder_size(item)
                total_size += size
                line = f"📁 {item.name:<40} ({format_size(size)})\n"
            else:
                size = item.stat().st_size
                total_size += size
                line = f"{get_emoji(item)} {item.name:<40} ({format_size(size)})\n"
            self.textbox.insert("end", line)

        self.total_label.configure(text=f"Total: {format_size(total_size)}")


# Run the app
if __name__ == "__main__":
    app = FileExplorerApp()
    app.mainloop()
