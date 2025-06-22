# 📝 Line Endings Configuration Guide

This guide explains how the LED Tomato project handles line endings consistently across all platforms.

## 🎯 Why Line Ending Consistency Matters

- **Cross-platform compatibility** - Works on Windows, macOS, and Linux
- **Avoid diff noise** - No more "every line changed" commits
- **Build consistency** - Prevents build issues across different environments
- **Team collaboration** - Everyone sees the same files regardless of platform

## ⚙️ Repository Configuration

### .gitattributes Rules

The project uses a comprehensive `.gitattributes` file that:

- **Default Rule**: `* text=auto eol=lf` - All text files use LF
- **Source Code**: Force LF for all programming languages
- **Windows Scripts**: Keep CRLF for `.bat` and `.cmd` files (Windows compatibility)
- **Binary Files**: No text processing for images, audio, executables, etc.

### Key Rules Applied

```gitattributes
# Force LF for most files
* text=auto eol=lf

# Source code files
*.js text eol=lf
*.cpp text eol=lf
*.h text eol=lf
*.json text eol=lf

# Windows compatibility
*.bat text eol=crlf
*.cmd text eol=crlf

# Binary files
*.png binary
*.mp3 binary
```

## 🚀 Initial Setup

### For Repository Maintainers

1. **Apply line ending normalization**:
   ```bash
   # On Windows
   normalize-line-endings.bat
   
   # On macOS/Linux
   ./normalize-line-endings.sh
   ```

2. **Commit the changes**:
   ```bash
   git add .gitattributes
   git commit -m "Add .gitattributes for consistent line endings"
   ```

### For Team Members

When you first clone or pull the updated repository:

1. **Configure git locally**:
   ```bash
   git config core.autocrlf false
   git config core.eol lf
   ```

2. **Reset your working directory**:
   ```bash
   git rm --cached -r .
   git reset --hard
   ```

## 🔧 Editor Configuration

### Visual Studio Code

Add to your `.vscode/settings.json`:
```json
{
    "files.eol": "\n",
    "files.insertFinalNewline": true,
    "files.trimFinalNewlines": true,
    "files.trimTrailingWhitespace": true
}
```

### Visual Studio

1. Go to **Tools → Options → Environment → Documents**
2. Check **"Check for consistent line endings on load"**
3. Set line endings to **"Unix (LF)"**

### IntelliJ IDEA / Android Studio

1. Go to **File → Settings → Editor → Code Style**
2. Set **Line separator** to **"Unix and macOS (\n)"**

### Sublime Text

Add to your user settings:
```json
{
    "default_line_ending": "unix",
    "ensure_newline_at_eof_on_save": true
}
```

### Atom

Add to your `config.cson`:
```cson
"*":
  "line-ending-selector":
    "defaultLineEnding": "LF"
```

## 🔍 Verification

### Check Line Endings

```bash
# Check a specific file
file filename.txt

# Check line ending type
od -c filename.txt | head

# Git check
git ls-files --eol
```

### Common Commands

```bash
# See current git configuration
git config --list | grep -E "(autocrlf|eol)"

# Check .gitattributes rules for a file
git check-attr -a filename.txt

# Show files with different line endings
git ls-files --eol | grep -v "i/lf"
```

## 🚨 Troubleshooting

### Problem: Files still have CRLF after setup

**Solution:**
```bash
# Force refresh all files
git rm --cached -r .
git add .
git commit -m "Refresh line endings"
```

### Problem: Editor keeps changing line endings

**Solution:**
- Check editor settings (see Editor Configuration above)
- Ensure `.gitattributes` is properly configured
- Verify git config: `git config core.autocrlf` should be `false`

### Problem: Windows scripts don't work

**Solution:**
- `.bat` and `.cmd` files are configured to keep CRLF
- If they're not working, check the `.gitattributes` file
- Manually convert if needed: `unix2dos script.bat`

### Problem: "Every line changed" in diffs

**Solution:**
```bash
# This usually means line endings are mixed
# Run the normalization script
./normalize-line-endings.sh  # or .bat on Windows
```

## 📋 Best Practices

### For Developers

1. **Always configure git properly** when starting work
2. **Use editor settings** to match project requirements
3. **Check line endings** before committing large changes
4. **Don't override** `.gitattributes` rules manually

### For Code Reviews

1. **Watch for line-ending-only changes** in PRs
2. **Ask contributors to normalize** if you see mixed endings
3. **Verify binary files** aren't being treated as text

### For CI/CD

```bash
# Add to your CI script to verify line endings
git ls-files --eol | grep -v "i/lf" | grep -v "i/crlf.*\.bat$" | grep -v "i/crlf.*\.cmd$"
if [ $? -eq 0 ]; then
    echo "❌ Files with incorrect line endings found!"
    exit 1
fi
```

## 🔄 Migration Guide

### From Mixed Line Endings

1. **Back up your work** (commit or stash changes)
2. **Run normalization script**:
   ```bash
   ./normalize-line-endings.sh
   ```
3. **Update your git config**:
   ```bash
   git config core.autocrlf false
   git config core.eol lf
   ```
4. **Update editor settings** (see Editor Configuration)

### From CRLF Repository

1. **Add `.gitattributes`** with LF rules
2. **Run normalization**:
   ```bash
   git add .gitattributes
   git commit -m "Add .gitattributes"
   ./normalize-line-endings.sh
   ```
3. **Inform team members** to update their local config

## 📚 References

- [Git Documentation - gitattributes](https://git-scm.com/docs/gitattributes)
- [GitHub - Dealing with line endings](https://docs.github.com/en/get-started/getting-started-with-git/configuring-git-to-handle-line-endings)
- [EditorConfig](https://editorconfig.org/) - Cross-editor configuration

---

**Consistent line endings = Happy developers! 📝✨**
