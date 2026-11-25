#!/usr/bin/env bash
# Create an instance repository from template/.
#
# Usage:
#   scripts/new-instance.sh <owner>/<repo> [--private] [--dir <path>] [--local]
#
#   --private   create a private GitHub repository (GitHub then bills the
#               build minutes; macOS runners count ten times)
#   --dir       where to create the local copy (default: ./<repo>)
#   --local     only create the local copy, do not touch GitHub
#
# Values are asked interactively. Each one can be preset with an environment
# variable of the same name as in client.env (APP_NAME, COMPANY, BUNDLE_ID,
# SERVER_HOST, SERVER_KEY, API_URL, WEBSITE_URL, ACCENT_COLOR).
#
# Requires git and python3, plus the GitHub CLI (gh, logged in) unless --local.

set -euo pipefail

generator_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

die() {
  echo "error: $*" >&2
  exit 1
}

usage() {
  sed -n '2,16p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
}

repository=""
visibility="--public"
target_dir=""
local_only=false

while [ $# -gt 0 ]; do
  case "$1" in
    --private) visibility="--private" ;;
    --local) local_only=true ;;
    --dir)
      [ $# -ge 2 ] || die "--dir needs a path"
      target_dir="$2"
      shift
      ;;
    -h | --help) usage 0 ;;
    -*) die "unknown option: $1" ;;
    *)
      [ -z "$repository" ] || die "only one repository can be given"
      repository="$1"
      ;;
  esac
  shift
done

[ -n "$repository" ] || usage 1
[[ "$repository" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] || die "repository must look like owner/name"
target_dir="${target_dir:-./${repository#*/}}"
[ ! -e "$target_dir" ] || die "$target_dir already exists"

command -v git > /dev/null || die "git is required"
command -v python3 > /dev/null || die "python3 is required"
if ! $local_only; then
  command -v gh > /dev/null || die "the GitHub CLI (gh) is required, or use --local"
  gh auth status > /dev/null 2>&1 || die "run 'gh auth login' first, or use --local"
fi

# ask <VARIABLE> <question> [default]: keeps a value preset in the environment.
ask() {
  local name="$1" question="$2" default="${3:-}" answer
  if [ -n "${!name:-}" ]; then
    return
  fi
  if [ -n "$default" ]; then
    read -r -p "$question [$default]: " answer
  else
    read -r -p "$question: " answer
  fi
  printf -v "$name" '%s' "${answer:-$default}"
}

echo "New instance: $repository"
echo
ask APP_NAME "Application name shown to users" "Remote Support"
ask COMPANY "Publisher (your organisation)"
ask BUNDLE_ID "macOS bundle identifier" "org.example.remotesupport"
ask SERVER_HOST "RustDesk server host (hbbs)"
ask SERVER_KEY "Server public key (content of id_ed25519.pub)"
ask API_URL "API server / console URL (empty if none)"
ask WEBSITE_URL "Your website (empty if none)"
ask ACCENT_COLOR "Accent colour as #RRGGBB (empty to keep the default)"

mkdir -p "$target_dir"
cp -R "$generator_root/template/." "$target_dir/"

cat > "$target_dir/client.env" << CONFIG
# Instance configuration, see the Configuration reference in the wiki.
# Nothing here is secret: all of it can be read from the client you distribute.
APP_NAME=$APP_NAME
COMPANY=$COMPANY
BUNDLE_ID=$BUNDLE_ID
SERVER_HOST=$SERVER_HOST
SERVER_KEY=$SERVER_KEY
API_URL=${API_URL:-}
WEBSITE_URL=${WEBSITE_URL:-}
SOURCE_URL=https://github.com/$repository
ACCENT_COLOR=${ACCENT_COLOR:-}
CONFIG

if ! python3 "$generator_root/scripts/apply.py" --instance "$target_dir" --validate-only; then
  rm -rf "$target_dir"
  die "the configuration is not valid, nothing was created"
fi

git -C "$target_dir" init --quiet --initial-branch=main
git -C "$target_dir" add -A
git -C "$target_dir" commit --quiet -m "Initial instance configuration"
echo
echo "Local instance created in $target_dir"

if $local_only; then
  echo "Next: push it to GitHub, then run the 'Build client' workflow."
  exit 0
fi

read -r -p "Create the ${visibility#--} repository github.com/$repository and push? [y/N] " confirm
case "$confirm" in
  y | Y | yes) ;;
  *)
    echo "Skipped. The local copy is ready in $target_dir."
    exit 0
    ;;
esac

gh repo create "$repository" "$visibility" --source "$target_dir" --remote origin --push

cat << NEXT

Done. Next steps:
  1. Replace $target_dir/branding/icon.png with your icon (square PNG, 1024x1024).
  2. Start a build:   gh workflow run "Build client" --repo $repository
  3. Publish a release by pushing a tag:   git tag v1.0.0 && git push origin v1.0.0
NEXT
