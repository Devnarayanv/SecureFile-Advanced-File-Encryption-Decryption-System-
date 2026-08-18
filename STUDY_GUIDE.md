# Python Environment & Command-Line Study Guide

This document lists and explains the essential terminal commands for setting up and managing a Python workspace on **Windows**.

---

## 1. Environment Setup Commands

### A. Check Python and Launcher Installation
Before doing anything, you check if Python is installed on your computer.
- **Command:**
  ```powershell
  py --version
  ```
- **Explanation:** `py` is the official Python Launcher for Windows. This command prints the version of Python it is currently pointing to (e.g., `Python 3.14.0`).
- **Alternative:** If `py` is not found, you can use `python --version` or `python3 --version`.

### B. Create a Virtual Environment (`.venv`)
A virtual environment is an isolated container for your project's dependencies so they do not interfere with other projects on your machine.
- **Command:**
  ```powershell
  py -m venv .venv
  ```
- **Explanation:**
  - `py` starts Python.
  - `-m venv` runs the built-in module named `venv` (virtual environment creator).
  - `.venv` is the name of the folder where the environment is created (you can name it anything, but `.venv` is standard).

---

## 2. Managing the Virtual Environment

### A. Activate the Virtual Environment
To use the isolated Python version and package installer inside `.venv`, you must activate it first.
- **Command (PowerShell):**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
- **Command (Command Prompt / CMD):**
  ```cmd
  .venv\Scripts\activate.bat
  ```
- **Explanation:** This runs an activation script. Once active, your command line prompt will be prefixed with `(.venv)`, showing that any python or pip commands you run will use the files inside the `.venv` folder.

### B. Deactivate the Virtual Environment
When you are done working on this project, you can exit the virtual environment.
- **Command:**
  ```powershell
  deactivate
  ```
- **Explanation:** Restores your terminal path and environment to your global system settings.

---

## 3. Package Management with `pip`

`pip` is Python's Package Installer. It downloads and installs libraries from PyPI (Python Package Index).

### A. Install a Specific Package
- **Command:**
  ```powershell
  pip install colorama
  ```
- **Explanation:** Installs the library `colorama` (used to print colored text in the terminal) directly into `.venv`.

### B. Install from a `requirements.txt` File
Instead of installing packages one by one, developers list them in a file named `requirements.txt`.
- **Command:**
  ```powershell
  pip install -r requirements.txt
  ```
- **Explanation:**
  - `-r` stands for "requirements".
  - `pip` reads the file and installs all packages listed there matching the specified versions.

### C. List Installed Packages
- **Command:**
  ```powershell
  pip list
  ```
- **Explanation:** Displays all Python libraries currently installed inside the active environment.

---

## 4. Running Your Python Program

Once your environment is set up and activated, you can execute your code.

- **Command (Active Virtual Env):**
  ```powershell
  python main.py
  ```
- **Command (Without Activating, using full path directly):**
  ```powershell
  .venv\Scripts\python.exe main.py
  ```
- **Explanation:** Runs the `main.py` script using the virtual environment's Python interpreter.

---

## Study Exercise & Project Checklist

1. [x] **Create Environment:** Created using `py -m venv .venv`
2. [x] **Setup Dependencies:** Created `requirements.txt` and installed with `.venv\Scripts\pip install -r requirements.txt`
3. [x] **Write Code:** Wrote `main.py`
4. [ ] **Practice Running the App:** Run the application using the instructions below!
