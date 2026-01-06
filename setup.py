"""
Prometheus Setup Script
Automated installation and configuration
"""

import os
import subprocess
import sys
import platform

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def run_command(command, cwd=None):
    """Run shell command"""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_python_version():
    """Check Python version"""
    print_header("Checking Python Version")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.10+)")
        return False

def check_node():
    """Check Node.js installation"""
    print_header("Checking Node.js")
    success, output = run_command("node --version")
    if success:
        print(f"✅ Node.js {output.strip()} (OK)")
        return True
    else:
        print("❌ Node.js not found. Please install Node.js 18+")
        return False

def check_ollama():
    """Check Ollama installation"""
    print_header("Checking Ollama")
    success, output = run_command("ollama --version")
    if success:
        print(f"✅ Ollama {output.strip()} (OK)")
        return True
    else:
        print("⚠️  Ollama not found. Install from https://ollama.ai")
        return False

def setup_backend():
    """Setup backend dependencies"""
    print_header("Setting Up Backend")
    
    backend_path = os.path.join("prometheus-ui", "backend")
    
    # Create virtual environment
    print("Creating virtual environment...")
    venv_path = ".venv" if platform.system() == "Windows" else "venv"
    success, _ = run_command(f"python -m venv {venv_path}")
    
    if not success:
        print("❌ Failed to create virtual environment")
        return False
    
    # Determine pip path
    if platform.system() == "Windows":
        pip_path = os.path.join(".venv", "Scripts", "pip")
    else:
        pip_path = os.path.join("venv", "bin", "pip")
    
    # Install requirements
    print("Installing Python dependencies...")
    requirements_path = os.path.join(backend_path, "requirements.txt")
    success, output = run_command(f"{pip_path} install -r {requirements_path}")
    
    if success:
        print("✅ Backend dependencies installed")
        return True
    else:
        print(f"❌ Failed to install dependencies:\n{output}")
        return False

def setup_frontend():
    """Setup frontend dependencies"""
    print_header("Setting Up Frontend")
    
    frontend_path = os.path.join("prometheus-ui", "frontend")
    
    print("Installing Node dependencies...")
    success, output = run_command("npm install", cwd=frontend_path)
    
    if success:
        print("✅ Frontend dependencies installed")
        return True
    else:
        print(f"❌ Failed to install dependencies:\n{output}")
        return False

def check_ollama_model():
    """Check if Llama model is installed"""
    print_header("Checking Ollama Models")
    
    success, output = run_command("ollama list")
    if success and "llama3.1:8b" in output:
        print("✅ Llama 3.1 8B model found")
        return True
    else:
        print("⚠️  Llama 3.1 8B model not found")
        print("   Run: ollama pull llama3.1:8b")
        return False

def create_env_file():
    """Create .env file if not exists"""
    print_header("Creating Environment File")
    
    env_path = os.path.join("prometheus-ui", "backend", ".env")
    
    if os.path.exists(env_path):
        print("✅ .env file already exists")
        return True
    
    env_content = """# Prometheus Environment Configuration

# Ollama
OLLAMA_BASE_URL=http://localhost:11434

# Database
DATABASE_PATH=prometheus.db
CHROMA_PATH=chroma_db

# Logging
LOG_LEVEL=INFO

# Server
HOST=0.0.0.0
PORT=8000
"""
    
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env: {e}")
        return False

def print_next_steps():
    """Print next steps"""
    print_header("Setup Complete!")
    
    print("""
🎉 Prometheus is ready to run!

Next Steps:

1. Start Ollama (if not running):
   ollama serve

2. Pull Llama model (if needed):
   ollama pull llama3.1:8b

3. Start Backend:
   cd prometheus-ui/backend
   
   # Windows:
   .venv\\Scripts\\activate
   python main.py
   
   # Linux/Mac:
   source venv/bin/activate
   python main.py
   
   Backend: http://localhost:8000

4. Start Frontend (in new terminal):
   cd prometheus-ui/frontend
   npm run dev
   
   Frontend: http://localhost:3000

5. Open browser:
   http://localhost:3000
   
   Default login:
   Username: demo
   Password: demo123

📚 Documentation: docs/
🐛 Issues: GitHub Issues
⭐ Star the repo if you like it!

Happy querying! 🚀
""")

def main():
    """Main setup flow"""
    print("""
╔══════════════════════════════════════════════════════════╗
║          PROMETHEUS - Setup & Installation               ║
║      Multilingual Startup RAG System                     ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    checks_passed = True
    
    # Check prerequisites
    if not check_python_version():
        checks_passed = False
    
    if not check_node():
        checks_passed = False
    
    check_ollama()  # Warning only
    
    if not checks_passed:
        print("\n❌ Prerequisites check failed. Please install missing components.\n")
        return False
    
    # Setup components
    if not setup_backend():
        print("\n❌ Backend setup failed.\n")
        return False
    
    if not setup_frontend():
        print("\n❌ Frontend setup failed.\n")
        return False
    
    # Additional setup
    create_env_file()
    check_ollama_model()
    
    # Success
    print_next_steps()
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}\n")
        sys.exit(1)
