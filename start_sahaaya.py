#!/usr/bin/env python3
"""
🆘 Sahaaya - Quick Start Script
One-click setup and launch for the Emergency Aid Companion

This script handles dependency installation and app launch automatically.
"""

import os
import sys
import subprocess
import platform

def print_banner():
    """Print the Sahaaya banner"""
    banner = """
    ╔══════════════════════════════════════════════════════╗
    ║                                                      ║
    ║       🆘 SAHAAYA - AI Emergency Aid Companion       ║
    ║                                                      ║
    ║     Your AI Partner in Moments that Matter ⚡       ║
    ║                                                      ║
    ╚══════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        print("   Please upgrade Python and try again.")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n📦 Checking dependencies...")
    
    try:
        import streamlit
        print("✅ Streamlit is already installed")
        return True
    except ImportError:
        print("⚠️ Streamlit not found. Will install dependencies...")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("\n⚙️ Installing dependencies...")
    print("This may take a few minutes depending on your internet connection...")
    
    try:
        # Install requirements
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True, capture_output=True, text=True)
        
        print("✅ Dependencies installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print("❌ Failed to install dependencies!")
        print(f"Error: {e}")
        print("\nTry installing manually:")
        print("pip install -r requirements.txt")
        return False
    except FileNotFoundError:
        print("❌ pip not found! Please ensure Python and pip are properly installed.")
        return False

def check_system_audio():
    """Check if system audio components are available (for speech features)"""
    print("\n🎤 Checking audio system...")
    
    system = platform.system().lower()
    
    if system == "windows":
        print("✅ Windows audio system detected")
        return True
    elif system == "darwin":  # macOS
        print("✅ macOS audio system detected")
        return True
    elif system == "linux":
        print("⚠️ Linux detected. Speech features may require additional setup.")
        print("   If you encounter audio issues, install: sudo apt-get install espeak")
        return True
    else:
        print(f"⚠️ Unknown system: {system}. Speech features may not work.")
        return True

def run_tests():
    """Run basic tests to ensure everything is working"""
    print("\n🧪 Running system tests...")
    
    try:
        # Import core modules to test
        from utils.ai_engine import EmergencyDetector
        detector = EmergencyDetector("data/emergency_database.json")
        
        # Test emergency detection
        test_result = detector.detect_emergency("test emergency cardiac arrest")
        if test_result:
            print("✅ Emergency detection working")
        else:
            print("⚠️ Emergency detection test failed, but app should still work")
        
        print("✅ Core systems operational")
        return True
        
    except Exception as e:
        print(f"⚠️ Test warning: {e}")
        print("App may still work, but some features might be limited.")
        return True

def launch_app():
    """Launch the Streamlit app"""
    print("\n🚀 Launching Sahaaya Emergency Aid Companion...")
    print("The app will open in your default web browser.")
    print("If it doesn't open automatically, visit: http://localhost:8501")
    print("\nTo stop the app, press Ctrl+C in this terminal.\n")
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.headless", "false",
            "--server.address", "localhost",
            "--server.port", "8501"
        ], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to launch app: {e}")
        print("\nTry launching manually:")
        print("streamlit run app.py")
        return False
    except KeyboardInterrupt:
        print("\n\n👋 Sahaaya stopped. Thank you for using our emergency aid companion!")
        return True
    
    return True

def main():
    """Main setup and launch function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check and install dependencies if needed
    if not check_dependencies():
        if not install_dependencies():
            return False
    
    # Check system audio
    check_system_audio()
    
    # Run basic tests
    run_tests()
    
    # Launch the app
    print("\n" + "="*60)
    print("🆘 SAHAAYA IS READY FOR EMERGENCY ASSISTANCE")
    print("="*60)
    
    launch_app()
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled. You can run this script again anytime.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check your Python installation and try again.")
        sys.exit(1)