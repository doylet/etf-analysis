#!/bin/bash
# Setup git hooks for architecture enforcement

HOOKS_DIR=".git/hooks"
CUSTOM_HOOKS_DIR=".githooks"

echo "🔧 Setting up git hooks..."

# Create hooks directory if it doesn't exist
mkdir -p "$HOOKS_DIR"

# Create pre-commit hook that calls our architecture check
cat > "$HOOKS_DIR/pre-commit" << 'EOF'
#!/bin/bash
# Run architecture validation before commit

echo "Running architecture validation..."
python3 .githooks/pre-commit-architecture

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Commit blocked due to architecture violations"
    echo "Fix the issues above or use --no-verify to bypass (not recommended)"
    exit 1
fi

exit 0
EOF

# Make hooks executable
chmod +x "$HOOKS_DIR/pre-commit"
chmod +x "$CUSTOM_HOOKS_DIR/pre-commit-architecture"

echo "✅ Git hooks installed successfully!"
echo ""
echo "The following hooks are now active:"
echo "  - pre-commit: Architecture validation"
echo ""
echo "To bypass hooks (not recommended): git commit --no-verify"
