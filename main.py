import os
import shutil
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
import subprocess

from improvements.folder_size import get_folder_size_optimized

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
        self.view_mode = "grid"

        self.folder_color = "#324b5e"
        self.file_color = "#2d2d2d"
        self.highlight_color = "#1f6aa5"

        self.sort_by = "size"
        self.sort_order = "desc"

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
        self.toggle_btn = ctk.CTkButton(
            nav_frame, text="🗂️ Toggle View", command=self.toggle_view, width=120
        )

        self.back_btn.pack(side="left", padx=5)
        self.forward_btn.pack(side="left", padx=5)
        self.home_btn.pack(side="left", padx=5)
        self.select_btn.pack(side="left", padx=5)
        self.toggle_btn.pack(side="left", padx=5)

        self.sort_option = ctk.CTkOptionMenu(
            nav_frame,
            values=["name", "size"],
            command=self.change_sort_option,
            width=100,
        )
        self.sort_option.set("name")
        self.sort_option.pack(side="left", padx=5)

        self.sort_order_btn = ctk.CTkButton(
            nav_frame, text="⬇ Asc", width=60, command=self.toggle_sort_order
        )
        self.sort_order_btn.pack(side="left", padx=5)

        self.progress_bar = ctk.CTkProgressBar(self, width=500)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=3)

        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="Contents")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.total_label = ctk.CTkLabel(
            self, text="Total: 0 B", font=("Segoe UI", 14, "bold")
        )
        self.total_label.pack(pady=5)

        self.load_folder_async(self.current_path)

    def toggle_view(self):
        self.view_mode = "grid" if self.view_mode == "list" else "list"
        self.load_folder_async(self.current_path)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.forward_history.clear()
            self.history.append(self.current_path)
            self.current_path = Path(folder)
            self.load_folder_async(self.current_path)

    def go_back(self):
        if self.history:
            self.forward_history.append(self.current_path)
            self.current_path = self.history.pop()
            self.load_folder_async(self.current_path)

    def go_forward(self):
        if self.forward_history:
            self.history.append(self.current_path)
            self.current_path = self.forward_history.pop()
            self.load_folder_async(self.current_path)

    def go_home(self):
        self.forward_history.clear()
        self.history.append(self.current_path)
        self.current_path = Path.home() / "Downloads"
        self.load_folder_async(self.current_path)

    def change_sort_option(self, value):
        self.sort_by = value
        self.load_folder_async(self.current_path)

    def toggle_sort_order(self):
        self.sort_order = "desc" if self.sort_order == "asc" else "asc"
        arrow = "⬆ Desc" if self.sort_order == "desc" else "⬇ Asc"
        self.sort_order_btn.configure(text=arrow)
        self.load_folder_async(self.current_path)

    def load_folder_async(self, folder):
        self.progress_bar.set(0)
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        threading.Thread(
            target=self._load_folder_thread, args=(folder,), daemon=True
        ).start()

    def _load_folder_thread(self, folder):
        total_size = 0
        items_data = []

        try:
            items = list(folder.iterdir())
            total_items = len(items)

            def get_sort_key(item):
                if self.sort_by == "size":
                    return (
                        get_folder_size_optimized(item)
                        if item.is_dir()
                        else item.stat().st_size
                    )
                else:
                    return item.name.lower()

            items.sort(key=get_sort_key, reverse=(self.sort_order == "desc"))

            for index, item in enumerate(items):
                if item.is_dir():
                    size = get_folder_size_optimized(item)
                    total_size += size
                    items_data.append(("folder", item, size))
                else:
                    size = item.stat().st_size
                    total_size += size
                    items_data.append(("file", item, size))

                if total_items > 0 and (index % 2 == 0 or index == total_items - 1):
                    progress = (index + 1) / total_items
                    self.after(0, lambda p=progress: self.progress_bar.set(p))

        except Exception as e:
            self.after(
                0, lambda: messagebox.showerror("Error", f"Cannot open folder:\n{e}")
            )
            return

        self.after(
            0, lambda: self._update_ui_with_items(folder, items_data, total_size)
        )

    def _update_ui_with_items(self, folder, items_data, total_size):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        row, col = 0, 0
        for kind, item, size in items_data:
            if kind == "folder":
                label = f"📁 {item.name}\n{format_size(size)}"
                btn = ctk.CTkButton(
                    self.scroll_frame,
                    text=label,
                    anchor="center",
                    fg_color=self.folder_color,
                    hover_color="#3a5a72",
                    command=lambda p=item: self.open_folder(p),
                    corner_radius=8,
                    font=("Consolas", 14),
                    height=70,
                    width=200,
                )
                btn.bind("<Button-1>", lambda e, b=btn: self.select_item(b))
                widget = btn
            else:
                label = f"{get_emoji(item)} {item.name}\n{format_size(size)}"
                lbl = ctk.CTkLabel(
                    self.scroll_frame,
                    text=label,
                    anchor="center",
                    fg_color=self.file_color,
                    text_color="#dcdcdc",
                    font=("Consolas", 14),
                    corner_radius=8,
                    height=70,
                    width=200,
                )
                lbl.bind("<Button-1>", lambda e, l=lbl: self.select_item(l))
                widget = lbl

            if self.view_mode == "grid":
                widget.grid(row=row, column=col, padx=8, pady=8)
                col += 1
                if col >= 4:
                    col = 0
                    row += 1
            else:
                widget.pack(fill="x", padx=5, pady=3)

        self.total_label.configure(text=f"Total: {format_size(total_size)}")
        self.progress_bar.set(0)

    def open_folder(self, path):
        self.history.append(self.current_path)
        self.forward_history.clear()
        self.current_path = path
        self.load_folder_async(path)

    def select_item(self, widget):
        if self.selected_widget:
            prev_color = (
                self.folder_color
                if isinstance(self.selected_widget, ctk.CTkButton)
                else self.file_color
            )
            self.selected_widget.configure(fg_color=prev_color)
        widget.configure(fg_color=self.highlight_color)
        self.selected_widget = widget


if __name__ == "__main__":
    app = FileExplorerApp()
    app.mainloop()
