"""
Test script to verify Unity project reset functionality
"""
import pathlib
import os
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "editor"))

from dotenv import load_dotenv
from run_experiment import ExperimentRunner

# Load environment
env_path = pathlib.Path(__file__).parent.parent / "editor" / ".env"
load_dotenv(env_path)

runner = ExperimentRunner()

# Test the reset function
print("Testing Unity project reset...")
runner._reset_unity_project()
print("Reset completed successfully!")
