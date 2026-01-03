# Flow Studio Properties Panel - User Guide

## How to Edit Node Properties

### Properties Panel Location

When you select a node in the Flow Studio, the **Properties panel** appears on the **right side** of the window. This panel allows you to customize node behavior without editing code.

### If You Don't See the Properties Panel

**The properties panel requires NodeGraphQt 0.6.30 or higher.** If you don't see it:

1. **Check your NodeGraphQt version**:

   ```bash
   pip show NodeGraphQt
   ```

2. **Update if needed**:

   ```bash
   pip install --upgrade NodeGraphQt
   ```

3. **Restart the application** after updating

### Alternative: Use the Toolbar Buttons

If the properties panel isn't available, you can still configure nodes using:

- **"Set Models..." button**: Configure LLM models for selected nodes
- **Import/Export**: Edit flow JSON files directly (for advanced users)

---

## Editing Common Properties

### 1. Change Output Filename (FileWriteNode)

**Steps**:

1. Click on the **"File Write"** node
2. Look for the **Properties panel** on the right
3. Find the property named **`path`**
4. Change from `"best_of_n.txt"` to your desired filename
5. Run the flow - output will now go to your specified file

**Example**: Change to `"my_synthesis_result.txt"` to save results with a custom name.

### 2. Customize Synthesis Prompt (BestOfNNode)

**Steps**:

1. Click on the **"Best-of-N Synthesizer"** node
2. In Properties panel, find **`extra_prompt`**
3. This is a multiline text field - edit the instructions
4. Run the flow - the synthesizer will use your custom prompt

**Example Customizations**:

```
Original:
"Analyze each response, identify strengths/weaknesses..."

Modified for Performance Focus:
"Analyze each response focusing on PERFORMANCE OPTIMIZATIONS.
Identify which solution is fastest and most efficient.
Combine the best performance insights from all responses."

Modified for Security Focus:
"Analyze each response from a SECURITY perspective.
Identify potential vulnerabilities in each approach.
Synthesize the most secure solution combining all insights."
```

### 3. Configure LLM Model Settings

**For Individual Nodes**:

1. Click on an **OpenRouter LLM** node
2. In Properties panel, find:
   - **`provider`**: openrouter, openai, gemini, etc.
   - **`model_mode`**: choose, random, random_free
   - **`model`**: specific model ID (if mode = "choose")
   - **`api_key`**: override default API key (optional)

**For Multiple Nodes at Once**:

1. **Select multiple nodes** (Ctrl+Click or drag selection box)
2. Click **"Set Models..."** in toolbar
3. Choose mode and enter model IDs
4. Click OK - all selected nodes update

### 4. Configure Context Source (ContextOutputNode)

**Steps**:

1. Click on **"Context Output"** node
2. In Properties panel, find:
   - **`path`**: Which file to read context from (default: `fullcode.txt`)
   - **`use_latest_generated`**: Whether to use latest generated context

---

## Property Types Reference

### Text Fields

- Single-line text input
- Used for: file paths, model IDs, API keys
- **Tip**: Copy/paste works as expected

### Multiline Text Fields

- Large text area with scrolling
- Used for: prompts, synthesis instructions
- **Tip**: Use Ctrl+Enter to add newlines

### Dropdown Lists

- Select from predefined options
- Used for: provider selection, model modes
- **Options**:
  - **provider**: openrouter, openai, gemini, compatible
  - **model_mode**: choose, random, random_free

### File Pickers

- Browse for files (if available)
- Used for: file paths
- **Fallback**: Manual text entry if file picker unavailable

---

## Troubleshooting

### "I don't see the Properties panel"

**Possible Causes**:

1. **NodeGraphQt version too old**

   - Update to 0.6.30+: `pip install --upgrade NodeGraphQt`

2. **No node is selected**

   - Click on a node to activate the properties panel

3. **Properties panel is collapsed**

   - Look for a splitter handle between graph and panel
   - Drag the splitter to reveal the panel

4. **Running in read-only mode (Free version)**
   - Some features may be limited
   - Properties viewing should still work

### "Changes don't take effect"

**Solutions**:

1. **Make sure you pressed Enter or clicked outside the field**

   - Some properties update on blur/enter

2. **Re-run the flow**

   - Property changes apply to next execution
   - Click "Run Flow" button to see changes

3. **Check for validation errors**
   - Invalid values may be rejected silently
   - Check console/logs for error messages

### "Can't find a specific property"

**Try**:

1. **Different node might have that property**

   - FileWriteNode has `path`
   - BestOfNNode has `extra_prompt`
   - LLM nodes have `model`, `provider`, etc.

2. **Property might be nested or hidden**

   - Scroll in the properties panel
   - Some properties only appear in certain modes

3. **Use the toolbar dialog instead**
   - "Set Models..." button provides alternative UI
   - Works even if properties panel has issues

---

## Best Practices

### 1. Test Small Changes First

- Modify one property at a time
- Run flow to verify it works
- Then make additional changes

### 2. Save Your Flows

- After configuring properties, use **"Export..."**
- Save as `.json` file for reuse
- Share with others or version control

### 3. Document Your Custom Prompts

- Keep a separate text file with your best prompts
- Copy/paste into `extra_prompt` when needed
- Build a library of specialized prompts

### 4. Use Descriptive Filenames

- Instead of `output.txt`, use:
  - `refactoring_consensus_2025-01-27.txt`
  - `security_audit_results.txt`
  - `best_of_5_debugging_session.txt`

---

## Advanced: Direct JSON Editing

If properties panel is unavailable, you can edit flows as JSON:

1. **Export your flow**: Flow menu → Export...
2. **Edit the JSON file**:
   ```json
   {
     "nodes": [
       {
         "id": "file_write_node",
         "type": "FileWriteNode",
         "properties": {
           "path": "my_custom_output.txt"
         }
       }
     ]
   }
   ```
3. **Import back**: Flow menu → Import...

---

## Getting Help

If you're still having trouble:

1. **Check the logs**: `~/.aicodeprep/logs/`
2. **Report issues**: GitHub Issues with screenshot
3. **Community support**: Discord/Forum

**Useful Debug Info to Include**:

- NodeGraphQt version: `pip show NodeGraphQt`
- Python version: `python --version`
- Screenshot of Flow Studio window
- Log file excerpt showing errors
