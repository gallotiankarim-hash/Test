#!/usr/bin/env bash
set -euo pipefail

echo "🛡️ CallBreach – Policy Remap Script"
echo "----------------------------------"

ROOT_DIR="$(pwd)"
OLD_MODE_FILE="rtcef/config/policy.yaml"
NEW_POLICY_FILE="policy.yaml"
BACKUP_DIR=".policy_backup_$(date +%s)"

echo "[*] Working directory: $ROOT_DIR"
echo "[*] Backup directory:  $BACKUP_DIR"

mkdir -p "$BACKUP_DIR"

# --------------------------------------------------
# 1. Safety checks
# --------------------------------------------------

if [[ ! -f "$NEW_POLICY_FILE" ]]; then
  echo "❌ ERROR: policy.yaml not found at project root"
  exit 1
fi

echo "✅ policy.yaml found"

# --------------------------------------------------
# 2. Backup all python files before modification
# --------------------------------------------------

echo "[*] Backing up Python files..."
find . -type f -name "*.py" -print0 | while IFS= read -r -d '' file; do
  cp "$file" "$BACKUP_DIR/$(basename "$file").bak"
done

# --------------------------------------------------
# 3. Remove old policy.yaml (if exists)
# --------------------------------------------------

if [[ -f "$OLD_MODE_FILE" ]]; then
  echo "[*] Removing obsolete $OLD_MODE_FILE"
  rm "$OLD_MODE_FILE"
else
  echo "[*] policy.yaml already absent (ok)"
fi

# --------------------------------------------------
# 4. Remap Python imports & references
# --------------------------------------------------

echo "[*] Remapping imports and references..."

# Replace direct references to policy.yaml
grep -RIl "policy.yaml" . | while read -r file; do
  echo "  ↪ Updating $file"
  sed -i '' 's|policy.yaml|policy.yaml|g' "$file" 2>/dev/null || \
  sed -i 's|policy.yaml|policy.yaml|g' "$file"
done

# Replace variables like POLICY / policy
grep -RIl "policy\|POLICY" . | while read -r file; do
  echo "  ↪ Normalizing policy naming in $file"
  sed -i '' \
    -e 's/policy/policy/g' \
    -e 's/POLICY/POLICY/g' "$file" 2>/dev/null || \
  sed -i \
    -e 's/policy/policy/g' \
    -e 's/POLICY/POLICY/g' "$file"
done

# --------------------------------------------------
# 5. Ensure policy.yaml is the only YAML loaded
# --------------------------------------------------

echo "[*] Verifying YAML loaders..."

YAML_LOADERS=$(grep -R "yaml.safe_load" -n . | grep -v policy.yaml || true)

if [[ -n "$YAML_LOADERS" ]]; then
  echo "⚠️ WARNING: Additional yaml.safe_load detected:"
  echo "$YAML_LOADERS"
  echo "👉 Review manually if intentional."
else
  echo "✅ No conflicting YAML loaders detected"
fi

# --------------------------------------------------
# 6. Final integrity check
# --------------------------------------------------

echo "[*] Final integrity scan..."

if grep -R "policy.yaml" . >/dev/null 2>&1; then
  echo "❌ ERROR: Residual references to policy.yaml found"
  exit 1
fi

echo "✅ Remap completed successfully"
echo "📦 Backup stored in $BACKUP_DIR"
echo "🚀 You can now safely commit changes"