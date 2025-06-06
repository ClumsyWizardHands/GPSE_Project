# Running GPSE with Memory Enabled

## Quick Start - Run as Administrator

To ensure ChromaDB has proper permissions for memory storage:

### Option 1: PowerShell as Administrator (Recommended)

1. **Right-click on PowerShell** and select "Run as Administrator"
2. Navigate to project:
   ```powershell
   cd C:\Users\every\Desktop\GPSE_Project
   ```
3. Run the script:
   ```powershell
   .\run_gpse.ps1
   ```

### Option 2: Command Prompt as Administrator

1. **Right-click on Command Prompt** and select "Run as Administrator"
2. Navigate and run:
   ```cmd
   cd C:\Users\every\Desktop\GPSE_Project
   powershell -ExecutionPolicy Bypass -File run_gpse.ps1
   ```

### Option 3: Direct Python Execution

If you still get permission errors, run directly:
```powershell
# In Administrator PowerShell
cd C:\Users\every\Desktop\GPSE_Project
.\gpse_venv\Scripts\Activate.ps1
python main_crew_memory_fix.py
```

## What the Memory Fix Does

1. **Configures ChromaDB** to use a local `chroma_db` directory
2. **Creates the directory** with proper permissions
3. **Validates permissions** before starting
4. **Enables memory** for all agents to maintain context

## Benefits of Memory

- Agents remember previous interactions
- Better continuity between tasks
- Learning from past analyses
- Improved performance over time

## If You Still Get Errors

1. Make sure you're running as Administrator
2. Check if `chroma_db` folder was created
3. Try deleting `chroma_db` folder and `.chroma` folder if they exist
4. Run again as Administrator

The system will now maintain memory across runs, improving analysis quality!
