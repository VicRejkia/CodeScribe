import os
import sys
import json
import ast
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import ctypes
from ctypes import wintypes
from collections import defaultdict

def get_long_path_name(short_path):
    if sys.platform != 'win32':
        return short_path
    try:
        _GetLongPathNameW = ctypes.windll.kernel32.GetLongPathNameW
        _GetLongPathNameW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
        _GetLongPathNameW.restype = wintypes.DWORD
        buffer_size = _GetLongPathNameW(short_path, None, 0)
        if buffer_size == 0: return short_path
        long_path_buffer = ctypes.create_unicode_buffer(buffer_size)
        result = _GetLongPathNameW(short_path, long_path_buffer, buffer_size)
        if result == 0: return short_path
        return long_path_buffer.value
    except Exception:
        return short_path

class SettingsManager:
    def __init__(self, filename="settings.json"):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.filename = os.path.join(script_dir, filename)
        self.settings = {}
        self.load_settings()

    def _create_default_settings(self):
        return {
            "extension_map": {
                ".py": "python", ".sql": "sql", ".js": "javascript",
                ".html": "html", ".css": "css", ".json": "json",
                ".md": "markdown", ".txt": "text", ".yml": "yaml",
                ".yaml": "yaml", ".toml": "toml", ".ini": "ini",
                ".sh": "bash", ".bat": "batch", ".dockerfile": "dockerfile"
            },
            "exclude_list": [
                "__pycache__", ".git", ".vscode", "node_modules", "venv", ".env"
            ],
            "exclude_dotfiles": True
        }

    def load_settings(self):
        try:
            with open(self.filename, 'r') as f: self.settings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.settings = self._create_default_settings()
            self.save_settings()

    def save_settings(self):
        try:
            with open(self.filename, 'w') as f: json.dump(self.settings, f, indent=4)
        except IOError as e:
            messagebox.showerror("Settings Error", f"Could not save settings: {e}")

    def get(self, key): return self.settings.get(key)
    def set(self, key, value): self.settings[key] = value

class SettingsWindow(tk.Toplevel):
    # This class remains unchanged from the previous version
    def __init__(self, parent, settings_manager, on_close_callback):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.on_close_callback = on_close_callback
        self.title("Settings"); self.transient(parent); self.grab_set()
        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10"); main_frame.pack(fill=tk.BOTH, expand=True)
        exclude_frame = ttk.LabelFrame(main_frame, text="Exclusion Filters", padding="10"); exclude_frame.pack(fill=tk.X, expand=True, pady=5)
        ttk.Label(exclude_frame, text="Exclude files/folders by name (one per line):").pack(anchor=tk.W)
        self.exclude_text = tk.Text(exclude_frame, height=8, width=50); self.exclude_text.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        self.exclude_text.insert("1.0", "\n".join(self.settings_manager.get("exclude_list")))
        self.exclude_dotfiles_var = tk.BooleanVar(value=self.settings_manager.get("exclude_dotfiles"))
        ttk.Checkbutton(exclude_frame, text="Exclude all files and folders starting with '.'", variable=self.exclude_dotfiles_var).pack(anchor=tk.W)
        ext_frame = ttk.LabelFrame(main_frame, text="File Type Mappings", padding="10"); ext_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        ttk.Label(ext_frame, text="Map extensions to Markdown language identifiers:").pack(anchor=tk.W)
        self.ext_map_text = tk.Text(ext_frame, height=10, width=50); self.ext_map_text.pack(fill=tk.BOTH, expand=True)
        self.ext_map_text.insert("1.0", json.dumps(self.settings_manager.get("extension_map"), indent=4))
        button_frame = ttk.Frame(main_frame); button_frame.pack(fill=tk.X, pady=10)
        ttk.Button(button_frame, text="Save & Close", command=self.save_and_close).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT)

    def save_and_close(self):
        exclude_list = self.exclude_text.get("1.0", tk.END).strip().split("\n")
        self.settings_manager.set("exclude_list", [item.strip() for item in exclude_list if item.strip()])
        self.settings_manager.set("exclude_dotfiles", self.exclude_dotfiles_var.get())
        ext_map_str = self.ext_map_text.get("1.0", tk.END)
        try:
            new_ext_map = ast.literal_eval(ext_map_str)
            if not isinstance(new_ext_map, dict): raise ValueError("Input is not a valid dictionary.")
            self.settings_manager.set("extension_map", new_ext_map)
        except (ValueError, SyntaxError) as e:
            messagebox.showerror("Invalid Format", f"File type mapping is not a valid Python dictionary.\nError: {e}", parent=self)
            return
        self.settings_manager.save_settings()
        self.on_close_callback()
        self.destroy()

class ProjectDocumenter:
    def __init__(self, root):
        self.root = root; self.root.title("Project Documenter"); self.root.geometry("800x650")
        self.settings_manager = SettingsManager(); self.project_path = ""; self.file_states = {}
        self.create_ui()

    def create_ui(self):
        top_frame = ttk.Frame(self.root); top_frame.pack(pady=10, padx=10, fill=tk.X)
        self.select_btn = ttk.Button(top_frame, text="Select Project Folder", command=self.select_folder_dialog); self.select_btn.pack(side=tk.LEFT, padx=5)
        self.generate_btn = ttk.Button(top_frame, text="Generate Documentation", command=self.generate_markdown, state=tk.DISABLED); self.generate_btn.pack(side=tk.LEFT, padx=5)
        self.settings_btn = ttk.Button(top_frame, text="Settings", command=self.open_settings); self.settings_btn.pack(side=tk.RIGHT, padx=5)
        
        tree_frame = ttk.Frame(self.root); tree_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(tree_frame); self.tree["columns"] = ("path", "type")
        self.tree.column("#0", width=300, anchor=tk.W); self.tree.column("path", width=350, anchor=tk.W); self.tree.column("type", width=100, anchor=tk.W)
        self.tree.heading("#0", text="Name", anchor=tk.W); self.tree.heading("path", text="Path", anchor=tk.W); self.tree.heading("type", text="Type", anchor=tk.W)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview); self.tree.configure(yscrollcommand=vsb.set); vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<Button-1>", self.handle_tree_click)

        # Status Bar for Token Count
        status_bar = ttk.Frame(self.root, relief=tk.SUNKEN, padding="2 5"); status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.token_count_label = ttk.Label(status_bar, text="~0 tokens"); self.token_count_label.pack(side=tk.RIGHT)
        ttk.Label(status_bar, text="Estimated Size:").pack(side=tk.RIGHT, padx=(0,5))
    
    def open_settings(self): SettingsWindow(self.root, self.settings_manager, self.on_settings_closed)
    def on_settings_closed(self):
        messagebox.showinfo("Settings Saved", "Settings updated. The file tree will now be refreshed.")
        if self.project_path: self.load_project(self.project_path)

    def select_folder_dialog(self):
        folder = filedialog.askdirectory(title="Select Project Root Folder")
        if folder: self.load_project(folder)

    def load_project(self, path):
        self.project_path = get_long_path_name(path)
        self.clear_tree(); self.populate_tree(self.project_path, ""); self.generate_btn.config(state=tk.NORMAL)
        
    def clear_tree(self):
        self.tree.delete(*self.tree.get_children()); self.file_states = {}; self.update_token_count()
        
    def populate_tree(self, path, parent_node):
        exclude_list = self.settings_manager.get("exclude_list"); exclude_dotfiles = self.settings_manager.get("exclude_dotfiles"); extension_map = self.settings_manager.get("extension_map")
        try: items = sorted(os.listdir(path))
        except PermissionError: return
        for item in items:
            if item in exclude_list or (exclude_dotfiles and item.startswith('.')): continue
            full_path = os.path.join(path, item)
            relative_path = os.path.relpath(full_path, self.project_path)
            if os.path.isdir(full_path):
                node = self.tree.insert(parent_node, "end", text=f"[ ] {item}", values=(relative_path, "Folder"), open=False)
                self.file_states[node] = {"checked": False, "path": full_path, "type": "folder", "children": []}
                if parent_node in self.file_states: self.file_states[parent_node]["children"].append(node)
                self.populate_tree(full_path, node)
            else:
                _, ext = os.path.splitext(item)
                if ext.lower() in extension_map:
                    node = self.tree.insert(parent_node, "end", text=f"[ ] {item}", values=(relative_path, ext[1:].upper()))
                    self.file_states[node] = {"checked": False, "path": full_path, "type": "file"}
                    if parent_node in self.file_states: self.file_states[parent_node]["children"].append(node)
                        
    def handle_tree_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region != "tree": return
        item = self.tree.identify_row(event.y)
        if not item or item not in self.file_states: return
        new_state = not self.file_states[item]["checked"]
        self.set_item_state(item, new_state)
        if self.file_states[item]["type"] == "folder": self.update_children(item, new_state)
        self.update_parents(item)
        self.update_token_count()
        
    def set_item_state(self, item, state):
        if item not in self.file_states: return
        self.file_states[item]["checked"] = state
        base_text = self.tree.item(item, "text")
        if re.match(r"\[[✔✔~ ]\] ", base_text): base_text = base_text[4:]
        if state is True: display_text = f"[✔] {base_text}"
        elif state is False: display_text = f"[ ] {base_text}"
        else: display_text = f"[~] {base_text}"
        self.tree.item(item, text=display_text)

    def update_children(self, item, state):
        for child in self.file_states.get(item, {}).get("children", []):
            self.set_item_state(child, state)
            if self.file_states[child]["type"] == "folder": self.update_children(child, state)
                    
    def update_parents(self, item):
        parent = self.tree.parent(item)
        if not parent or parent not in self.file_states: return
        children = self.file_states[parent].get("children", [])
        if not children: return
        checked_states = [self.file_states[c]["checked"] for c in children if c in self.file_states]
        if all(s is True for s in checked_states): new_state = True
        elif all(s is False for s in checked_states): new_state = False
        else: new_state = None
        if self.file_states[parent]["checked"] != new_state:
            self.set_item_state(parent, new_state); self.update_parents(parent)

    def update_token_count(self):
        total_chars = 0
        for item, info in self.file_states.items():
            if info["type"] == "file" and info["checked"]:
                try:
                    with open(info["path"], "r", encoding="utf-8", errors="ignore") as f:
                        total_chars += len(f.read())
                except (IOError, OSError): continue
        # Simple heuristic: 1 token ~ 4 characters
        estimated_tokens = int(total_chars / 4)
        self.token_count_label.config(text=f"~{estimated_tokens:,} tokens")

    def _generate_tree_structure(self, file_paths):
        tree = {}
        for path in file_paths:
            parts = path.replace(os.sep, '/').split('/')
            current_level = tree
            for part in parts:
                if part not in current_level: current_level[part] = {}
                current_level = current_level[part]

        lines = ["."]; P_C, P_S = "├── ", "│   "; E_C, E_S = "└── ", "    "
        def _build_lines(d, prefix=""):
            items = sorted(d.keys())
            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                connector = E_C if is_last else P_C
                lines.append(f"{prefix}{connector}{item}{'/' if d[item] else ''}")
                if d[item]:
                    new_prefix = prefix + (E_S if is_last else P_S)
                    _build_lines(d[item], new_prefix)
        _build_lines(tree)
        return "\n".join(lines)

    def generate_markdown(self):
        if not self.project_path:
            return messagebox.showwarning("Warning", "Please select a project folder.")
        
        selected_files = sorted([
            info["path"] for info in self.file_states.values() 
            if info["type"] == "file" and info["checked"]
        ])
        if not selected_files:
            return messagebox.showinfo("Info", "No files were selected.")
        
        output_file = filedialog.asksaveasfilename(
            defaultextension=".md", 
            filetypes=[("Markdown", "*.md"), ("All", "*.*")]
        )
        if not output_file:
            return

        # --- Pre-processing for Dependencies and SQL Consolidation ---
        known_deps = ['requirements.txt', 'package.json', 'Pipfile', 'pyproject.toml', 'pom.xml', 'build.gradle']
        dependency_files = [p for p in selected_files if os.path.basename(p) in known_deps]
        main_code_files = [p for p in selected_files if p not in dependency_files]
        relative_paths = [os.path.relpath(p, self.project_path) for p in selected_files]

        # Group main files by directory for consolidation logic
        grouped_files = defaultdict(lambda: defaultdict(list))
        for file_path in main_code_files:
            directory = os.path.dirname(os.path.relpath(file_path, self.project_path))
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.sql':
                grouped_files[directory]['sql'].append(file_path)
            else:
                grouped_files[directory]['other'].append(file_path)

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                project_name = os.path.basename(os.path.normpath(self.project_path))
                f.write(f"# `{project_name}` Project Files\n\n")
                f.write(f"📅 Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"📂 Project root: `{self.project_path}`\n\n---\n\n")

                # --- 1. Project Structure Tree ---
                f.write("## 🌳 Project Structure (Selected Files)\n\n")
                f.write(f"```\n{self._generate_tree_structure(relative_paths)}\n```\n\n---\n\n")

                # --- 2. Dependencies Section ---
                if dependency_files:
                    f.write("## ⚙️ Dependencies\n\n")
                    for dep_path in dependency_files:
                        filename = os.path.basename(dep_path)
                        relative_dep_path = os.path.relpath(dep_path, self.project_path).replace(os.sep, '/')
                        
                        f.write(f"### 📄 {filename}\n")
                        f.write(f"*path: `{relative_dep_path}`*\n\n")
                        f.write("---\n\n")
                        
                        f.write("```\n")
                        try:
                            with open(dep_path, "r", encoding="utf-8", errors='replace') as src:
                                f.write(src.read())
                        except Exception as e:
                            f.write(f"")
                        f.write("\n```\n\n")
                    f.write("---\n\n")
                
                # --- 3. Main File Contents Section ---
                f.write("## 📄 File Contents\n\n")
                extension_map = self.settings_manager.get("extension_map")
                
                for directory in sorted(grouped_files.keys()):
                    files_in_dir = grouped_files[directory]
                    display_dir = directory.replace(os.sep, "/") if directory else "(Root)"
                    f.write(f"### 📂 `{display_dir}`\n\n")

                    # --- SQL CONSOLIDATION BLOCK ---
                    if files_in_dir['sql']:
                        f.write("### 📄 SQL Schema Files (Consolidated)\n\n")
                        f.write("---\n\n")
                        f.write("```sql\n")
                        for i, sql_path in enumerate(sorted(files_in_dir['sql'])):
                            if i > 0:
                                f.write("\n\n-- -- -- -- -- -- -- -- -- --\n\n")
                            
                            filename = os.path.basename(sql_path)
                            relative_sql_path = os.path.relpath(sql_path, self.project_path).replace(os.sep, '/')
                            f.write(f"-- From: {filename} | path: {relative_sql_path}\n")
                            try:
                                with open(sql_path, 'r', encoding='utf-8', errors='replace') as src:
                                    f.write(src.read().strip())
                            except Exception as e:
                                f.write(f"/* Error reading file: {e} */")
                        f.write("\n```\n\n")

                    # --- OTHER FILES BLOCK ---
                    for file_path in sorted(files_in_dir['other']):
                        filename = os.path.basename(file_path)
                        relative_file_path = os.path.relpath(file_path, self.project_path).replace(os.sep, '/')
                        ext = os.path.splitext(filename)[1].lower()
                        lang = extension_map.get(ext, "")
                        
                        f.write(f"### 📄 {filename}\n")
                        f.write(f"*path: `{relative_file_path}`*\n\n")
                        f.write("---\n\n")
                        
                        f.write(f"```{lang}\n")
                        try:
                            with open(file_path, "r", encoding="utf-8", errors='replace') as src:
                                f.write(src.read())
                        except Exception as e:
                            f.write(f"")
                        f.write("\n```\n\n")
            
            messagebox.showinfo("Success", f"Documentation generated at:\n{output_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate documentation:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ProjectDocumenter(root)
    if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
        app.load_project(sys.argv[1])
    root.mainloop()