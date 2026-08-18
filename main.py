"""
Python Interactive Study Guide
------------------------------
This script is designed for you to study core Python concepts.
You can read through the source code comments to understand the syntax,
and run the script to see how each concept behaves in real time.
"""

import os
import sys
import time
from colorama import init, Fore, Back, Style

# Initialize colorama to support colored output in the Windows terminal
init(autoreset=True)

def clear_screen():
    """Utility function to clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def wait_for_user():
    """Pause execution until the user presses Enter."""
    print(f"\n{Fore.CYAN}Press Enter to return to the main menu...{Style.RESET_ALL}")
    input()

# =====================================================================
# STUDY TOPIC 1: Variables & Data Types
# =====================================================================
def study_variables():
    clear_screen()
    print(f"{Back.BLUE}{Fore.WHITE} === TOPIC 1: VARIABLES & DATA TYPES === {Style.RESET_ALL}\n")
    
    print(f"{Fore.GREEN}# 1. Variables are dynamically typed (no need to declare types upfront){Style.RESET_ALL}")
    x = 10                  # Integer (int)
    y = 3.14                # Floating-point number (float)
    name = "Alice"          # String (str)
    is_learning = True      # Boolean (bool)
    
    print(f"Code:")
    print("  x = 10")
    print("  y = 3.14")
    print("  name = 'Alice'")
    print("  is_learning = True\n")
    
    print(f"Values and Types in Python:")
    print(f"  x is {Fore.YELLOW}{x}{Style.RESET_ALL} (type: {type(x).__name__})")
    print(f"  y is {Fore.YELLOW}{y}{Style.RESET_ALL} (type: {type(y).__name__})")
    print(f"  name is {Fore.YELLOW}'{name}'{Style.RESET_ALL} (type: {type(name).__name__})")
    print(f"  is_learning is {Fore.YELLOW}{is_learning}{Style.RESET_ALL} (type: {type(is_learning).__name__})\n")
    
    print(f"{Fore.GREEN}# 2. Basic Arithmetic & F-Strings (Formatted string literals){Style.RESET_ALL}")
    result = x + y
    print(f"Code:")
    print("  result = x + y")
    print("  print(f'Sum: {result:.2f}')")
    print(f"Output:")
    print(f"  Sum: {Fore.YELLOW}{result:.2f}{Style.RESET_ALL} (formatted to 2 decimal places)\n")
    
    wait_for_user()

# =====================================================================
# STUDY TOPIC 2: Control Flow (Conditional Statements & Loops)
# =====================================================================
def study_control_flow():
    clear_screen()
    print(f"{Back.BLUE}{Fore.WHITE} === TOPIC 2: CONTROL FLOW (IF & LOOPS) === {Style.RESET_ALL}\n")
    
    # Conditional statement (if-elif-else)
    print(f"{Fore.GREEN}# 1. Conditional Statements (if-elif-else){Style.RESET_ALL}")
    age = 20
    print(f"Code:")
    print("  age = 20")
    print("  if age < 18:")
    print("      print('Minor')")
    print("  elif age < 65:")
    print("      print('Adult')")
    print("  else:")
    print("      print('Senior')")
    
    print(f"Output:")
    if age < 18:
        print(f"  Result: {Fore.YELLOW}Minor{Style.RESET_ALL}")
    elif age < 65:
        print(f"  Result: {Fore.YELLOW}Adult{Style.RESET_ALL}")
    else:
        print(f"  Result: {Fore.YELLOW}Senior{Style.RESET_ALL}")
    print()
    
    # Loops
    print(f"{Fore.GREEN}# 2. Loops (for and while){Style.RESET_ALL}")
    print("Code (For Loop iterating over a range):")
    print("  for i in range(3):")
    print("      print(f'Loop iteration: {i}')")
    print("Output:")
    for i in range(3):
        print(f"  Loop iteration: {Fore.YELLOW}{i}{Style.RESET_ALL}")
    print()
    
    print("Code (While Loop with condition):")
    print("  count = 3")
    print("  while count > 0:")
    print("      print(count)")
    print("      count -= 1")
    print("Output:")
    count = 3
    while count > 0:
        print(f"  Countdown: {Fore.YELLOW}{count}{Style.RESET_ALL}")
        count -= 1
        
    wait_for_user()

# =====================================================================
# STUDY TOPIC 3: Data Structures (Lists & Dictionaries)
# =====================================================================
def study_data_structures():
    clear_screen()
    print(f"{Back.BLUE}{Fore.WHITE} === TOPIC 3: DATA STRUCTURES === {Style.RESET_ALL}\n")
    
    # Lists
    print(f"{Fore.GREEN}# 1. Lists (Ordered, mutable sequences){Style.RESET_ALL}")
    fruits = ["apple", "banana", "cherry"]
    print("Code:")
    print("  fruits = ['apple', 'banana', 'cherry']")
    print("  fruits.append('orange')")
    print("  print(fruits[0]) # Accessing elements")
    
    fruits.append("orange")
    print("Output:")
    print(f"  Full list: {Fore.YELLOW}{fruits}{Style.RESET_ALL}")
    print(f"  First fruit (index 0): {Fore.YELLOW}{fruits[0]}{Style.RESET_ALL}")
    print(f"  List length: {Fore.YELLOW}{len(fruits)}{Style.RESET_ALL}\n")
    
    # Dictionaries
    print(f"{Fore.GREEN}# 2. Dictionaries (Key-Value pairs){Style.RESET_ALL}")
    student = {
        "name": "Alex",
        "course": "Python 101",
        "grade": "A"
    }
    print("Code:")
    print("  student = {'name': 'Alex', 'course': 'Python 101', 'grade': 'A'}")
    print("  student['passed'] = True # Add new key-value pair")
    
    student["passed"] = True
    print("Output:")
    print(f"  Student dict: {Fore.YELLOW}{student}{Style.RESET_ALL}")
    print(f"  Student Name: {Fore.YELLOW}{student['name']}{Style.RESET_ALL}")
    print(f"  Keys in dictionary: {Fore.YELLOW}{list(student.keys())}{Style.RESET_ALL}\n")
    
    wait_for_user()

# =====================================================================
# STUDY TOPIC 4: Functions & Scope
# =====================================================================
def greet_user(username, greeting="Hello"):
    """
    A simple function with a default parameter value.
    Docstrings (like this text) document what the function does.
    """
    return f"{greeting}, {username}!"

def study_functions():
    clear_screen()
    print(f"{Back.BLUE}{Fore.WHITE} === TOPIC 4: FUNCTIONS & SCOPE === {Style.RESET_ALL}\n")
    
    print(f"{Fore.GREEN}# 1. Defining and Calling Functions{Style.RESET_ALL}")
    print("Code:")
    print("  def greet_user(username, greeting='Hello'):")
    print("      return f'{greeting}, {username}!'")
    print("\nCalling the function:")
    print("  print(greet_user('Devan'))")
    print("  print(greet_user('Devan', greeting='Welcome'))")
    
    print("\nOutput:")
    print(f"  Call 1: {Fore.YELLOW}{greet_user('Devan')}{Style.RESET_ALL}")
    print(f"  Call 2: {Fore.YELLOW}{greet_user('Devan', greeting='Welcome')}{Style.RESET_ALL}\n")
    
    print(f"{Fore.GREEN}# 2. Function Docstrings (Documentation){Style.RESET_ALL}")
    print("Python lets you inspect a function's documentation at runtime:")
    print("  print(greet_user.__doc__)")
    print("\nOutput:")
    print(f"{Fore.LIGHTBLACK_EX}{greet_user.__doc__}{Style.RESET_ALL}")
    
    wait_for_user()

# =====================================================================
# STUDY TOPIC 5: File Operations (I/O)
# =====================================================================
def study_file_io():
    clear_screen()
    print(f"{Back.BLUE}{Fore.WHITE} === TOPIC 5: FILE OPERATIONS (I/O) === {Style.RESET_ALL}\n")
    
    filename = "study_note.txt"
    print(f"We will create and write to a file named: {Fore.CYAN}{filename}{Style.RESET_ALL}\n")
    
    # Writing to a file
    print(f"{Fore.GREEN}# 1. Writing to a file using 'with open()'{Style.RESET_ALL}")
    print("Code:")
    print(f"  with open('{filename}', 'w') as file:")
    print("      file.write('Learning Python is fun!\\n')")
    print("      file.write('Virtual environments help organize dependencies.\\n')")
    
    with open(filename, 'w') as file:
        file.write("Learning Python is fun!\n")
        file.write("Virtual environments help organize dependencies.\n")
    print(f"{Fore.YELLOW}  [File written successfully!]{Style.RESET_ALL}\n")
    
    # Reading from a file
    print(f"{Fore.GREEN}# 2. Reading from the file{Style.RESET_ALL}")
    print("Code:")
    print(f"  with open('{filename}', 'r') as file:")
    print("      content = file.read()")
    print("      print(content)")
    
    print("\nOutput (Content read from file):")
    with open(filename, 'r') as file:
        content = file.read()
        for line in content.splitlines():
            print(f"  | {Fore.YELLOW}{line}{Style.RESET_ALL}")
            
    # Cleanup the file
    print(f"\n{Fore.GREEN}# 3. Cleaning up (deleting the study_note.txt file)...{Style.RESET_ALL}")
    if os.path.exists(filename):
        os.remove(filename)
        print(f"  {Fore.LIGHTBLACK_EX}[File {filename} deleted]{Style.RESET_ALL}")
        
    wait_for_user()

# =====================================================================
# STUDY TOPIC 6: Understanding Environments & CLI
# =====================================================================
def study_environments():
    clear_screen()
    print(f"{Back.BLUE}{Fore.WHITE} === TOPIC 6: PYTHON ENVIRONMENTS & VENV === {Style.RESET_ALL}\n")
    
    print(f"{Fore.CYAN}What is a Virtual Environment (.venv)?{Style.RESET_ALL}")
    print("- A self-contained folder that contains a Python installation for a specific version,")
    print("  along with its own copy of pip, library packages, and activation scripts.")
    print("- It prevents version conflicts between different projects on your computer.\n")
    
    print(f"{Fore.CYAN}Important files in this project folder:{Style.RESET_ALL}")
    print(f"- {Fore.YELLOW}.venv/{Style.RESET_ALL}       : The virtual environment directory containing the python binaries.")
    print(f"- {Fore.YELLOW}requirements.txt{Style.RESET_ALL} : Lists external packages required (like colorama).")
    print(f"- {Fore.YELLOW}main.py{Style.RESET_ALL}          : This study guide script.\n")
    
    print(f"{Fore.CYAN}Standard Command-Line Commands to Know:{Style.RESET_ALL}")
    print(f"1. {Fore.GREEN}Create environment{Style.RESET_ALL} : py -m venv .venv")
    print(f"2. {Fore.GREEN}Activate (.venv)  {Style.RESET_ALL} : .venv\\Scripts\\activate  (Windows PowerShell or Command Prompt)")
    print(f"3. {Fore.GREEN}Install packages  {Style.RESET_ALL} : pip install -r requirements.txt")
    print(f"4. {Fore.GREEN}Run your script   {Style.RESET_ALL} : python main.py")
    print(f"5. {Fore.GREEN}Deactivate venv   {Style.RESET_ALL} : deactivate")
    
    wait_for_user()

# =====================================================================
# MAIN MENU LOOP
# =====================================================================
def main():
    while True:
        clear_screen()
        print(f"{Fore.CYAN}==================================================")
        print(f"       {Fore.LIGHTYELLOW_EX}Interactive Python & Venv Study Guide{Fore.CYAN}")
        print(f"=================================================={Style.RESET_ALL}")
        print(f"Current Python Interpreter: {Fore.YELLOW}{sys.executable}{Style.RESET_ALL}")
        print(f"Virtual Env Active: {Fore.GREEN if hasattr(sys, 'real_prefix') or (sys.base_prefix != sys.prefix) else Fore.RED}{sys.base_prefix != sys.prefix}{Style.RESET_ALL}")
        print("--------------------------------------------------")
        print("Please choose a topic to study:")
        print(f"  {Fore.LIGHTGREEN_EX}1.{Style.RESET_ALL} Variables & Data Types")
        print(f"  {Fore.LIGHTGREEN_EX}2.{Style.RESET_ALL} Control Flow (If statements, loops)")
        print(f"  {Fore.LIGHTGREEN_EX}3.{Style.RESET_ALL} Data Structures (Lists, Dictionaries)")
        print(f"  {Fore.LIGHTGREEN_EX}4.{Style.RESET_ALL} Functions & Scope")
        print(f"  {Fore.LIGHTGREEN_EX}5.{Style.RESET_ALL} File Operations (I/O)")
        print(f"  {Fore.LIGHTGREEN_EX}6.{Style.RESET_ALL} Environments, Pip & CLI commands")
        print(f"  {Fore.LIGHTRED_EX}7.{Style.RESET_ALL} Exit Guide")
        print("--------------------------------------------------")
        
        choice = input("Enter your choice (1-7): ").strip()
        
        if choice == '1':
            study_variables()
        elif choice == '2':
            study_control_flow()
        elif choice == '3':
            study_data_structures()
        elif choice == '4':
            study_functions()
        elif choice == '5':
            study_file_io()
        elif choice == '6':
            study_environments()
        elif choice == '7':
            clear_screen()
            print(f"\n{Fore.GREEN}Thank you for studying Python! Keep coding!{Style.RESET_ALL}\n")
            break
        else:
            print(f"{Fore.RED}Invalid choice. Please enter a number between 1 and 7.{Style.RESET_ALL}")
            time.sleep(1.5)

if __name__ == "__main__":
    main()
