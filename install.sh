#!/bin/sh
# Synapse installer
# https://github.com/romulofebasi/synapse-releases
#
# Detects OS + architecture, downloads the matching release tarball
# from the public release mirror, verifies it, and drops `syn` into
# INSTALL_DIR (defaults to /usr/local/bin).
#
# The simplest install is npm (any platform with Node 18+):
#   npx @febasi/synapse --help      # run once, no install
#   npm install -g @febasi/synapse  # global `syn`
# This script is the standalone alternative for systems without Node.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/romulofebasi/synapse-releases/main/install.sh | sh
#
# Environment knobs:
#   SYNAPSE_VERSION   tag to install (default: latest published release)
#   INSTALL_DIR       where to write `syn` (default: /usr/local/bin)
#   SKIP_QUARANTINE   set to 1 on macOS to skip the Gatekeeper clear

set -eu

repo="romulofebasi/synapse-releases"
bin_name="syn"

say() { printf 'syn-install: %s\n' "$*"; }
die() { printf 'syn-install: error: %s\n' "$*" >&2; exit 1; }

require() {
    command -v "$1" >/dev/null 2>&1 || die "$1 is required (install it and retry)"
}

require curl
require uname
require tar

# ----- resolve target -------------------------------------------------------

os=$(uname -s | tr '[:upper:]' '[:lower:]')
arch=$(uname -m)

case "$os-$arch" in
    darwin-arm64|darwin-aarch64) target=aarch64-apple-darwin ;;
    darwin-x86_64)
        die "Intel Macs (x86_64) are not supported: Synapse's semantic-search runtime (ONNX Runtime) ships no Intel-macOS build, so there is no binary for this target. Apple Silicon (M1+) only."
        ;;
    linux-x86_64|linux-amd64)    target=x86_64-unknown-linux-gnu ;;
    linux-arm64|linux-aarch64)   target=aarch64-unknown-linux-gnu ;;
    *)
        die "no prebuilt binary for $os-$arch; try npm (npx @febasi/synapse) or contact support"
        ;;
esac

# ----- resolve version ------------------------------------------------------

version="${SYNAPSE_VERSION:-}"
if [ -z "$version" ]; then
    say "fetching latest release tag…"
    version=$(curl -fsSL -H 'Accept: application/json' \
        "https://api.github.com/repos/$repo/releases/latest" \
        | sed -n 's/.*"tag_name":[[:space:]]*"\([^"]*\)".*/\1/p' \
        | head -n1)
    [ -n "$version" ] || die "could not resolve latest tag for $repo"
fi
# Normalise: API may return "v0.1.0" or "0.1.0"; we always want the leading v.
case "$version" in
    v*) tag="$version"; ver_no_v="${version#v}" ;;
    *)  tag="v$version"; ver_no_v="$version" ;;
esac

# ----- download + extract ---------------------------------------------------

asset="synapse-${ver_no_v}-${target}.tar.gz"
url="https://github.com/$repo/releases/download/$tag/$asset"
tmpdir=$(mktemp -d 2>/dev/null || mktemp -d -t syn)
trap 'rm -rf "$tmpdir"' EXIT

say "downloading $asset"
curl -fsSL "$url" -o "$tmpdir/$asset" \
    || die "download failed: $url (check that $tag exists)"

# ----- verify integrity -----------------------------------------------------
# Release archives ship a SHA256SUMS manifest signed with keyless
# Sigstore/cosign. We always check the checksum; if `cosign` is installed we
# also verify the signature. Full manual steps: VERIFYING-RELEASES.md.

sums_url="https://github.com/$repo/releases/download/$tag/SHA256SUMS"
if curl -fsSL "$sums_url" -o "$tmpdir/SHA256SUMS" 2>/dev/null; then
    expected=$(sed -n "s/^\([0-9a-f]\{64\}\)[[:space:]]*[*]\{0,1\}$asset\$/\1/p" \
        "$tmpdir/SHA256SUMS" | head -n1)
    if [ -n "$expected" ]; then
        if command -v sha256sum >/dev/null 2>&1; then
            actual=$(sha256sum "$tmpdir/$asset" | cut -d' ' -f1)
        elif command -v shasum >/dev/null 2>&1; then
            actual=$(shasum -a 256 "$tmpdir/$asset" | cut -d' ' -f1)
        else
            actual=""
        fi
        if [ -n "$actual" ]; then
            [ "$actual" = "$expected" ] \
                || die "checksum mismatch for $asset (expected $expected, got $actual)"
            say "checksum verified"
        fi
    fi
    if command -v cosign >/dev/null 2>&1; then
        bundle_url="https://github.com/$repo/releases/download/$tag/SHA256SUMS.cosign.bundle"
        if curl -fsSL "$bundle_url" -o "$tmpdir/SHA256SUMS.cosign.bundle" 2>/dev/null; then
            if cosign verify-blob \
                --bundle "$tmpdir/SHA256SUMS.cosign.bundle" \
                --certificate-identity-regexp '^https://github.com/romulofebasi/synapse/\.github/workflows/release\.yml@refs/tags/v' \
                --certificate-oidc-issuer 'https://token.actions.githubusercontent.com' \
                "$tmpdir/SHA256SUMS" >/dev/null 2>&1; then
                say "cosign signature verified"
            else
                say "warning: cosign signature check failed; proceeding on checksum only"
            fi
        fi
    else
        say "tip: install cosign to also verify the release signature"
    fi
else
    say "warning: no SHA256SUMS for $tag; skipping checksum verification"
fi

say "unpacking"
tar -xzf "$tmpdir/$asset" -C "$tmpdir"
src="$tmpdir/synapse-${ver_no_v}-${target}/$bin_name"
[ -x "$src" ] || die "expected $bin_name at $src after extracting"

# ----- install --------------------------------------------------------------

install_dir="${INSTALL_DIR:-/usr/local/bin}"
mkdir -p "$install_dir" 2>/dev/null || true

target_path="$install_dir/$bin_name"
if [ -w "$install_dir" ]; then
    install -m 755 "$src" "$target_path"
else
    say "$install_dir is not writable by $(id -un); using sudo"
    sudo install -m 755 "$src" "$target_path"
fi

# ----- macOS quarantine -----------------------------------------------------

if [ "$os" = "darwin" ] && [ "${SKIP_QUARANTINE:-0}" != "1" ]; then
    if xattr -p com.apple.quarantine "$target_path" >/dev/null 2>&1; then
        say "clearing Gatekeeper quarantine on $target_path"
        if [ -w "$target_path" ]; then
            xattr -d com.apple.quarantine "$target_path" || true
        else
            sudo xattr -d com.apple.quarantine "$target_path" || true
        fi
    fi
fi

# ----- summary --------------------------------------------------------------

say "installed $bin_name $tag at $target_path"
case ":$PATH:" in
    *:"$install_dir":*) ;;
    *) say "warning: $install_dir is not in your PATH" ;;
esac

if command -v "$bin_name" >/dev/null 2>&1; then
    "$bin_name" --version || true
fi

say "done. try: $bin_name init ~/brain && cd ~/brain && $bin_name --help"
