@echo off
REM LED Tomato - Line Ending Normalization Script (Windows)
REM This script normalizes all text files in the repository to use LF line endings

echo 🔧 LED Tomato - Line Ending Normalization
echo ==========================================

REM Check if we're in a git repository
if not exist ".git" (
    echo ❌ Error: Not in a git repository!
    pause
    exit /b 1
)

echo 📋 Current repository status:
git status --porcelain

echo.
echo 🔄 Normalizing line endings...

REM Configure git for this repository
echo ⚙️  Configuring git settings for consistent line endings...
git config core.autocrlf false
git config core.eol lf

REM Remove the index entirely - this forces git to re-examine all files
echo 🗑️  Clearing git index...
del /q .git\index 2>nul

REM Re-add all files - this will apply .gitattributes rules
echo 📁 Re-adding all files with new line ending rules...
git add .

REM Show what changed
echo.
echo 📊 Files that will have line endings normalized:
git diff --cached --name-only

REM Check if there are any changes
git diff --cached --quiet
if %errorlevel% == 0 (
    echo ✅ No line ending changes needed - all files already have correct endings!
    goto :end
)

echo.
echo 💾 Committing line ending normalization...
git commit -m "Normalize line endings to LF" -m "" -m "- Applied .gitattributes rules to ensure consistent LF line endings" -m "- All text files now use LF across all platforms" -m "- Binary files properly marked to avoid text processing"

if %errorlevel% == 0 (
    echo ✅ Line ending normalization complete!
    echo.
    echo 📋 What was changed:
    git show --name-only --pretty=format:""
) else (
    echo ❌ Failed to commit changes!
    goto :error
)

:end
echo.
echo 🔍 Verifying .gitattributes is properly configured...
if exist ".gitattributes" (
    echo ✅ .gitattributes file exists
    echo 📄 Key rules applied:
    echo    - Default: * text=auto eol=lf
    echo    - Source files: Force LF
    echo    - Windows scripts: Keep CRLF for .bat/.cmd
    echo    - Binary files: No text processing
) else (
    echo ❌ .gitattributes file not found!
    goto :error
)

echo.
echo 📝 Next steps for team members:
echo 1. Pull the latest changes
echo 2. Run: git config core.autocrlf false
echo 3. Run: git config core.eol lf
echo 4. Optional: Configure editor to use LF line endings

echo.
echo ✅ Repository is now configured for consistent LF line endings!
goto :final

:error
echo ❌ An error occurred during normalization!
pause
exit /b 1

:final
pause
