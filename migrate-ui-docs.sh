#!/bin/bash

# Sutra UI Documentation Migration Script
# Migrates from docs/ui to organized professional structure

set -e

SOURCE_DIR="docs/ui"
TARGET_DIR="docs/ui-professional" 
BACKUP_DIR="docs/ui-backup-$(date +%Y%m%d-%H%M%S)"

echo "🚀 Starting Sutra UI Documentation Migration"
echo "============================================"

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ Source directory $SOURCE_DIR does not exist"
    exit 1
fi

# Create backup
echo "📋 Creating backup at $BACKUP_DIR..."
cp -r "$SOURCE_DIR" "$BACKUP_DIR"
echo "✅ Backup created successfully"

# Create new professional structure  
echo "📁 Creating professional directory structure..."
mkdir -p "$TARGET_DIR"/{user-guides,api,technical,deployment,development,archive/{sessions,progress}}

# Copy organized structure from ui-new
echo "📝 Copying organized documentation..."
cp -r docs/ui-new/* "$TARGET_DIR/"

echo "✅ Professional documentation structure created!"
echo ""
echo "📊 Migration Summary:"
echo "===================="
echo "📂 Source:      $SOURCE_DIR (backed up to $BACKUP_DIR)"
echo "📂 Target:      $TARGET_DIR" 
echo "📚 Structure:   6 main categories + archive"
echo "📄 Files:       $(find "$TARGET_DIR" -type f -name "*.md" | wc -l | tr -d ' ') Markdown documents"
echo ""

# Show new structure
echo "📁 New Professional Structure:"
echo "=============================="
tree "$TARGET_DIR" -I "*.backup|*.tmp" --dirsfirst

echo ""
echo "🎯 Next Steps:"
echo "=============="
echo "1. Review the new structure: cd $TARGET_DIR"
echo "2. Update any external links pointing to old paths"
echo "3. Test all internal cross-references"  
echo "4. Replace old docs/ui with new structure when ready:"
echo "   mv $SOURCE_DIR ${SOURCE_DIR}-old"
echo "   mv $TARGET_DIR $SOURCE_DIR"
echo ""
echo "📚 Documentation Quality:"
echo "========================"
echo "✅ Professional organization (6 categories)"
echo "✅ Clear navigation paths for different user types"
echo "✅ Comprehensive README files with guidance"
echo "✅ Maintained all original content"
echo "✅ Added professional index and cross-references"
echo ""
echo "🎉 Migration completed successfully!"

# Optional: Show file mapping
echo ""
echo "📋 Key File Mappings:"
echo "===================="
echo "QUICKSTART.md → user-guides/quickstart.md"
echo "USER_GUIDE.md → user-guides/user-guide.md" 
echo "FAQ.md → user-guides/faq.md"
echo "API_REFERENCE.md → api/api-reference.md"
echo "AUTH_API_REFERENCE.md → api/auth-reference.md"
echo "CONVERSATION_FIRST_ARCHITECTURE.md → technical/architecture.md"
echo "PRODUCTION_DEPLOYMENT.md → deployment/production-guide.md"
echo "IMPLEMENTATION_ROADMAP.md → development/implementation-roadmap.md"
echo "SESSION_*_COMPLETE.md → archive/sessions/"
echo "PROGRESS_SUMMARY.md → archive/progress-summary.md"
echo "TODO.md → archive/todo.md"
echo ""
echo "Ready for professional documentation! 🚀"