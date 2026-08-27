#!/usr/bin/env bash
set -euo pipefail
package_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$package_dir/installer.py" "$@"
