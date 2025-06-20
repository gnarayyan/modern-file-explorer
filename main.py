# 👇 Copy this entire script into a .py file and run it
# Required packages: customtkinter (pip install customtkinter)

import os
import shutil
import customtkinter as ctk
from tkinter import filedialog, messagebox, Menu
from pathlib import Path
import subprocess


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
        self.title("Enhanced Folder & File Explorer")
        self.geometry("900x600")

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.history = []
        self.forward_history = []
        self.current_path = Path.home() / "Downloads"

        nav_frame = ctk.CTkFrame(self)
        nav_frame.pack(pady=5, padx=10, fill="x")

        self.back_btn = ctk.CTkButton(
            nav_frame,
            text="← Back",
            command=self.go_back,
            width=60,
            font=("Consolas", 14),
        )
        self.forward_btn = ctk.CTkButton(
            nav_frame,
            text="→ Forward",
            command=self.go_forward,
            width=60,
            font=("Consolas", 14),
        )
        self.home_btn = ctk.CTkButton(
            nav_frame,
            text="🏠 Home",
            command=self.go_home,
            width=60,
            font=("Consolas", 14),
        )
        self.select_btn = ctk.CTkButton(
            nav_frame,
            text="📁 Browse",
            command=self.browse_folder,
            width=80,
            font=("Consolas", 14),
        )

        self.back_btn.pack(side="left", padx=5)
        self.forward_btn.pack(side="left", padx=5)
        self.home_btn.pack(side="left", padx=5)
        self.select_btn.pack(side="left", padx=5)

        self.file_list = ctk.CTkTextbox(self, font=("Consolas", 11), wrap="none")
        self.file_list.pack(expand=True, fill="both", padx=10, pady=5)
        self.file_list.bind("<Double-Button-1>", self.on_double_click)
        self.file_list.bind("<Button-3>", self.on_right_click)

        self.total_label = ctk.CTkLabel(
            self, text="Total: 0 B", font=("Segoe UI", 13, "bold")
        )
        self.total_label.pack(pady=5)
        # Context menu using standard tkinter
        self.context_menu = Menu(self, tearoff=0)
        self.context_menu.add_command(label="Open", command=self.open_selected)
        self.context_menu.add_command(
            label="Reveal in Explorer", command=self.reveal_selected
        )
        self.context_menu.add_command(label="Delete", command=self.delete_selected)

        # self.context_menu = ctk.CTkMenu(self, tearoff=0)
        # self.context_menu.add_command(label="Open", command=self.open_selected)
        # self.context_menu.add_command(
        #     label="Reveal in Explorer", command=self.reveal_selected
        # )
        # self.context_menu.add_command(label="Delete", command=self.delete_selected)

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
        self.file_list.delete("1.0", "end")
        total_size = 0

        try:
            for item in sorted(folder.iterdir(), key=lambda x: x.name.lower()):
                if item.is_dir():
                    size = get_folder_size(item)
                    total_size += size
                    line = f"📁 {item.name:<60} ({format_size(size)})\n"
                else:
                    size = item.stat().st_size
                    total_size += size
                    line = f"{get_emoji(item)} {item.name:<60} ({format_size(size)})\n"
                self.file_list.insert("end", line)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read folder:\n{e}")
            return

        self.total_label.configure(text=f"Total: {format_size(total_size)}")

    def on_double_click(self, event):
        try:
            index = self.file_list.index("@%d,%d linestart" % (event.x, event.y))
            line = self.file_list.get(index, f"{index} lineend").strip()
            name = line[2:].split(" (")[0].strip()
            target = self.current_path / name
            if target.is_dir():
                self.history.append(self.current_path)
                self.forward_history.clear()
                self.current_path = target
                self.load_folder(target)
        except:
            pass

    def on_right_click(self, event):
        try:
            self.file_list.tag_remove("sel", "1.0", "end")
            index = self.file_list.index("@%d,%d linestart" % (event.x, event.y))
            self.file_list.tag_add("sel", index, f"{index} lineend")
            self.selected_line = self.file_list.get(index, f"{index} lineend").strip()
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def get_selected_path(self):
        name = self.selected_line[2:].split(" (")[0].strip()
        return self.current_path / name

    def open_selected(self):
        path = self.get_selected_path()
        if path.is_file():
            os.startfile(path)
        elif path.is_dir():
            self.history.append(self.current_path)
            self.forward_history.clear()
            self.current_path = path
            self.load_folder(path)

    def reveal_selected(self):
        path = self.get_selected_path()
        if path.exists():
            reveal_in_explorer(str(path))

    def delete_selected(self):
        path = self.get_selected_path()
        confirm = messagebox.askyesno(
            "Confirm Delete", f"Are you sure you want to delete:\n{path.name}"
        )
        if confirm:
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                self.load_folder(self.current_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete:\n{e}")


if __name__ == "__main__":
    app = FileExplorerApp()
    app.mainloop()
