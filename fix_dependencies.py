#!/usr/bin/env python3
"""
This script fixes dependency issues by reinstalling them in the correct order.
"""

import subprocess
import sys

def run_command(command):
    """Run a shell command and print the output."""
    print(f"Running: {command}")
    process = subprocess.Popen(
        command, 
        shell=True, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT
    )
    
    # Print output in real-time
    for line in iter(process.stdout.readline, b''):
        sys.stdout.write(line.decode('utf-8'))
    
    process.wait()
    return process.returncode

def main():
    """Main function to fix dependencies."""
    print("Fixing dependencies for Alpaca Trading...")
    
    # First, uninstall problematic packages
    packages_to_uninstall = [
        "alpaca-py",
        "pandas",
        "numpy"
    ]
    
    for package in packages_to_uninstall:
        run_command(f"pip uninstall -y {package}")
    
    # Then install them in the correct order
    run_command("pip install numpy==1.24.3")
    run_command("pip install pandas==2.0.3")
    run_command("pip install alpaca-py==0.8.2")
    
    print("\nDependencies fixed successfully!")
    print("You can now run the application using:")
    print("python -m alpaca_trader.official")

if __name__ == "__main__":
    main() 