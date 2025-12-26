# Patent Project

## 🚀 Getting Started

Follow these steps to set up the project on your local machine.

---

### 1️⃣ Clone the Repository

Open your **Command Prompt** (or terminal) and run:

```bash
git clone https://github.com/RoyaMhdd/ChatBotProject.git
cd ChatBotProject
```

---

### 2️⃣ Create a Virtual Environment

Create a virtual environment to isolate project dependencies:

```bash
python -m venv .venv
```

---

### 3️⃣ Activate the Virtual Environment

On Windows (CMD):

```bash
.venv\Scripts\activate
```

On PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

---

### 4️⃣ Install Required Packages

Install all dependencies listed in requirements.txt:

```bash
pip install -r requirements.txt
```

---

### ✅ Done!

Now your environment is ready to work on Patent Project.
You can open the project in PyCharm and set the interpreter to use the .venv folder.

---
# 🧠 AI System Prompts Configuration

This project uses external system prompt files to control the behavior of the AI assistant.  
Prompt files are intentionally excluded from the repository and must be created locally on each environment (developer machine or server).

The system dynamically selects one of six prompt variants based on:

- invention_type (process, product, hybrid)
- details flag (true / false)

## 1️⃣ Create the `prompts/` Directory

At the project root (same level as `manage.py`), create a directory named:

`prompts/`

Expected project structure:

ChatBotProject/  
├─ manage.py  
├─ app/  
├─ prompts/  
│  ├─ process_generative.txt  
│  ├─ process_non_generative.txt  
│  ├─ product_generative.txt  
│  ├─ product_non_generative.txt  
│  ├─ hybrid_generative.txt  
│  ├─ hybrid_non_generative.txt  

### Note
The `prompts/` directory is listed in `.gitignore` to ensure prompt contents are never committed to the repository.

## 2️⃣ Create Prompt Files (6 Variants)

Inside the `prompts/` directory, create the following six UTF-8 encoded text files:

- process_generative.txt  
- process_non_generative.txt  
- product_generative.txt  
- product_non_generative.txt  
- hybrid_generative.txt  
- hybrid_non_generative.txt  

Each file must contain the complete system-level instructions for the AI assistant.

## 3️⃣ Prompt Selection Logic

The backend dynamically loads the appropriate system prompt according to the following logic:

| invention_type | details | Loaded prompt file              |
|----------------|---------|----------------------------------|
| process        | false   | process_non_generative.txt       |
| process        | true    | process_generative.txt           |
| product        | false   | product_non_generative.txt       |
| product        | true    | product_generative.txt           |
| hybrid         | false   | hybrid_non_generative.txt        |
| hybrid         | true    | hybrid_generative.txt            |

This structure keeps prompt management modular, scalable, and environment-specific, while allowing precise control over AI behavior.


---

### 🧠 Notes

Always activate your virtual environment before running commands.

Keep your dependencies up to date by running:

```bash
pip install --upgrade -r requirements.txt
```


###
.env
make a .env file in your pc and fill following fields 

SECRET_KEY=django-insecure-xyz123...
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# 👉 if USE-MOCK is True it doesnt works with mock,if it is False it works with Api Key and Connected to OpenAi 
# for tests use Mock version please 
USE_MOCK=True
OPENAI_API_KEY=Our api Keyyyyyy




.env
SECRET_KEY=django-insecure-xyz123...
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
USE_MOCK=False
OPENAI_API_KEY=Our api Keyyyyyy



