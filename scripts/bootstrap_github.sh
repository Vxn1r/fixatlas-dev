#!/usr/bin/env bash
set -Eeuo pipefail

REPOSITORY="${FIXATLAS_REPOSITORY:-Vxn1r/fixatlas-dev}"
DESCRIPTION="Evidence-first, offline developer error diagnostics for humans and coding agents."

fail() {
  printf 'FixAtlas GitHub setup: %s\n' "$*" >&2
  exit 1
}

command -v gh >/dev/null 2>&1 || fail "GitHub CLI (gh) is required. Install it from https://cli.github.com/."
command -v git >/dev/null 2>&1 || fail "Git is required."
gh auth status >/dev/null 2>&1 || fail "Authenticate first with: gh auth login"

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || fail "Run this script from inside the FixAtlas Git repository."
git show-ref --verify --quiet refs/heads/main || fail "The local main branch is missing."
git show-ref --verify --quiet refs/tags/v0.1.0 || fail "The local v0.1.0 release tag is missing."

if gh repo view "$REPOSITORY" >/dev/null 2>&1; then
  printf 'Using existing GitHub repository %s\n' "$REPOSITORY"
  expected_url="https://github.com/${REPOSITORY}.git"
  if git remote get-url origin >/dev/null 2>&1; then
    current_url="$(git remote get-url origin)"
    case "$current_url" in
      "$expected_url"|"https://github.com/${REPOSITORY}"|"git@github.com:${REPOSITORY}.git") ;;
      *) fail "origin points to $current_url, not $expected_url. Fix it before continuing." ;;
    esac
  else
    git remote add origin "$expected_url"
  fi
  git push --set-upstream origin main
else
  printf 'Creating public repository %s\n' "$REPOSITORY"
  gh repo create "$REPOSITORY" \
    --public \
    --source=. \
    --remote=origin \
    --push \
    --description="$DESCRIPTION"
fi

# Push the annotated release tag explicitly; repo creation's --push concerns commits.
git push origin v0.1.0

# These topics describe FixAtlas's actual scope; Claude-specific topics are intentionally omitted.
gh repo edit "$REPOSITORY" \
  --description "$DESCRIPTION" \
  --enable-issues \
  --enable-discussions \
  --enable-squash-merge \
  --delete-branch-on-merge \
  --add-topic ai-agents \
  --add-topic developer-tools \
  --add-topic mcp \
  --add-topic productivity \
  --add-topic debugging \
  --add-topic troubleshooting \
  --add-topic error-diagnostics \
  --add-topic cli \
  --add-topic python \
  --add-topic offline \
  --add-topic llm \
  --add-topic open-source \
  --add-topic developer-experience

create_label() {
  local name="$1" color="$2" description="$3"
  gh label create "$name" --repo "$REPOSITORY" --color "$color" \
    --description "$description" --force >/dev/null
}

create_label "bug" "D73A4A" "Something is not working as expected"
create_label "documentation" "0075CA" "Documentation improvements"
create_label "enhancement" "A2EEEF" "A feature or improvement proposal"
create_label "good first issue" "7057FF" "Suitable for a first contribution"
create_label "help wanted" "008672" "Extra attention or contributor help is welcome"
create_label "needs-triage" "FBCA04" "Needs maintainer review and categorization"
create_label "rule:new" "1D76DB" "A new diagnostic rule or signature"
create_label "tests" "BFD4F2" "Test coverage or fixture changes"

printf '\nRepository bootstrap complete: https://github.com/%s\n' "$REPOSITORY"
printf 'Next: wait for CI, then follow docs/repository-setup.md for branch protection and security settings.\n'
