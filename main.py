import os
import shutil
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
import subprocess

# Initialize customtkinter
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


def format_size(size_bytes):
    if size_bytes >= 1 << 30:
        return f"{size_bytes / (1 << 30):.2f} GB"
    elif size_bytes >= 1 << 20:
        return f"{size_bytes / (1 << 20):.2f} MB"
    elif size_bytes >= 1 << 10:
        return f"{size_bytes / (1 << 10):.2f} KB"
    else:
        return f"{size_bytes} B"


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


def get_folder_size(path):
    total = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total += os.path.getsize(fp)
    return total


def reveal_in_explorer(path):
    subprocess.run(['explorer', '/select,', os.path.normpath(path)])


class FileExplorerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Modern File Explorer")
        self.geometry("1000x700")

        self.history = []
        self.forward_history = []
        self.current_path = Path.home() / "Downloads" / "8th Sem"
        self.selected_widget = None

        # Navigation bar
        nav_frame = ctk.CTkFrame(self)
        nav_frame.pack(pady=5, padx=10, fill="x")

        self.back_btn = ctk.CTkButton(
            nav_frame, text="← Back", command=self.go_back, width=60
        )
        self.forward_btn = ctk.CTkButton(
            nav_frame, text="→ Forward", command=self.go_forward, width=60
        )
        self.home_btn = ctk.CTkButton(
            nav_frame, text="🏠 Home", command=self.go_home, width=60
        )
        self.select_btn = ctk.CTkButton(
            nav_frame, text="📁 Browse", command=self.browse_folder, width=80
        )

        self.back_btn.pack(side="left", padx=5)
        self.forward_btn.pack(side="left", padx=5)
        self.home_btn.pack(side="left", padx=5)
        self.select_btn.pack(side="left", padx=5)

        # Scrollable content area
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Contents")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Total size label
        self.total_label = ctk.CTkLabel(
            self, text="Total: 0 B", font=("Segoe UI", 14, "bold")
        )
        self.total_label.pack(pady=5)

        # Initial load
        self.load_folder(self.current_path)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.forward_history.clear()
            self.history.append(self.current_path)
            self.current_path = Path(folder)
            self.load_folder(self.current_path)

    def go_back(self):
        if self.history:
            self.forward_history.append(self.current_path)
            self.current_path = self.history.pop()
            self.load_folder(self.current_path)

    def go_forward(self):
        if self.forward_history:
            self.history.append(self.current_path)
            self.current_path = self.forward_history.pop()
            self.load_folder(self.current_path)

    def go_home(self):
        self.forward_history.clear()
        self.history.append(self.current_path)
        self.current_path = Path.home() / "Downloads"
        self.load_folder(self.current_path)

    def load_folder(self, folder):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        total_size = 0

        try:
            for item in sorted(folder.iterdir(), key=lambda x: x.name.lower()):
                if item.is_dir():
                    size = get_folder_size(item)
                    total_size += size
                    label = f"📁 {item.name} ({format_size(size)})"
                    btn = ctk.CTkButton(
                        self.scroll_frame,
                        text=label,
                        anchor="w",
                        command=lambda p=item: self.open_folder(p),
                    )
                    btn.pack(fill="x", padx=5, pady=2)
                    btn.bind("<Button-1>", lambda e, b=btn: self.select_item(b))
                else:
                    size = item.stat().st_size
                    total_size += size
                    label = f"{get_emoji(item)} {item.name} ({format_size(size)})"
                    lbl = ctk.CTkLabel(self.scroll_frame, text=label, anchor="w")
                    lbl.pack(fill="x", padx=5, pady=2)
                    lbl.bind("<Button-1>", lambda e, l=lbl: self.select_item(l))
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open folder:\n{e}")
            return

        self.total_label.configure(text=f"Total: {format_size(total_size)}")

    def open_folder(self, path):
        self.history.append(self.current_path)
        self.forward_history.clear()
        self.current_path = path
        self.load_folder(path)

    def select_item(self, widget):
        if self.selected_widget:
            self.selected_widget.configure(fg_color="transparent")
        widget.configure(fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        self.selected_widget = widget


if __name__ == "__main__":
    app = FileExplorerApp()
    app.mainloop()
