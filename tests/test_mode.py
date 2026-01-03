"""
Test mode configuration for aicodeprep-gui.

When imported, sets up the application for test mode, disabling
network requests, metrics, and other features that interfere with testing.
"""
import os
import sys

# Set test mode environment variable
os.environ['AICODEPREP_TEST_MODE'] = '1'

# Disable network requests in test mode
os.environ['AICODEPREP_NO_METRICS'] = '1'
os.environ['AICODEPREP_NO_UPDATES'] = '1'
