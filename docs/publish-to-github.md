# Publish this source tree to GitHub

The GitHub connection available during this build can write to existing repositories, but it does not expose repository creation. The source archive therefore includes a bootstrap script that uses the GitHub CLI from your own computer.

## One-command setup

1. Install [GitHub CLI](https://cli.github.com/) and authenticate with `gh auth login`.
2. Extract this archive and open a **Git Bash or WSL** terminal in the `fixatlas-dev` folder on Windows (or a terminal on macOS/Linux).
3. Run:

```bash
bash scripts/bootstrap_github.sh
```

The script creates `Vxn1r/fixatlas-dev` as a public repository if it does not exist. If you already created the repository on GitHub, it connects `origin` and pushes the existing `main` branch. It then pushes the annotated `v0.1.0` tag, applies the project's description and topics, enables Issues and Discussions, selects squash merging, enables branch deletion after merge, and creates the standard issue labels. It checks the existing `origin` URL before pushing rather than silently replacing an unrelated remote.

You can choose a different owner/repository by setting `FIXATLAS_REPOSITORY=OWNER/NAME` before running the script. The project README and package metadata are currently configured for `Vxn1r/fixatlas-dev`, so update those URLs too if you change the repository name.

## After the first CI run

Follow [repository-setup.md](repository-setup.md) to protect `main`, require passing CI and resolved conversations, enable Dependabot/security features, and check the CodeQL workflow. Those settings are kept separate because branch protection needs the actual workflow check names to exist first.

## Manual alternative

If you prefer creating the empty public repository through the GitHub website, create `Vxn1r/fixatlas-dev` without a README or license. Then run these commands from the extracted project root:

```bash
git remote add origin https://github.com/Vxn1r/fixatlas-dev.git
git push -u origin main
git push origin v0.1.0
```

Then run `bash scripts/bootstrap_github.sh` to apply topics and labels; it will detect and reuse the existing repository and matching `origin` remote.
