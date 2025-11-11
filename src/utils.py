"""
Utility functions for Ash robot.

This module provides helper functions used across different modules.
"""

import os
import yaml
from pathlib import Path
from dotenv import load_dotenv


def load_config(config_path="config/settings.yaml"):
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        dict: Configuration dictionary
    """
    # Get the project root directory (parent of src/)
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    full_path = project_root / config_path
    
    with open(full_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config


def load_env():
    """
    Load environment variables from .env file.
    Looks for .env in the project root.
    """
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    env_path = project_root / ".env"
    
    if env_path.exists():
        load_dotenv(env_path)
    else:
        print(f"Warning: .env file not found at {env_path}")


def get_api_key():
    """
    Get Gemini API key from environment variables.
    
    Returns:
        str: API key
        
    Raises:
        ValueError: If API key is not set
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        raise ValueError(
            "GEMINI_API_KEY not set. Please create a .env file with your API key."
        )
    return api_key


def get_project_root():
    """
    Get the project root directory.
    
    Returns:
        Path: Path to project root
    """
    return Path(__file__).parent.parent

