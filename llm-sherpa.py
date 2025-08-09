import os
import sys
import json
import ast
import re
from datetime import datetime
import ctypes
from ctypes import wintypes

# --- PySide6 Imports ---
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTreeView, QTextEdit, QFileDialog, QMessageBox,
    QDialog, QCheckBox, QLabel, QDialogButtonBox, QStatusBar
)
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt, Slot

# --- UNCHANGED: get_long_path_name & SettingsManager ---
# This helper function and class are independent of the UI framework.
def get_long_path_name(short_path):
    if sys.platform != 'win32': return short_path
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
    except Exception: return short_path

class SettingsManager:
    def __init__(self, filename="settings.json"):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.filename = os.path.join(script_dir, filename)
        self.settings = {}
        self.load_settings()

    def _create_default_settings(self):
        return {
            "extension_map": { ".py": "python", ".sql": "sql", ".js": "javascript", ".html": "html", ".css": "css", ".json": "json", ".md": "markdown", ".txt": "text", ".yml": "yaml", ".yaml": "yaml", ".toml": "toml", ".ini": "ini", ".sh": "bash", ".bat": "batch", ".dockerfile": "dockerfile" },
            "exclude_list": [ "__pycache__", ".git", ".vscode", "node_modules", "venv", ".env" ],
            "exclude_dotfiles": True, "show_project_structure": True
        }

    def load_settings(self):
        try:
            with open(self.filename, 'r') as f:
                loaded_settings = json.load(f)
                defaults = self._create_default_settings(); defaults.update(loaded_settings); self.settings = defaults
        except (FileNotFoundError, json.JSONDecodeError):
            self.settings = self._create_default_settings(); self.save_settings()

    def save_settings(self):
        try:
            with open(self.filename, 'w') as f: json.dump(self.settings, f, indent=4)
        except IOError as e: print(f"Settings Error: Could not save settings: {e}")

    def get(self, key): return self.settings.get(key)
    def set(self, key, value): self.settings[key] = value

# --- NEW: PySide6 Settings Dialog ---
class SettingsWindow(QDialog):
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)

        # Options
        self.exclude_dotfiles_chk = QCheckBox("Exclude all files and folders starting with '.'")
        self.exclude_dotfiles_chk.setChecked(self.settings_manager.get("exclude_dotfiles"))
        layout.addWidget(self.exclude_dotfiles_chk)
        
        self.show_structure_chk = QCheckBox("Include 'Project Structure' tree in output")
        self.show_structure_chk.setChecked(self.settings_manager.get("show_project_structure"))
        layout.addWidget(self.show_structure_chk)

        # Exclusion Filters
        layout.addWidget(QLabel("\nExclude files/folders by name (one per line):"))
        self.exclude_text = QTextEdit()
        self.exclude_text.setText("\n".join(self.settings_manager.get("exclude_list")))
        layout.addWidget(self.exclude_text)

        # Mappings
        layout.addWidget(QLabel("\nMap extensions to Markdown language identifiers:"))
        self.ext_map_text = QTextEdit()
        ext_map_str = json.dumps(self.settings_manager.get("extension_map"), indent=4)
        self.ext_map_text.setText(ext_map_str)
        layout.addWidget(self.ext_map_text)

        # Dialog Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def accept(self):
        # Save settings when 'Save' is clicked
        self.settings_manager.set("exclude_dotfiles", self.exclude_dotfiles_chk.isChecked())
        self.settings_manager.set("show_project_structure", self.show_structure_chk.isChecked())
        
        exclude_list = self.exclude_text.toPlainText().strip().split("\n")
        self.settings_manager.set("exclude_list", [item.strip() for item in exclude_list if item.strip()])
        
        try:
            new_ext_map = ast.literal_eval(self.ext_map_text.toPlainText())
            if not isinstance(new_ext_map, dict): raise ValueError("Input is not a dictionary.")
            self.settings_manager.set("extension_map", new_ext_map)
        except (ValueError, SyntaxError) as e:
            QMessageBox.critical(self, "Invalid Format", f"File type mapping is not a valid Python dictionary.\nError: {e}")
            return

        self.settings_manager.save_settings()
        super().accept()

# --- NEW: PySide6 Main Application Window ---
class ProjectDocumenter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LLM-Sherpa - Project Documenter v0.1")
        self.setGeometry(100, 100, 800, 750)

        self.settings_manager = SettingsManager()
        self.project_path = ""

        self._is_updating_checks = False

        self.init_ui()
        if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
            self.load_project(sys.argv[1])
    
    def init_ui(self):
        # ... (This entire method is correct, no changes needed here) ...
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Top button layout
        button_layout = QHBoxLayout()
        self.select_btn = QPushButton("Select Project Folder")
        self.generate_btn = QPushButton("Generate Documentation")
        self.settings_btn = QPushButton("Settings")
        self.generate_btn.setEnabled(False)
        button_layout.addWidget(self.select_btn)
        button_layout.addWidget(self.generate_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.settings_btn)
        main_layout.addLayout(button_layout)

        # Tree View for file hierarchy
        self.tree_view = QTreeView()
        self.tree_model = QStandardItemModel()
        self.tree_model.setHorizontalHeaderLabels(['Name', 'Path', 'Type'])
        self.tree_view.setModel(self.tree_model)
        self.tree_view.setColumnWidth(0, 350)
        main_layout.addWidget(self.tree_view, stretch=3)

        # Prompt Text Area
        main_layout.addWidget(QLabel("🎯 Objective / Prompt (Optional)"))
        self.prompt_text = QTextEdit()
        main_layout.addWidget(self.prompt_text, stretch=1)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.token_count_label = QLabel("Estimated Size: ~0 tokens")
        self.status_bar.addPermanentWidget(self.token_count_label)

        # --- Signal and Slot Connections ---
        self.select_btn.clicked.connect(self.select_folder_dialog)
        self.settings_btn.clicked.connect(self.open_settings)
        self.generate_btn.clicked.connect(self.generate_markdown)
        self.tree_model.itemChanged.connect(self.on_item_changed)
        self.prompt_text.textChanged.connect(self.update_token_count)

    # --- NO CHANGES to select_folder_dialog, load_project, populate_tree, on_item_changed, open_settings ---
    # These methods are all correct and do not need to be changed.
    @Slot()
    def select_folder_dialog(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Project Root Folder")
        if folder:
            self.load_project(folder)

    def load_project(self, path):
        self.project_path = get_long_path_name(path)
        self.tree_model.removeRows(0, self.tree_model.rowCount()) # Clear existing tree
        self.populate_tree(self.project_path, self.tree_model.invisibleRootItem())
        self.generate_btn.setEnabled(True)
        self.update_token_count()

    def populate_tree(self, path, parent_item):
        exclude_list = self.settings_manager.get("exclude_list")
        exclude_dotfiles = self.settings_manager.get("exclude_dotfiles")
        extension_map = self.settings_manager.get("extension_map")

        try: items = sorted(os.listdir(path))
        except PermissionError: return

        for name in items:
            if name in exclude_list or (exclude_dotfiles and name.startswith('.')): continue
            
            full_path = os.path.join(path, name)
            relative_path = os.path.relpath(full_path, self.project_path)
            
            name_item = QStandardItem(name)
            name_item.setCheckable(True)
            name_item.setEditable(False)
            name_item.setData(full_path, Qt.UserRole) # Store full path in item

            path_item = QStandardItem(relative_path)
            path_item.setEditable(False)
            
            if os.path.isdir(full_path):
                type_item = QStandardItem("Folder")
                type_item.setEditable(False)
                parent_item.appendRow([name_item, path_item, type_item])
                self.populate_tree(full_path, name_item) # Recurse
            else:
                _, ext = os.path.splitext(name)
                if ext.lower() in extension_map:
                    type_item = QStandardItem(ext[1:].upper())
                    type_item.setEditable(False)
                    parent_item.appendRow([name_item, path_item, type_item])
    
    @Slot(QStandardItem)
    def on_item_changed(self, item):
        if self._is_updating_checks: return # Prevent recursion

        self._is_updating_checks = True
        # Update children if a folder is checked/unchecked
        if item.hasChildren():
            for row in range(item.rowCount()):
                child = item.child(row, 0)
                if child and child.isCheckable():
                    child.setCheckState(item.checkState())
        
        # Update parent state
        parent = item.parent()
        if parent:
            child_states = [parent.child(row, 0).checkState() for row in range(parent.rowCount())]
            if all(s == Qt.CheckState.Checked for s in child_states):
                parent.setCheckState(Qt.CheckState.Checked)
            elif all(s == Qt.CheckState.Unchecked for s in child_states):
                parent.setCheckState(Qt.CheckState.Unchecked)
            else:
                parent.setCheckState(Qt.CheckState.PartiallyChecked)
        
        self._is_updating_checks = False
        self.update_token_count()
    
    # --- FIX: New recursive helper function ---
    def _get_checked_file_paths(self, parent_item):
        """Recursively traverses the model to find all checked files."""
        paths = []
        for row in range(parent_item.rowCount()):
            child_item = parent_item.child(row, 0)
            if not child_item:
                continue
            
            # If it's a folder, recurse into it
            if child_item.hasChildren():
                paths.extend(self._get_checked_file_paths(child_item))
            # If it's a file and it's checked, add its path
            elif child_item.checkState() == Qt.CheckState.Checked:
                file_path = child_item.data(Qt.UserRole)
                if file_path:
                    paths.append(file_path)
        return paths

    # --- FIX: Reworked update_token_count ---
    def update_token_count(self):
        total_chars = len(self.prompt_text.toPlainText())
        
        # Use the new helper function to get the list of files
        root = self.tree_model.invisibleRootItem()
        checked_files = self._get_checked_file_paths(root)

        for file_path in checked_files:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    total_chars += len(f.read())
            except (IOError, OSError):
                continue
        
        estimated_tokens = int(total_chars / 4)
        self.token_count_label.setText(f"Estimated Size: ~{estimated_tokens:,} tokens")

    @Slot()
    def open_settings(self):
        dialog = SettingsWindow(self.settings_manager, self)
        if dialog.exec(): # exec() returns true if accepted
            if self.project_path:
                self.load_project(self.project_path) # Reload project with new settings
    
    # --- UNCHANGED LOGIC: _generate_tree_structure ---
    def _generate_tree_structure(self, file_paths):
        # This function's logic is UI-independent and remains the same.
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

    # --- FIX: Reworked generate_markdown ---
    def generate_markdown(self):
        prompt_text = self.prompt_text.toPlainText().strip()
        
        # Use the new helper function to get the list of files
        root = self.tree_model.invisibleRootItem()
        selected_files = sorted(self._get_checked_file_paths(root))

        if not selected_files and not prompt_text:
            QMessageBox.information(self, "Info", "No files selected and no prompt provided.")
            return
        
        output_file, _ = QFileDialog.getSaveFileName(self, "Save Documentation", "", "Markdown Files (*.md);;All Files (*)")
        if not output_file:
            return

        # --- The rest of the markdown generation logic is mostly unchanged ---
        has_objective = bool(prompt_text)
        show_structure_setting = self.settings_manager.get("show_project_structure")
        has_structure = show_structure_setting and selected_files
        known_deps = ['requirements.txt', 'package.json', 'Pipfile', 'pyproject.toml', 'pom.xml', 'build.gradle']
        dependency_files = [p for p in selected_files if os.path.basename(p) in known_deps]
        has_dependencies = bool(dependency_files)
        main_code_files = [p for p in selected_files if p not in dependency_files]
        has_main_files = bool(main_code_files)

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                if has_objective:
                    f.write("# 🎯 Objective\n\n")
                    f.write(prompt_text)
                    f.write("\n\n---\n\n")

                if has_structure or has_dependencies or has_main_files:
                    project_name = os.path.basename(os.path.normpath(self.project_path))
                    f.write(f"## 📚 Project Context: `{project_name}`\n\n")
                    f.write("This document provides the necessary files and structure for the task.\n\n")

                    section_counter = 1

                    # Section: Project Structure
                    if has_structure:
                        f.write(f"### {section_counter}. Project Structure\n\n")
                        relative_paths = [os.path.relpath(p, self.project_path) for p in selected_files]
                        f.write(f"```\n{self._generate_tree_structure(relative_paths)}\n```\n\n")
                        section_counter += 1

                    # Section: Dependencies
                    if has_dependencies:
                        f.write(f"### {section_counter}. Dependencies\n\n")
                        for dep_path in dependency_files:
                            filename = os.path.basename(dep_path)
                            relative_dep_path = os.path.relpath(dep_path, self.project_path).replace(os.sep, '/')
                            f.write(f"#### `{filename}`\n*path: `{relative_dep_path}`*\n\n")
                            f.write("```\n")
                            try:
                                with open(dep_path, "r", encoding="utf-8", errors='replace') as src:
                                    f.write(src.read())
                            except Exception as e:
                                f.write(f"Error reading file: {e}")
                            f.write("\n```\n\n")
                        section_counter += 1

                    # Section: File Contents
                    if has_main_files:
                        f.write(f"### {section_counter}. File Contents\n\n")
                        extension_map = self.settings_manager.get("extension_map")
                        for file_path in main_code_files:
                            filename = os.path.basename(file_path)
                            relative_file_path = os.path.relpath(file_path, self.project_path).replace(os.sep, '/')
                            ext = os.path.splitext(filename)[1].lower()
                            lang = extension_map.get(ext, "")
                            f.write(f"#### 📄 `{filename}`\n\n*path: `{relative_file_path}`*\n\n")
                            f.write(f"```{lang}\n")
                            try:
                                with open(file_path, "r", encoding="utf-8", errors='replace') as src:
                                    f.write(src.read())
                            except Exception as e:
                                f.write(f"Error reading file: {e}")
                            f.write("\n```\n\n")
            QMessageBox.information(self, "Success", f"Documentation generated at:\n{output_file}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate documentation:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = ProjectDocumenter()
    main_window.show()
    sys.exit(app.exec())