import subprocess
import sys
import os
import time

def main():
    # Get the directory where this script is located
    base_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(base_dir, "frontend")
    
    print("🔥 Starting PROMETHEUS...")
    print("=" * 50)
    
    # Start FastAPI backend
    print("\n📡 Starting API server on http://localhost:8000...")
    api_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=base_dir
    )
    
    # Wait a bit for API to start
    time.sleep(3)
    
    # Start React frontend
    print("\n🌐 Starting React frontend on http://localhost:3000...")
    print("Note: First run may take a while to install dependencies...\n")
    
    try:
        # Check if node_modules exists
        if not os.path.exists(os.path.join(frontend_dir, "node_modules")):
            print("📦 Installing frontend dependencies...")
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        
        frontend_process = subprocess.Popen(
            ["npm", "start"],
            cwd=frontend_dir,
            shell=True
        )
        
        print("\n" + "=" * 50)
        print("✅ PROMETHEUS is running!")
        print("API: http://localhost:8000")
        print("Frontend: http://localhost:3000")
        print("Press Ctrl+C to stop both servers")
        print("=" * 50)
        
        # Wait for processes
        api_process.wait()
        frontend_process.wait()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down PROMETHEUS...")
        api_process.terminate()
        frontend_process.terminate()
        print("✅ Servers stopped successfully")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        api_process.terminate()
        if 'frontend_process' in locals():
            frontend_process.terminate()

if __name__ == "__main__":
    main()
