import json
from typing import Any
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.google import Gemini
from config import settings

def get_llm_model(api_key: str = None, model_name: str = None) -> Any:
    """
    Returns an Agno model instance configured for OpenRouter (OpenAIChat) or Google Gemini (Gemini).
    """
    key = api_key or settings.OPENROUTER_API_KEY
    
    if not key:
        raise ValueError(
            "API Key is missing! Please configure the key in your .env file or pass it directly."
        )
        
    # Auto-detect Google Gemini vs OpenRouter based on key prefix (Gemini keys start with AIzaSy)
    if key.strip().startswith("AIzaSy"):
        # Default Gemini model if not specified or if an OpenRouter model was passed
        if not model_name or "kimi" in model_name:
            model = settings.GEMINI_MODEL
        else:
            model = model_name
            
        return Gemini(
            id=model,
            api_key=key.strip(),
        )
    else:
        # Default OpenRouter model if not specified or if a Gemini model was passed
        if not model_name or "gemini" in model_name:
            model = settings.OPENROUTER_MODEL
        else:
            model = model_name
        
        return OpenAIChat(
            id=model,
            api_key=key.strip(),
            base_url=settings.OPENROUTER_BASE_URL,
        )

# Alias for backwards compatibility
get_openrouter_model = get_llm_model

def get_analyzer_agent(model: Any) -> Agent:
    """
    Creates and returns the Codebase Analyzer Agent.
    """
    return Agent(
        model=model,
        markdown=True,
        instructions=[
            "You are a Senior Principal Code Architect and Repository Analyst.",
            "Your goal is to perform a deep-dive analysis of a codebase's files, configurations, and tree structure.",
            "Identify:",
            "  1. The core programming languages, frameworks, and library dependencies used.",
            "  2. The project's overall architectural design pattern.",
            "  3. The main entry point files and how they orchestrate the app.",
            "  4. A concise summary of the purpose and utility of each major module/directory.",
            "Provide a highly technical, factual summary of your findings. Do not write a README yet, just analyze the repository."
        ]
    )

def get_writer_agent(model: Any) -> Agent:
    """
    Creates and returns the Documentation Writer Agent.
    """
    return Agent(
        model=model,
        markdown=True,
        instructions=[
            "You are a Technical Documentation Engineer specializing in open-source software.",
            "Your goal is to generate a comprehensive, highly styled, and fully structured README.md.",
            "Utilize the directory tree and the codebase analysis to write the README.",
            "The README should include the following sections:",
            "  - **Title / Header**: Include a catchy, clear name and a professional description.",
            "  - **Aesthetics & Badges**: Add standard GitHub shields/badges (e.g., build status, license, language, version).",
            "  - **Key Features**: A detailed, bulleted list of what the project does.",
            "  - **Tech Stack**: A clean list/table of core technologies used (frameworks, databases, libraries).",
            "  - **Directory Structure**: Embed the ASCII tree and briefly explain major directories/files.",
            "  - **Getting Started**: Clear step-by-step setup, dependency installation, and running instructions.",
            "  - **Usage**: Detailed examples or commands demonstrating how to use the project.",
            "  - **API Reference (if applicable)**: Document key endpoints, functions, or configurations.",
            "  - **Contributing**: Standard instructions on how to contribute.",
            "  - **License**: Placeholders or common licenses (MIT, Apache, etc.).",
            "Ensure the tone is professional, inviting, and highly informative. Avoid placeholders where actual info is available."
        ]
    )

def get_qa_agent(model: Any) -> Agent:
    """
    Creates and returns the Quality Assurance / Editor Agent.
    """
    return Agent(
        model=model,
        markdown=True,
        instructions=[
            "You are an Elite Open-Source Editor and QA Specialist.",
            "Your job is to read a generated README.md draft, refine it, polish the syntax, fix layout issues, and ensure maximum visual impact.",
            "Guidelines:",
            "  1. Ensure headings (`#`, `##`, `###`) are perfectly nested and logical.",
            "  2. Add subtle styling elements, such as emoji tags, clean code blocks, and markdown tables to make it look premium.",
            "  3. Check that the installations and commands align exactly with the technology stack (e.g., don't suggest npm install for a Python project).",
            "  4. Fix any broken links, unclosed markdown tags, or typos.",
            "Output ONLY the finalized README.md markdown text. Do not add introductory or concluding chatter (e.g., 'Here is your polished README:')."
        ]
    )

def run_readme_generator_workflow(
    repo_tree: str,
    context_data: dict,
    api_key: str = None,
    model_name: str = None,
    custom_instructions: str = None,
    progress_callback=None
) -> str:
    """
    Runs the agentic workflow sequentially:
    Analyzer -> Writer -> QA Editor
    Returns the final polished README markdown.
    """
    # 1. Initialize the OpenRouter model client
    model = get_openrouter_model(api_key, model_name)
    
    # Format files data nicely for agents
    config_details = "\n\n".join([f"### File: {path}\n```\n{content}\n```" for path, content in context_data.get("config_files", {}).items()])
    entry_details = "\n\n".join([f"### File: {path}\n```\n{content}\n```" for path, content in context_data.get("entry_files", {}).items()])
    summary_meta = context_data.get("summary", "")

    # Combine technical inputs for the Analyzer
    analyzer_prompt = f"""
    Please analyze the following codebase details:
    
    [SCAN METADATA]
    {summary_meta}
    
    [DIRECTORY TREE]
    ```text
    {repo_tree}
    ```
    
    [CONFIGURATION FILES]
    {config_details}
    
    [ENTRYPOINT FILES]
    {entry_details}
    """

    # --- Phase 1: Codebase Analysis ---
    if progress_callback:
        progress_callback("Analyzing codebase structure and configurations...", 0.3)
    
    analyzer_agent = get_analyzer_agent(model)
    analysis_response = analyzer_agent.run(analyzer_prompt)
    analysis_report = analysis_response.content

    # --- Phase 2: Documentation Drafting ---
    if progress_callback:
        progress_callback("Drafting initial README markdown...", 0.6)
        
    writer_prompt = f"""
    You are given a Codebase Analysis Report and the Directory Tree.
    Generate an outstanding, comprehensive README.md file.
    
    [DIRECTORY TREE]
    ```text
    {repo_tree}
    ```
    
    [ANALYSIS REPORT]
    {analysis_report}
    """
    
    if custom_instructions:
        writer_prompt += f"\n\n[USER CUSTOM INSTRUCTIONS]\n{custom_instructions}"

    writer_agent = get_writer_agent(model)
    draft_response = writer_agent.run(writer_prompt)
    draft_readme = draft_response.content

    # --- Phase 3: QA Review & Polishing ---
    if progress_callback:
        progress_callback("Polishing documentation and validating layout...", 0.9)

    qa_prompt = f"""
    Please review, polish, and output the final version of the following README.md draft:
    
    [DRAFT README]
    {draft_readme}
    """
    
    qa_agent = get_qa_agent(model)
    final_response = qa_agent.run(qa_prompt)
    
    if progress_callback:
        progress_callback("README generated successfully!", 1.0)
        
    return final_response.content
