# **CodeScribe 📜✍️**

**Tired of explaining your sprawling, majestic, and *slightly* chaotic codebase to a Large Language Model?** Do you find yourself manually copy-pasting files, hoping the AI understands that `utils_final_final_v2.py` is, in fact, the most important file?

Fear not, weary developer\! **CodeScribe** is here to be the overly-organized, slightly-caffeinated intern you wish you had. It takes your beautiful mess of a project, lets you pick the good parts, and bundles it all into a single, pristine Markdown file that any LLM would be delighted to read.

Think of it as a diplomatic envoy for your code, ensuring it makes the best possible first impression.

## **What is this madness?**

In short, **CodeScribe** is a Python GUI application that helps you package source code into a single, context-rich Markdown file. The goal is to create a perfect "prompt artifact" for Large Language Models. Instead of just pasting raw code, you're providing a structured document that includes:

* A file tree of the selected components.  
* Clearly separated dependency files (`requirements.txt`, etc.).  
* Consolidated SQL files for easy schema review.  
* The actual content of each selected file, formatted in clean Markdown code blocks.

This gives the AI the best possible chance of understanding your project's architecture and providing a high-quality response.

## **Features (The Good Parts) ✨**

* **Interactive File Tree:** Select your project folder and get a full tree view. Check the files and folders you want to include.  
* **Smart Filtering:** A persistent settings panel lets you define file extensions to include and create a universal exclusion list (goodbye, `__pycache__` and `node_modules`!).  
* **Dynamic File Tree Generation:** The output markdown includes a text-based tree of *only the files you selected*, giving the LLM an immediate overview.  
* **Dependency First:** Automatically identifies and highlights common dependency files at the top of the document.  
* **SQL Consolidation:** Intelligently groups all selected `.sql` files from the same directory into a single, easy-to-read code block.  
* **Live Token Counter:** A real-time token estimator helps you keep your context size in check for different LLMs.  
* **Polished Output:** Adds file paths and separators to the final markdown for maximum readability.

## **How to Use It (The Pointy-Clicky Bit) 🖱️**

1. **Prerequisites:** Make sure you have Python installed. The script uses the built-in `tkinter` library, which is included with most Python installations on Windows and macOS. On Linux, you may need to install it separately:  

    ```shell
    sudo apt-get install python3-tk
    ```

2. **Run the Script:**  

    ```shell
    python CodeScribe.py
    ```

   You can also optionally pass a project path as a command-line argument to auto-load it on startup:  

   ```shell
   python CodeScribe.py "C:\\path\\to\\your\\project"
   ```

3. **Select a Folder:** Click the "Select Project Folder" button to load your codebase into the tree view.  
4. **Check Your Files:** Use the checkboxes to select the files and folders you want to include in the export.  
5. **Tweak Settings (Optional):** Click the "Settings" button to customize which file types are recognized and which folders/files are globally ignored. Your settings are saved in a `settings.json` file next to the script.  
6. **Generate\!** Click "Generate Documentation". You will be prompted to choose a location to save your `.md` file.  
7. **Upload to your LLM:** Take the generated Markdown file and use it as the context for your prompt. Enjoy the significantly better answers\!

## **Contributing 🤝**

Got an idea to make CodeScribe even better? Contributions are welcome\! Feel free to fork the repository, make your changes, and submit a pull request.

## **License 📄**

This project is licensed under the Apache License 2.0. See the [LICENSE](https://www.google.com/search?q=LICENSE) file for details.
