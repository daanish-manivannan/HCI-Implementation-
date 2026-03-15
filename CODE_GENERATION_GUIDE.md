# Code Generation Guide

## Where Generated Code is Saved

### 1. **Generate Code (Memory Only - NOT Saved)**
```
Say: "generate code palindrome"
or: "generate hello world in python"
```
**Result**: Code is generated in memory  
**Saved to**: NOWHERE (temporary memory)  
**Find it**: Check console for the generated code preview  
**Action**: Use "open code in editor" command to save it

---

### 2. **Open Code in Editor (SAVES to Desktop)**
```
Say: "open code in editor generate fibonacci in python"
or: "open code in editor generate hello world"
```
**Result**: Code is generated AND saved  
**Saved to**: `C:\Users\KumaraGuru\Desktop\code_snippet_<timestamp>.py`  
**Find it**: 
- ✅ Check your Desktop folder
- ✅ File opens automatically in VS Code
- ✅ Console shows: `[SAVE LOCATION] Code saved to: C:\Users\KumaraGuru\Desktop\...\`

**Example file names**:
```
code_snippet_1742215898.py    (Python)
code_snippet_1742215899.java  (Java)
code_snippet_1742215900.js    (JavaScript)
```

---

### 3. **Execute Code (Runs in Temp - Auto-Deleted)**
```
Say: "execute code factorial in python"
or: "execute code generate palindrome"
```
**Result**: Code is generated, executed, output shown  
**Saved to**: Temporary system folder (C:\Users\...\AppData\Local\Temp\)  
**Find it**: CANNOT ACCESS (file auto-deleted after execution)  
**Output**: Shown directly in console

**Console Output Example**:
```
============================================================
[EXECUTED]
5! = 120
10! = 120
============================================================
```

---

## Summary Table

| Command | Code Generated? | File Saved? | Location | Auto-Opens? |
|---------|---|---|---|---|
| Generate code | ✅ Yes | ❌ No | Memory only | ❌ No |
| Open code in editor | ✅ Yes | ✅ YES | **Desktop** | ✅ VS Code |
| Execute code | ✅ Yes | ❌ No (temp) | Temp deleted | ❌ No |

---

## Quick Test

### Test 1: Generate & Save
```
Say: "open code in editor generate factorial in python"

Expected:
1. Console shows: [SAVE LOCATION] Code saved to: C:\Users\KumaraGuru\Desktop\code_snippet_<time>.py
2. VS Code opens with the Python file
3. Desktop shows new file: code_snippet_<time>.py
```

### Test 2: Execute & See Output
```
Say: "execute code fibonacci in python"

Expected:
1. Code runs
2. Console shows output (Fibonacci sequence)
3. No file remains (temp file deleted)
```

### Test 3: Generate Without Saving
```
Say: "generate hello world in python"

Expected:
1. Console shows generated code
2. No file saved
3. Use "open code in editor" to save it later
```

---

## Supported Languages

When you say "open code in editor", you can specify language:

```
Say: "open code in editor generate hello world in python"      -> .py
Say: "open code in editor generate hello world in java"        -> .java
Say: "open code in editor generate hello world in javascript"  -> .js
Say: "open code in editor generate hello world in cpp"         -> .cpp
Say: "open code in editor generate hello world in csharp"      -> .cs
```

---

## File Naming Convention

All generated files use timestamp naming to avoid overwrites:

```
code_snippet_1742215898.py
co <-- "code_snippet_"
                 <-- Unix timestamp (when file was created)
```

This means:
- ✅ Each generated file has a unique name
- ✅ No files overwrite each other
- ✅ Easy to sort by creation time
- ✅ Multiple files can exist on Desktop

---

## Accessing Your Generated Code Files

### **Quick Access to Desktop**:
1. Open File Explorer
2. Click on `Desktop` in the left sidebar
3. Look for files starting with `code_snippet_`

### **Using Command Line**:
```powershell
# List all generated code files
Get-ChildItem -Path "~/Desktop" -Filter "code_snippet*"

# Open in VS Code from PowerShell
code "~/Desktop/code_snippet_1742215898.py"
```

### **From VS Code**:
1. File → Open Folder
2. Select Desktop
3. Look for `code_snippet_*.py` files

---

## Tips & Tricks

### Organize Your Code Files
```
# Create a folder on Desktop
New-Item -ItemType Directory -Path "~/Desktop/Generated_Code" -Force

# Move code files there
Move-Item -Path "~/Desktop/code_snippet*" -Destination "~/Desktop/Generated_Code"
```

### Clean Up Old Files
```powershell
# Remove code files older than 7 days
Get-ChildItem -Path "~/Desktop" -Filter "code_snippet*" | 
  Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) } | 
  Remove-Item
```

### View Generated Code in Console
The console output shows a preview when generating. Look for:
```
[CodeGen] Generated code: <preview>
```

---

## Troubleshooting

### "File not on Desktop"
- ✅ Check if VS Code opened and created the file there
- ✅ Search for `code_snippet*` files on your entire Drive C:
- ✅ Check console for exact file path

### "Can't find generated code"
- ✅ Use `Execute code` if you just want to see output
- ✅ Use `Open code in editor` if you want to save the file
- ✅ Check Desktop folder directly

### "VS Code didn't open"
- ✅ File is still saved to Desktop
- ✅ Manually open the file from Desktop
- ✅ Right-click file → Open with → Visual Studio Code

