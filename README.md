# **LLM-Sherpa 📜✍️**

**Tired of explaining your sprawling, majestic, and *slightly* chaotic codebase to a Large Language Model?** Do you find yourself manually copy-pasting files, hoping the AI understands that `utils_final_final_v2.py` is, in fact, the most important file?

Fear not, weary developer! **LLM-Sherpa** is here to be the overly-organized, slightly-caffeinated intern you wish you had. It takes your beautiful mess of a project, lets you pick the good parts, and bundles it all into a single, pristine Markdown file that any LLM would be delighted to read.

Think of it as a diplomatic envoy for your code, ensuring it makes the best possible first impression.

## **What is this madness?**

In short, **LLM-Sherpa** is a modern Python GUI application built with **PySide6** that helps you package source code into a single, context-rich Markdown file. The goal is to create a perfect "prompt artifact" for Large Language Models. Instead of just pasting raw code, you're providing a structured document that includes:

* A file tree of the selected components
* Clearly separated dependency files (`requirements.txt`, `package.json`, etc.)
* Consolidated SQL files for easy schema review
* The actual content of each selected file, formatted in clean Markdown code blocks
* Smart categorization and organization for maximum LLM comprehension

This gives the AI the best possible chance of understanding your project's architecture and providing high-quality responses.

## **Features (The Good Parts) ✨**

### **Core Functionality**

* **Modern PySide6 Interface:** Beautiful, native GUI with proper menus, toolbars, and keyboard shortcuts
* **Interactive File Tree:** Select your project folder and get a hierarchical tree view with checkboxes for precise file selection
* **Smart Background Scanning:** Multi-threaded file system scanning that won't freeze your UI, even on massive projects
* **Intelligent Parent-Child Selection:** Check a folder to auto-select all its contents, or pick individual files with automatic parent state updates

### **Advanced Filtering & Organization**

* **Comprehensive Settings Panel:** Persistent configuration for file types, exclusions, and behavior preferences
* **Smart File Type Recognition:** Extensive built-in mapping of file extensions to proper Markdown syntax highlighting
* **Universal Exclusion System:** Say goodbye to `__pycache__`, `node_modules`, `.git`, and other clutter with customizable global exclusions
* **Dotfile Control:** Toggle inclusion of hidden files and folders starting with '.'

### **Output Intelligence**

* **Dynamic Project Structure:** Generates a clean ASCII tree showing *only* your selected files
* **Dependency Prioritization:** Automatically identifies and highlights common dependency files (`requirements.txt`, `package.json`, `pyproject.toml`, etc.) at the top
* **SQL Consolidation:** Groups `.sql` files from the same directory into organized, readable sections
* **Smart File Categorization:** Separates dependencies from main code files for logical document flow

### **User Experience**

* **Live Token Estimation:** Real-time character and token counting to help you stay within LLM context limits
* **Session Persistence:** Optionally remembers your last project and file selections between sessions
* **Keyboard Shortcuts:** Full keyboard navigation with standard shortcuts (Ctrl+O, Ctrl+S, Ctrl+A, etc.)
* **Status Updates:** Clear loading indicators and progress feedback for large projects
* **Error Handling:** Graceful handling of permission errors, corrupted files, and inaccessible directories

### **Professional Polish**

* **Native Menus & Toolbars:** Standard File, Edit, Settings, and Help menus with proper icons
* **Responsive Layout:** Columns auto-size appropriately, and the interface scales well on different screen sizes
* **Clean Markdown Output:** Professional formatting with proper headers, code blocks, and file path annotations
* **Comprehensive Documentation:** Built-in help system with full README access

## **Requirements & Installation 🛠️**

### **System Requirements**

* **Python 3.7+** (tested with Python 3.8+)
* **PySide6** for the modern GUI interface
* **Operating System:** Windows, macOS, or Linux

### **Installation**

1. **Clone or Download:**

   ```bash
   git clone https://github.com/VicRejkia/LLM-Sherpa.git
   cd LLM-Sherpa
   ```

2. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   *Or install manually:*

   ```bash
   pip install PySide6
   ```

3. **Run the Application:**

   ```bash
   python llm-sherpa.py
   ```

   **Pro Tip:** You can also pass a project path directly to auto-load on startup:

   ```bash
   python llm-sherpa.py "/path/to/your/project"
   ```

## **How to Use It (The Complete Guide) 🖱️**

### **Getting Started**

1. **Launch the Application:** Run `python llm-sherpa.py`
2. **Open Your Project:** 
   - Click "Open Project Folder" in the toolbar, OR
   - Use `Ctrl+O`, OR
   - Use **File > Open Project Folder...**
3. **Wait for Scanning:** The app will scan your project in the background (watch the status bar for progress)

### **Selecting Files**

* **Individual Files:** Check/uncheck specific files in the tree
* **Entire Folders:** Check a folder to select all its contents recursively
* **Bulk Selection:** Use `Ctrl+A` or **Edit > Toggle All Selections** to select/deselect everything
* **Smart Updates:** Parent folders automatically show partial selection when only some children are selected

### **Customizing Your Export**

* **Add Context:** Use the "Objective / Prompt" text area to include your specific questions or goals
* **Real-time Feedback:** Watch the token counter in the status bar to manage context size
* **Preview Selection:** The tree view clearly shows what will be included

### **Advanced Configuration**

Click the **Settings** button (or **Settings > Settings...**) to access:

#### **Persistence Options**

* **Remember Last Project:** Auto-load your most recent project on startup
* **Restore Tree Selection:** Remember which files you had selected for each project

#### **File Filtering**

* **Exclude Dotfiles:** Toggle whether to include hidden files/folders (those starting with '.')
* **Custom Exclusions:** Add files and folders to globally ignore (one per line)
* **File Type Mapping:** Customize which extensions are recognized and how they're syntax-highlighted

#### **Output Control**

* **Project Structure Toggle:** Choose whether to include the ASCII file tree in your output

### **Generating Documentation**

1. **Generate:** Click "Generate Documentation" or use `Ctrl+S`
2. **Choose Location:** Select where to save your `.md` file
3. **Success!** Your comprehensive project context is ready for any LLM

## **Default Configuration 📋**

### **Supported File Types**

Out of the box, LLM-Sherpa recognizes these extensions:
```
.py → python          .js → javascript      .html → html
.sql → sql            .css → css            .json → json  
.md → markdown        .txt → text           .yml/.yaml → yaml
.toml → toml          .ini → ini            .sh → bash
.bat → batch          .dockerfile → dockerfile
```

### **Default Exclusions**

These are automatically ignored (customizable in settings):
```
__pycache__    .git         .vscode       node_modules
venv           .env
```

### **Recognized Dependencies**

These files are automatically promoted to the "Dependencies" section:
```
requirements.txt    package.json     Pipfile
pyproject.toml     pom.xml          build.gradle
```

## **Output Structure 📄**

Your generated Markdown follows this logical structure:

```markdown
# 🎯 Objective
[Your custom prompt/context, if provided]

## 📚 Project Context: `your-project-name`

### 1. Project Structure
[ASCII tree of selected files]

### 2. Dependencies  
[Content of requirements.txt, package.json, etc.]

### 3. File Contents
[All your selected source files with proper syntax highlighting]
```

## **Pro Tips & Best Practices 💡**

### **For Optimal LLM Results**

* **Be Selective:** Don't include everything—focus on files relevant to your specific task
* **Use the Objective Field:** Clearly state what you want the LLM to help you with
* **Watch Token Counts:** Keep an eye on the estimated size to stay within your LLM's context window
* **Include Dependencies:** Always include `requirements.txt`, `package.json`, etc., so the LLM understands your tech stack

### **Managing Large Projects**

* **Incremental Selection:** Start with core files, then add supporting files as needed
* **Use Exclusions Wisely:** Add large, auto-generated directories to your exclusion list
* **Session Persistence:** Enable "Remember Last Project" for frequently-worked projects

### **Troubleshooting**

* **Permission Errors:** The app gracefully skips inaccessible files and continues scanning
* **Large Files:** Very large files might impact token counts—consider excluding logs, data files, or compiled assets
* **Custom Extensions:** Add your own file types in Settings > File Type Mapping

## **Keyboard Shortcuts ⌨️**

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open Project Folder |
| `Ctrl+S` | Generate Documentation |
| `Ctrl+A` | Toggle All Selections |
| `Ctrl+Q` | Quit Application |

## **Configuration Files 📁**

LLM-Sherpa creates two configuration files:

* **`settings.json`** - Stored next to the script, contains your filtering preferences and UI settings
* **Application Config** - Stored in your OS's standard config location, remembers project paths and tree states

## **System Compatibility 🖥️**

* **Windows:** Full support with native Windows path handling
* **macOS:** Complete compatibility with macOS file systems
* **Linux:** Requires `python3-tk` package (though PySide6 is the primary UI framework)

## **What's New in v1.1 🆕**

* **Complete PySide6 Rewrite:** Modern, native interface replacing the old tkinter GUI
* **Background File Scanning:** Non-blocking project loading for better performance
* **Enhanced Tree Navigation:** Improved file selection with better visual feedback
* **Professional Menus:** Standard menu bar with File, Edit, Settings, and Help menus
* **Keyboard Shortcuts:** Full keyboard navigation support
* **Better Error Handling:** More robust file system operations
* **Improved Documentation:** Built-in help system and about dialog

## **Contributing 🤝**

Got an idea to make LLM-Sherpa even better? Contributions are welcome! Here's how to get involved:

1. **Fork the Repository** on GitHub
2. **Create a Feature Branch:** `git checkout -b feature/amazing-new-feature`
3. **Make Your Changes:** Follow the existing code style and add appropriate comments
4. **Test Thoroughly:** Ensure your changes work across different operating systems
5. **Submit a Pull Request:** Describe your changes and why they're awesome

### **Development Setup**

```bash
git clone https://github.com/VicRejkia/LLM-Sherpa.git
cd LLM-Sherpa
pip install -r requirements.txt
python llm-sherpa.py
```

## **License 📄**

This project is licensed under the **Apache License 2.0**. See the [LICENSE](https://github.com/VicRejkia/LLM-Sherpa/blob/main/LICENSE) file for details.

## **Support & Issues 🆘**

Having trouble? Found a bug? Want to request a feature?

* **GitHub Issues:** [Report bugs or request features](https://github.com/VicRejkia/LLM-Sherpa/issues)
* **Discussions:** [Ask questions or share ideas](https://github.com/VicRejkia/LLM-Sherpa/discussions)

---

**Happy coding, and may your LLMs always understand your intentions!** 🚀