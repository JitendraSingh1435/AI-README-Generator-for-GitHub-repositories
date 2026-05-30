import os
import shutil
import sys
from pathlib import Path
import streamlit as st

# Add current dir to path to ensure local imports work
sys.path.append(str(Path(__file__).parent.resolve()))

from config import settings
from utils import clone_repository, generate_dir_tree, extract_project_context
from agents import run_readme_generator_workflow

# Configure Streamlit page layout and theme
st.set_page_config(
    page_title="AI Readme Generator",
    page_icon="▲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styles (Glassmorphism & Harmonious Gradients)
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Space+Grotesk:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
}

/* Gradient Header */
.main-header {
    background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700;
    font-size: 3rem !important;
    margin-bottom: 0px;
    font-family: 'Space Grotesk', sans-serif;
}

.sub-header {
    color: #8892b0;
    font-size: 1.1rem;
    margin-bottom: 2.5rem;
}

/* Glassmorphism Cards */
.glass-card {
    background: rgba(17, 25, 40, 0.5);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}

/* Custom Tree Codebox */
.tree-code {
    background-color: #0f141c;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    padding: 1rem;
    font-family: 'Courier New', Courier, monospace;
    font-size: 0.9rem;
    overflow-x: auto;
    max-height: 350px;
}

/* Status Steps */
.status-badge {
    background-color: rgba(0, 242, 254, 0.1);
    color: #00f2fe;
    border: 1px solid rgba(0, 242, 254, 0.2);
    border-radius: 4px;
    padding: 0.2rem 0.6rem;
    font-size: 0.8rem;
    font-weight: 600;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Helper function to check configuration
def check_config_state(key):
    return bool(key and not key.startswith("your_"))

# Sidebar Configuration
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/database.png", width=65)
    st.markdown("<h2 style='font-family: Space Grotesk; margin-bottom: 0px;'>Settings</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #8892b0; font-size: 0.85rem; margin-bottom: 1.5rem;'>Configure your agent parameters</p>", unsafe_allow_html=True)
    
    # API key loader
    default_key = settings.OPENROUTER_API_KEY if check_config_state(settings.OPENROUTER_API_KEY) else ""
    openrouter_api_key = st.text_input(
        "LLM API Key (OpenRouter / Google Gemini)",
        value=default_key,
        type="password",
        help="Input your OpenRouter API Key (starts with sk-or-) or Google Gemini API Key (starts with AIzaSy)."
    )
    
    # Detect provider
    is_gemini = openrouter_api_key.strip().startswith("AIzaSy")
    
    # Model Selection
    if is_gemini:
        model_options = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-2.5-pro",
            "gemini-3.5-flash"
        ]
        model_label = "Google Gemini Model"
        model_help = "Select the specific Gemini model variant to generate documentation."
        default_model_display = "gemini-2.5-flash"
    else:
        model_options = [
            "moonshotai/kimi-k2.5",
            "moonshotai/kimi-k2.6",
            "moonshotai/kimi-k2-thinking",
            "moonshotai/kimi-k2"
        ]
        model_label = "Moonshot Kimi Model"
        model_help = "Select the specific Kimi model variant to generate documentation."
        default_model_display = "Kimi-k2.5"
        
    model_name = st.selectbox(
        model_label,
        options=model_options,
        index=0,
        help=model_help
    )
    
    # Advanced / Custom models
    custom_model_toggle = st.checkbox("Use custom model ID")
    if custom_model_toggle:
        model_name = st.text_input("Enter Model ID", value=model_name)
        
    st.markdown("---")
    st.markdown("### 🏷️ System Metadata")
    st.markdown(f"**Agno Engine**: v1.0+")
    st.markdown(f"**Provider**: `Google Gemini`" if is_gemini else f"**Provider**: `OpenRouter`")
    st.markdown(f"**Default Model**: `{default_model_display}`")
    
    # Status Indicators
    if openrouter_api_key:
        if is_gemini:
            st.success("🔑 Gemini API Key Active")
        else:
            st.success("🔑 OpenRouter API Key Active")
    else:
        st.warning("⚠️ API Key Missing")

# Main Interface
st.markdown("<h1 class='main-header'>▲ AI README GENERATOR</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Agentic AI codebase scanner & README markdown documentation architect.</p>", unsafe_allow_html=True)

# Form Section

col1, col2 = st.columns([3, 1])

with col1:
    repo_url = st.text_input(
        "🌐 GitHub Repository URL",
        placeholder="https://github.com/username/project-repo",
        help="Enter a public GitHub repository link."
    )
with col2:
    custom_name = st.text_input(
        "📁 File Output Name",
        value="README.md",
        help="The name of the file downloaded at completion."
    )

custom_instructions = st.text_area(
    "✍️ Custom Instructions (Optional)",
    placeholder="Example: Keep instructions optimized for Windows users. Make sure to detail deployment settings to AWS ECS. Focus highly on the testing section.",
    height=100
)

# Action Trigger
generate_btn = st.button("🚀 Generate README.md Documentation", use_container_width=True)

if generate_btn:
    if not openrouter_api_key:
        st.error("🔑 Please set your LLM API Key in the sidebar settings first!")
    elif not repo_url.strip():
        st.error("🌐 Please enter a valid GitHub repository URL!")
    else:
        # Initializing temp paths
        temp_dir = Path(settings.TEMP_CLONE_DIR) / "streamlit_temp"
        
        # Displaying real-time steps progress
        status_box = st.empty()
        progress_bar = st.progress(0.0)
        
        try:
            # 1. Cloning Phase
            status_box.info("📥 [1/4] Cloning repository to server...")
            progress_bar.progress(0.2)
            clone_path = clone_repository(repo_url, str(temp_dir))
            
            # 2. Scanning Phase
            status_box.info("🔍 [2/4] Traversing file tree & extracting configuration metadata...")
            progress_bar.progress(0.4)
            repo_tree = generate_dir_tree(clone_path)
            context_data = extract_project_context(clone_path)
            
            # 3. Agent Execution Callback Setup
            def on_agent_progress(message: str, completion_percentage: float):
                # Scale from 0.4 to 0.95
                scaled_prog = 0.4 + (completion_percentage * 0.55)
                status_box.info(f"🤖 [3/4] Agentic Workflow: {message}")
                progress_bar.progress(scaled_prog)

            # 4. Agent Pipeline Execution
            final_readme = run_readme_generator_workflow(
                repo_tree=repo_tree,
                context_data=context_data,
                api_key=openrouter_api_key,
                model_name=model_name,
                custom_instructions=custom_instructions,
                progress_callback=on_agent_progress
            )
            
            # 5. Success State
            status_box.success("🎉 [4/4] Documentation generated successfully!")
            progress_bar.progress(1.0)
            
            st.toast("Success! Scroll down to view documentation.", icon="🎉")
            st.markdown("---")
            
            # Display Results Layout
            res_col1, res_col2 = st.columns([1, 2])
            
            with res_col1:
                st.markdown("### 📁 Codebase Directory Tree")
                st.markdown(f"<pre class='tree-code'>{repo_tree}</pre>", unsafe_allow_html=True)
                
                # Show quick scanning metadata panel
                st.markdown("#### ⚙️ Scanner Metadata")
                st.info(context_data.get("summary", "No details gathered."))
                
            with res_col2:
                st.markdown("### 📄 Generated README.md")
                
                tab_preview, tab_raw = st.tabs(["✨ Markdown Preview", "💻 Raw Markdown Code"])
                
                with tab_preview:
                    st.markdown(final_readme)
                    
                with tab_raw:
                    st.code(final_readme, language="markdown")
                    
                # Download Button
                st.download_button(
                    label="📥 Download README.md",
                    data=final_readme,
                    file_name=custom_name,
                    mime="text/markdown",
                    use_container_width=True
                )
                
        except Exception as e:
            st.error(f"❌ Error during generation: {str(e)}")
            
        finally:
            # Clean up temp clones directory
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
