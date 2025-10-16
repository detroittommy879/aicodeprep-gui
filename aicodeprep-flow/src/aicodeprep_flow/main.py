import sys
import argparse
import logging
from PySide6.QtWidgets import QApplication


def main():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")

    parser = argparse.ArgumentParser(
        description="AICodePrep Flow: Visual Editor and MCP Server.")
    parser.add_argument("--mcp", action="store_true",
                        help="Run in headless MCP server mode (stdio).")
    args = parser.parse_args()

    if args.mcp:
        # Run in headless MCP server mode
        from .mcp.server import main_sync as run_mcp_server
        print("Starting aicodeprep-flow in headless MCP server mode...")
        run_mcp_server()
    else:
        # Run the GUI editor
        from .main_window import MainWindow
        from .apptheme import apply_dark_palette, load_custom_fonts

        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        apply_dark_palette(app)  # Default to dark theme for consistency
        load_custom_fonts()

        window = MainWindow()
        sys.exit(app.exec())


if __name__ == "__main__":
    main()
