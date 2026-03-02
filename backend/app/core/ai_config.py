"""
Kimi 2.5 AI Configuration for NVIDIA API
"""

import os
from dotenv import load_dotenv

load_dotenv()

class AIConfig:
    # Your NVIDIA API credentials
    API_KEY = "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"
    BASE_URL = "https://integrate.api.nvidia.com/v1"
    
    # Model settings
    MODEL = "moonshotai/kimi-k2.5"
    
    # Performance settings
    TEMPERATURE = 1.00  # From your curl command
    MAX_TOKENS = 16384   # From your curl command
    TOP_P = 1.00        # From your curl command
    
    # Feature flags
    ENABLE_THINKING = True  # Enable the thinking capability
