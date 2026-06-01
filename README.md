# 🚀 AI GitHub README Generator

Generate professional, production-ready GitHub README files automatically using AI-powered repository analysis, Agentic AI workflows, and Large Language Models.

Live on streamlit - https://aireadmegenerator.streamlit.app/

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Web_App-red)
![Gemini](https://img.shields.io/badge/Gemini-LLM-orange)
![OpenRouter](https://img.shields.io/badge/OpenRouter-Supported-green)

---

## 📖 Overview

Writing a high-quality README is often overlooked despite being one of the most important parts of a software project.

AI GitHub README Generator automates this process by analyzing a GitHub repository, understanding its structure, technologies, dependencies, and purpose, and then generating a professional README file within seconds.

The application uses an Agentic AI workflow powered by modern LLMs such as Gemini and OpenRouter models to produce detailed, structured, and developer-friendly documentation.

---

## ✨ Features

### 🔍 Repository Analysis
- Clones public GitHub repositories
- Analyzes project structure
- Detects technologies and frameworks
- Extracts dependencies automatically
- Identifies application entry points

### 🤖 Agentic AI Pipeline
- Repository Analyzer Agent
- Documentation Writer Agent
- README Reviewer Agent

### 🧠 Multi-LLM Support
Supports:

- Google Gemini
  - Gemini 2.5 Flash
  - Gemini 2.5 Pro
  - Gemini 2.0 Flash

- OpenRouter Models
  - Kimi K2.5
  - Kimi K2.6
  - Other OpenRouter-supported models

### 🎨 Streamlit Interface
- Clean and intuitive UI
- API key input support
- Model selection
- Custom generation instructions
- Real-time generation progress

### 📄 Professional README Generation
Automatically generates:

- Project Overview
- Features
- Installation Guide
- Usage Instructions
- Architecture Overview
- Tech Stack
- Folder Structure
- Contributing Guidelines
- License Information

---


## 🛠️ Tech Stack

This project is built primarily in Python, utilizing a robust set of modern libraries and frameworks:

*   **Core Language:** Python (`3.9+`)
*   **AI/LLM Orchestration:**
    *   [`agno`](https://github.com/agno-ai/agno) (`>=1.0.0`): The fundamental framework for building and managing AI agents.
*   **LLM Integration:**
    *   [`openai`](https://github.com/openai/openai-python) (`>=1.12.0`): For `OpenAIChat` model integration, compatible with OpenRouter.
    *   [`google-genai`](https://github.com/google/generative-ai-python) (`>=1.0.0`): For `Gemini` model integration.
*   **Web UI Framework:**
    *   [`streamlit`](https://github.com/streamlit/streamlit) (`>=1.31.0`): Powers the interactive web-based graphical user interface.
*   **CLI Enhancements:**
    *   [`rich`](https://github.com/Textualize/rich) (`>=13.7.0`): For beautiful and informative console output, progress bars, and prompts.
*   **Configuration & Data Management:**
    *   [`python-dotenv`](https://github.com/theskumar/python-dotenv) (`>=1.0.1`): Loads environment variables from `.env` files.
    *   [`pydantic`](https://github.com/pydantic/pydantic) (`>=2.6.0`): Data validation and settings definition.
    *   [`pydantic-settings`](https://github.com/pydantic/pydantic-settings) (`>=2.0.0`): Extends Pydantic for robust environment and configuration management.
*   **Version Control Interaction:**
    *   [`gitpython`](https://github.com/gitpython-developers/GitPython) (`>=3.1.40`): Programmatic interface for Git repositories.

---

## 🏗️ System Architecture

```text
User Input
     │
     ▼
GitHub Repository URL
     │
     ▼
Repository Cloning
     │
     ▼
Repository Scanner
     │
     ▼
Context Extraction
     │
     ▼
┌─────────────────────────┐
│ Repository Analyzer AI │
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐
│ Documentation Writer   │
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐
│ README Reviewer Agent  │
└──────────┬──────────────┘
           ▼
      README.md Output
```

---

## 📂 Project Structure

```text
AI-Github-README-Generator/
│
├── app.py
├── agents.py
├── config.py
├── utils.py
├── requirements.txt
├── .env
├── temp_clones/
└── README.md
```

---


## 🚀 Installation

### Clone Repository

```bash
git clone https://github.com/your-username/ai-github-readme-generator.git

cd ai-github-readme-generator
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / macOS

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file:

```env
OPENROUTER_API_KEY=your_api_key

OPENROUTER_MODEL=moonshotai/kimi-k2.5

TEMP_CLONE_DIR=./temp_clones
```

---

## ▶️ Run Application

```bash
streamlit run app.py
```

Application will be available at:

```text
http://localhost:8501
```

---

## 💡 Usage

### Step 1

Launch the application.

### Step 2

Enter a GitHub repository URL.

Example:

```text
https://github.com/streamlit/streamlit
```

### Step 3

Provide your API key.

### Step 4

Choose your preferred model.

### Step 5

Click **Generate README**.

### Step 6

Receive a complete, production-ready README file.

---

## 🎯 Example Use Cases

### Open Source Projects
Generate professional documentation instantly.

### Student Projects
Create polished README files for portfolios and academic submissions.

### Freelance Development
Deliver well-documented projects to clients.

### Startups
Maintain consistent documentation standards across repositories.

---

## 🔒 Security

- API keys are handled securely through the UI.
- Repository data is processed temporarily.
- No permanent storage of cloned repositories.
- Compatible with Streamlit Secrets for production deployment.

---

## 🤝 Contributing

We welcome contributions to the AI-Powered README Generator! Whether it's feature requests, bug reports, or code contributions, your help is valuable.

1. Fork the repository

2. Create a feature branch

```bash
git checkout -b feature/new-feature
```

3. Commit changes

```bash
git commit -m "Add new feature"
```

4. Push changes

```bash
git push origin feature/new-feature
```

5. Open a Pull Request

---

## 👨‍💻 Author

**Jitendra Singh**

AI/ML Enthusiast | Generative AI Developer | Agentic AI Builder

---

### ⭐ Star this repository if you found it useful!
