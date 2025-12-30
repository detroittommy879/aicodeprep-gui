import os
import shutil
import logging
import zipfile
import subprocess
from importlib import resources

# The name of the workflow bundle
WORKFLOW_NAME = "AICodePrep.workflow"

# The standard location for user-installed services/quick actions
SERVICES_DIR = os.path.expanduser("~/Library/Services")

def install_quick_action():
    """
    Extracts the AICodePrep.workflow.zip from package data to the user's Desktop
    and instructs them to double-click it for installation.
    """
    try:
        desktop_path = os.path.expanduser("~/Desktop")
        destination_workflow_path = os.path.join(desktop_path, WORKFLOW_NAME)
        zip_filename = f"{WORKFLOW_NAME}.zip"

        # Ensure the desktop exists
        os.makedirs(desktop_path, exist_ok=True)

        # If the workflow file already exists on the desktop, remove it first for a clean copy
        if os.path.exists(destination_workflow_path):
            logging.info(f"Removing existing '{WORKFLOW_NAME}' from Desktop before extraction.")
            shutil.rmtree(destination_workflow_path)

        # Find the zip file in the package data and extract it
        logging.info(f"Extracting '{zip_filename}' to Desktop...")
        with resources.files('aicodeprep_gui.data').joinpath(zip_filename).open('rb') as zip_file_obj:
            with zipfile.ZipFile(zip_file_obj, 'r') as zip_ref:
                zip_ref.extractall(desktop_path)

        # Open Finder to show the user the file
        subprocess.run(["open", desktop_path])

        msg = (
            f"The installer ('{WORKFLOW_NAME}') has been placed on your Desktop.\n\n"
            "Please follow these steps:\n"
            "1. Go to your Desktop.\n"
            "2. Double-click the 'AICodePrep' workflow file.\n"
            "3. Click 'Install' in the dialog that appears.\n\n"
            "The Quick Action will then be available when you right-click a folder in Finder."
        )
        logging.info("Successfully extracted workflow to Desktop for manual installation.")
        return True, msg

    except FileNotFoundError:
        msg = "Error: Could not find the installer 'AICodePrep.workflow.zip' inside the package."
        logging.error(msg)
        return False, msg
    except Exception as e:
        msg = f"An unexpected error occurred: {e}"
        logging.error(msg)
        return False, msg


def uninstall_quick_action():
    """Removes the macOS Quick Action from the user's Library."""
    dest_path = os.path.join(SERVICES_DIR, WORKFLOW_NAME)
    if os.path.exists(dest_path):
        try:
            shutil.rmtree(dest_path)
            # Attempt to refresh services to make the change immediate
            try:
                subprocess.run(["/System/Library/CoreServices/pbs", "-flush"], check=False, timeout=5)
            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                 logging.warning(f"Could not flush services cache during uninstall: {e}")
            msg = f"Quick Action '{WORKFLOW_NAME}' has been uninstalled."
            logging.info(msg)
            return True, msg
        except Exception as e:
            msg = f"Failed to uninstall Quick Action: {e}"
            logging.error(msg)
            return False, msg
    else:
        msg = "Quick Action was not found (already uninstalled)."
        logging.info(msg)
        return True, msg