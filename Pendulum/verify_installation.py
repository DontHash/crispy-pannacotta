#!/usr/bin/env python3
"""
Pendulum Simulation - Installation Verification Script
Tests all components to ensure the project is properly set up
"""

import sys
import importlib
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 7:
        print("✓ Python version OK\n")
        return True
    else:
        print("✗ Python 3.7+ required\n")
        return False

def check_imports():
    """Check if all required libraries can be imported"""
    packages = {
        'OpenGL': 'PyOpenGL',
        'OpenGL.GL': 'PyOpenGL (GL)',
        'OpenGL.GLU': 'PyOpenGL (GLU)',
        'OpenGL.GLUT': 'PyGLUT',
        'numpy': 'NumPy',
    }
    
    all_ok = True
    for module_name, display_name in packages.items():
        try:
            importlib.import_module(module_name)
            print(f"✓ {display_name:30} - OK")
        except ImportError as e:
            print(f"✗ {display_name:30} - MISSING: {e}")
            all_ok = False
    
    print()
    return all_ok

def check_project_files():
    """Check if all project files exist"""
    project_root = Path(__file__).parent
    
    required_files = [
        'main.py',
        'config.py',
        'requirements.txt',
        'physics/pendulum.py',
        'physics/__init__.py',
        'graphics/renderer.py',
        'graphics/__init__.py',
        'utils/helpers.py',
        'utils/__init__.py',
    ]
    
    all_ok = True
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"✓ {file_path:40} - {size:>8} bytes")
        else:
            print(f"✗ {file_path:40} - MISSING")
            all_ok = False
    
    print()
    return all_ok

def check_module_imports():
    """Check if project modules can be imported"""
    try:
        import config
        print("✓ config module           - OK")
    except Exception as e:
        print(f"✗ config module           - ERROR: {e}")
        return False
    
    try:
        from physics import Pendulum
        print("✓ physics.Pendulum        - OK")
    except Exception as e:
        print(f"✗ physics.Pendulum        - ERROR: {e}")
        return False
    
    try:
        from graphics import Renderer
        print("✓ graphics.Renderer       - OK")
    except Exception as e:
        print(f"✗ graphics.Renderer       - ERROR: {e}")
        return False
    
    try:
        from utils import Timer, FrameRateLimiter, DataRecorder, PhysicsValidator
        print("✓ utils (all classes)     - OK")
    except Exception as e:
        print(f"✗ utils classes           - ERROR: {e}")
        return False
    
    print()
    return True

def check_physics_engine():
    """Verify physics engine functionality"""
    try:
        from physics import Pendulum
        import config
        
        # Create a pendulum instance
        pend = Pendulum(
            length=config.PENDULUM_LENGTH,
            mass=config.BOB_MASS,
            gravity=config.GRAVITY,
            initial_angle=config.INITIAL_ANGLE,
            damping=config.DAMPING_COEFFICIENT
        )
        
        # Test a few physics calculations
        pend.update(0.001)
        pos = pend.get_bob_position(0, 0)
        vel = pend.get_bob_velocity()
        energy = pend.get_energy()
        
        print(f"✓ Pendulum creation       - OK")
        print(f"✓ Physics update          - OK")
        print(f"✓ Position calculation    - OK ({pos[0]:.4f}, {pos[1]:.4f})")
        print(f"✓ Velocity calculation    - OK ({vel[0]:.4f}, {vel[1]:.4f})")
        print(f"✓ Energy calculation      - OK (Total: {energy[0]:.6f} J)")
        print()
        return True
        
    except Exception as e:
        print(f"✗ Physics engine test     - ERROR: {e}")
        print()
        return False

def main():
    """Run all verification tests"""
    print_header("PENDULUM SIMULATION - INSTALLATION VERIFICATION")
    
    results = []
    
    print("1. Python Version Check:")
    results.append(check_python_version())
    
    print("2. Required Packages Check:")
    results.append(check_imports())
    
    print("3. Project Files Check:")
    results.append(check_project_files())
    
    print("4. Module Import Check:")
    results.append(check_module_imports())
    
    print("5. Physics Engine Check:")
    results.append(check_physics_engine())
    
    # Summary
    print_header("VERIFICATION SUMMARY")
    
    if all(results):
        print("✓ ALL CHECKS PASSED!")
        print("\nThe project is properly installed and ready to use.")
        print("\nTo run the simulation:")
        print("  python main.py")
        print()
        return 0
    else:
        print("✗ SOME CHECKS FAILED")
        print("\nPlease fix the issues listed above.")
        print("\nFor help, see INSTALL.md")
        print()
        return 1

if __name__ == '__main__':
    sys.exit(main())
