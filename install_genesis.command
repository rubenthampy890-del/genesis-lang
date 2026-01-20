#!/bin/bash

# ANSI Color Codes
CYAN='\033[1;36m'
PINK='\033[1;35m'
GREEN='\033[1;32m'
RESET='\033[0m'
BOLD='\033[1m'

clear

echo -e "${PINK}"
echo "   > G E N E S I S  (v5.0)"
echo "   ======================="
echo "   🤖 AI Powered | 🗣️ Voice | 🎨 Graphics"
echo -e "${RESET}"

# Install Dependencies
echo "   📦 Checking dependencies..."
pip3 install prompt_toolkit > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}   ✅ Intelligent Autocomplete Installed.${RESET}"
else
    echo -e "${PINK}   ⚠️  Could not install 'prompt_toolkit'. Autocomplete disabled.${RESET}"
fi

echo -e "${CYAN}   Welcome to the Future of Coding.${RESET}"
echo -e "${CYAN}   Developed by ${BOLD}'rubenthampy'${RESET}"
echo ""
echo "   New Features in v5.0:"
echo "   🧠 AI Inside ('ask' command)"
echo "   🗣️ Native Voice ('speak' command)"
echo "   🎨 Graphics Engine ('draw' command)"
echo "   ✍️ Natural Syntax (Postfix 'if', 'times' loops)"
echo "   ---------------------------------"
echo ""

TARGET_RC="$HOME/.zshrc"
CORRECT_ALIAS="alias genesis='\"/Users/basilthampy/Music/antigravity/just fun/genesis/genesis\"'"

echo -n "   Installing..."
# Remove old alias lines
grep -v "alias genesis=" "$TARGET_RC" > "$TARGET_RC.tmp" && mv "$TARGET_RC.tmp" "$TARGET_RC"

# Append the correct alias
echo "$CORRECT_ALIAS" >> "$TARGET_RC"
sleep 1
echo -e "${GREEN} Done!${RESET}"

echo ""
echo -e "${BOLD}   ✅ Installation Complete.${RESET}"
echo ""
echo "   How to start:\"\\n   1. Close this window.\"\\n   2. Open a new Terminal.\"\\n   3. Type 'genesis' to start.\"\\n"
