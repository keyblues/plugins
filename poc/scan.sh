#!/bin/bash
#
# PHP Code Audit - Quick Vulnerability Scanner
# Scans for basic vulnerability indicators in PHP files
#
# Usage: ./scan.sh [/path/to/php/files]
#

TARGET="${1:-/workspace}"
echo "=============================================="
echo "PHP Code Audit Scanner"
echo "Target: $TARGET"
echo "=============================================="
echo ""

# Check for dangerous functions
echo "[*] Scanning for dangerous functions..."
echo ""

echo "=== RCE (eval, system, exec, shell_exec) ==="
grep -rn -E "(eval\(|system\(|exec\(|shell_exec\(|passthru\(|popen\(|proc_open\(|pcntl_exec\(|create_function\()" "$TARGET" --include="*.php" 2>/dev/null | head -20

echo ""
echo "=== SQL Injection (direct query without prepare) ==="
grep -rn -E "->query\(['\"].*\$" "$TARGET" --include="*.php" 2>/dev/null | grep -v "prepare\|bindValue\|bindParam" | head -20

echo ""
echo "=== File Operations (file_put_contents, fwrite, move_uploaded_file) ==="
grep -rn -E "(file_put_contents|fwrite|move_uploaded_file|include\s|require\s)" "$TARGET" --include="*.php" 2>/dev/null | head -20

echo ""
echo "=== Unserialize ==="
grep -rn "unserialize(" "$TARGET" --include="*.php" 2>/dev/null | head -20

echo ""
echo "=== User Input (direct use without filtering) ==="
grep -rn -E "\$_GET\[|\$_POST\[|\$_REQUEST\[|\$_COOKIE\[" "$TARGET" --include="*.php" 2>/dev/null | grep -v "intval\|htmlspecialchars\|addslashes\|mysql_real_escape_string\|filter_" | head -20

echo ""
echo "=============================================="
echo "Scan complete. Manual analysis required."
echo "=============================================="
