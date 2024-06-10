# ProjectName/test/__main__.py

import os
import sys

import pytest

PROJECT_PATH = os.getcwd()
SOURCE_PATH = os.path.join(PROJECT_PATH, "app")
sys.path.append(SOURCE_PATH)

# sys.path.append('../project_name')
