#!/bin/sh
set -eu

version="${1:-1.7.12}"
expected_sha256="${2:?actionlint SHA-256 is required}"
config_file="${3:-.github/actionlint.yaml}"
archive="/tmp/actionlint.tar.gz"
url="https://github.com/rhysd/actionlint/releases/download/v${version}/actionlint_${version}_linux_amd64.tar.gz"

curl --fail --location --retry 5 --retry-all-errors --silent --show-error "$url" --output "$archive"
printf '%s  %s\n' "$expected_sha256" "$archive" | sha256sum --check --strict
mkdir -p /tmp/actionlint
tar -xzf "$archive" -C /tmp/actionlint
exec /tmp/actionlint/actionlint -config-file "$GITHUB_WORKSPACE/$config_file"
