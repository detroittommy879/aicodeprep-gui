# Parallel LLM MCP Server - Capabilities & Monitoring Guide

**Date:** 10_12_2025

---

## 🚀 Capabilities

- **Parallel LLM Calls:**

  - Sends a single prompt to 5 different LLM models (OpenRouter API)
  - Waits up to 4 minutes for each model
  - Continues if 1-2 models fail (graceful degradation)
  - Synthesizes responses from successful models

- **Robust Timeout Handling:**

  - 240s timeout per model (configurable)
  - No blocking of main event loop

- **Detailed Progress Logging:**

  - Logs all phases and model results to both console and `parallel_llm_progress.log`
  - Emoji and color-coded log entries for easy scanning
  - Tracks elapsed time, token counts, and errors

- **Live Monitoring:**
  - Real-time log monitoring via PowerShell script
  - Color-coded output for instant status visibility

---

## 🖥️ How to Start the Monitoring Script

1. **Open a PowerShell terminal**
2. **Navigate to the project folder:**
   ```powershell
   cd c:\2nd\Main\Git-Projects\parallel-MCP\parallel-llm-mcp
   ```
3. **Run the color-coded monitor:**

   ```powershell
   .\watch_progress_color.ps1
   ```

   - Shows last 50 lines and live updates
   - Color legend:
     - 🟢 Green: Success/Complete
     - 🟡 Yellow: Starting/In Progress
     - 🔴 Red: Errors
     - 🟣 Magenta: Timeouts/Warnings
     - 🔵 Cyan: Phase Headers
     - ⚪ Gray: Info

4. **(Optional) Run the basic monitor:**
   ```powershell
   .\watch_progress.ps1
   ```
   - Plain text, no colors

---

## 🏁 Typical Workflow

- **Terminal 1:** Start the server
  ```powershell
  python -m parallel_llm_mcp.server
  ```
- **Terminal 2:** Start the monitor
  ```powershell
  .\watch_progress_color.ps1
  ```
- **Terminal 3:** Send a prompt using your MCP client

---

## 📋 Troubleshooting

- If log file does not exist, the monitor script will create it automatically
- If you see timeouts, check model status on OpenRouter dashboard
- For more details, see `MONITORING.md` and log output

---

**File generated: 10_12_2025**
