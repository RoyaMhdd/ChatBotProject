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


