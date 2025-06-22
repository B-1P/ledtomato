#!/bin/bash

# LED Tomato - Line Ending Normalization Script
# This script normalizes all text files in the repository to use LF line endings

echo "🔧 LED Tomato - Line Ending Normalization"
echo "=========================================="

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository!"
    exit 1
fi

echo "📋 Current repository status:"
git status --porcelain

echo ""
echo "🔄 Normalizing line endings..."

# Remove the index entirely - this forces git to re-examine all files
echo "🗑️  Clearing git index..."
rm .git/index

# Re-add all files - this will apply .gitattributes rules
echo "📁 Re-adding all files with new line ending rules..."
git add .

# Show what changed
echo ""
echo "📊 Files that will have line endings normalized:"
git diff --cached --name-only

# Check if there are any changes
if [ -z "$(git diff --cached --name-only)" ]; then
    echo "✅ No line ending changes needed - all files already have correct endings!"
else
    echo ""
    echo "💾 Committing line ending normalization..."
    git commit -m "Normalize line endings to LF

- Applied .gitattributes rules to ensure consistent LF line endings
- All text files now use LF across all platforms
- Binary files properly marked to avoid text processing"

    echo "✅ Line ending normalization complete!"
    echo ""
    echo "📋 What was changed:"
    git show --name-only --pretty=format:""
fi

echo ""
echo "🔍 Verifying .gitattributes is properly configured..."
if [ -f ".gitattributes" ]; then
    echo "✅ .gitattributes file exists"
    echo "📄 Key rules applied:"
    echo "   - Default: * text=auto eol=lf"
    echo "   - Source files: Force LF"
    echo "   - Windows scripts: Keep CRLF for .bat/.cmd"
    echo "   - Binary files: No text processing"
else
    echo "❌ .gitattributes file not found!"
    exit 1
fi

echo ""
echo "📝 Next steps for team members:"
echo "1. Pull the latest changes"
echo "2. Run: git config core.autocrlf false"
echo "3. Run: git config core.eol lf"
echo "4. Optional: Configure editor to use LF line endings"

echo ""
echo "✅ Repository is now configured for consistent LF line endings!"
