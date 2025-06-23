#!/usr/bin/env python
"""
Setup script for ROAR CRM
Creates profiles for users and ensures a supervisor exists
"""
import os
import sys

if __name__ == "__main__":
    # Add the current directory to the path so we can import settings
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    import utils
    
    # Setup Django environment
    utils.setup_django()
    
    # Create user profiles
    utils.create_or_update_profiles()
    
    # Ensure supervisor exists
    utils.ensure_supervisor_exists()
    
    print("Setup complete!")
