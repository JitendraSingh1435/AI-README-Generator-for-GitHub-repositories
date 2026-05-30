import os
import shutil
import sys
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.status import Status
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

# Add current dir to path to ensure local imports work
sys.path.append(str(Path(__file__).parent.resolve()))

from config import settings
from utils import clone_repository, generate_dir_tree, extract_project_context
from agents import run_readme_generator_workflow

console = Console()

def display_welcome_banner():
    """
    Renders an elegant dashboard welcome banner.
    """
    banner_text = (
        "[bold cyan]▲ AGENTIC AI README GENERATOR ▲[/bold cyan]\n"
        "[dim]Powered by Agno Agents, GitPython, Moonshot Kimi (OpenRouter) & Google Gemini[/dim]"
    )
    console.print(Panel(banner_text, border_style="cyan", expand=False))

def ensure_env_setup():
    """
    Verifies that the LLM API Key (OpenRouter or Google Gemini) is set. 
    If not, prompts the user to enter it and saves it to a new .env file.
    """
    env_file = Path(__file__).parent / ".env"
    
    if not settings.is_api_key_configured:
        console.print("\n[yellow]⚠️  LLM API Key is not configured in environment variables or .env file.[/yellow]")
        api_key = Prompt.ask("[bold green]🔑 Please enter your LLM API Key (OpenRouter or Google Gemini)[/bold green]")
        
        if api_key.strip():
            # Auto-detect default model based on key prefix
            is_gemini = api_key.strip().startswith("AIzaSy")
            default_model = settings.GEMINI_MODEL if is_gemini else settings.OPENROUTER_MODEL
            
            # Write a new .env file
            with open(env_file, "w", encoding="utf-8") as f:
                f.write(f"OPENROUTER_API_KEY={api_key.strip()}\n")
                f.write(f"OPENROUTER_MODEL={default_model}\n")
                f.write(f"TEMP_CLONE_DIR={settings.TEMP_CLONE_DIR}\n")
            
            # Reload settings
            load_dotenv(dotenv_path=env_file, override=True)
            settings.OPENROUTER_API_KEY = api_key.strip()
            settings.OPENROUTER_MODEL = default_model
            provider_name = "Google Gemini" if is_gemini else "OpenRouter"
            console.print(f"[green]✓ Successfully saved {provider_name} API Key and configured default model to {default_model} in .env file![/green]\n")
        else:
            console.print("[bold red]Error: API Key is required to run the AI agents. Exiting.[/bold red]")
            sys.exit(1)

def main():
    display_welcome_banner()
    ensure_env_setup()

    # Step 1: Get user inputs
    repo_url = Prompt.ask("[bold white]🌐 Enter GitHub Repository URL[/bold white]")
    if not repo_url.startswith(("http://", "https://", "git@")):
        console.print("[bold red]Error: Please enter a valid Git URL.[/bold red]")
        sys.exit(1)
        
    custom_inst = Prompt.ask("[bold white]✍️ Enter any custom instructions/guidelines for the README (Optional)[/bold white]", default="")
    
    output_filename = Prompt.ask("[bold white]📁 Enter target output path[/bold white]", default="README_GENERATED.md")

    # Step 2: Define temp directories
    temp_dir = Path(settings.TEMP_CLONE_DIR) / "cli_temp"
    
    try:
        # Run workflow with progress spinner
        with Progress(
            SpinnerColumn("dots12", style="cyan"),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=30, style="dim", complete_style="cyan"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            # Clone Phase
            task_id = progress.add_task("[cyan]Cloning GitHub repository...", total=100)
            clone_path = clone_repository(repo_url, str(temp_dir))
            progress.update(task_id, description="[cyan]Repository cloned successfully!", completed=30)
            
            # Scanning Phase
            progress.update(task_id, description="[cyan]Scanning repository files & config...", completed=40)
            repo_tree = generate_dir_tree(clone_path)
            context_data = extract_project_context(clone_path)
            progress.update(task_id, description="[cyan]Structure parsed, contexts extracted!", completed=50)

            # Define a progress reporting callback for agents
            def agent_progress_callback(msg: str, completion_percentage: float):
                scaled_progress = 50 + int(completion_percentage * 50)
                progress.update(task_id, description=f"[cyan]{msg}", completed=scaled_progress)

            # Agent AI Generation Phase
            final_readme = run_readme_generator_workflow(
                repo_tree=repo_tree,
                context_data=context_data,
                api_key=settings.OPENROUTER_API_KEY,
                model_name=settings.OPENROUTER_MODEL,
                custom_instructions=custom_inst,
                progress_callback=agent_progress_callback
            )
            
        # Step 3: Write Output File
        out_path = Path(output_filename).resolve()
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(final_readme)

        # Print Success Details
        console.print(Panel(
            f"[bold green]✨ AI README GENERATION COMPLETED SUCCESSFULLY! ✨[/bold green]\n\n"
            f"[bold white]Output File:[/bold white] [underline cyan]{out_path}[/underline cyan]\n"
            f"[dim]The temporary workspace clone was fully cleaned up.[/dim]",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"\n[bold red]❌ Critical Error Occurred:[/bold red] {str(e)}")
        
    finally:
        # Step 4: Cleanup cloned directories
        if temp_dir.exists():
            with console.status("[yellow]Cleaning up temporary workspace clones...[/yellow]"):
                shutil.rmtree(temp_dir, ignore_errors=True)
            console.print("[dim green]Cleanup finished.[/dim green]")

if __name__ == "__main__":
    main()
