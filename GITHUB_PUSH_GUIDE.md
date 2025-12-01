# Step-by-Step Guide: Push Project to GitHub

This guide walks you through pushing your project to GitHub.

## Prerequisites

- Git installed on your system
- GitHub account created
- Terminal/Command Prompt access

## Step 1: Initialize Git Repository

Open terminal in your project directory and run:

```bash
cd "/Users/fawzanalfawzan/Documents/PhD/ASU/Cources/Traffic Simulation Modelling and Applications/Project"

# Initialize git repository
git init

# Check status (should show all files)
git status
```

## Step 2: Add Files to Git

```bash
# Add all files (respects .gitignore)
git add .

# Verify what will be committed
git status
```

**Note**: The `.gitignore` file will automatically exclude:
- `venv/` folder
- `__pycache__/` folders
- `.DS_Store` files
- Large data files in `data_cleaning_fusion_datasets/`
- Output files in `data/output/`

## Step 3: Create Initial Commit

```bash
git commit -m "Initial commit: Traffic data cleaning pipeline

- Comprehensive data cleaning pipeline for multi-source traffic data
- Six-step cleaning process following FHWA guidelines
- Map matching integration with gotrackit
- Complete documentation and analysis notebooks
- Ready for Architecture Alphabet framework integration"
```

## Step 4: Create GitHub Repository

1. **Go to GitHub**: https://github.com
2. **Click the "+" icon** (top right) → **"New repository"**
3. **Repository settings**:
   - **Name**: `traffic-data-cleaning` (or your preferred name)
   - **Description**: `Comprehensive data cleaning pipeline for multi-source traffic data to prepare it for traffic simulation model calibration. Implements Part 2: Data Cleaning within the Architecture Alphabet framework.`
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
4. **Click "Create repository"**

## Step 5: Connect Local Repository to GitHub

After creating the repository, GitHub will show you commands. Use these:

```bash
# Add remote repository (replace USERNAME and REPO_NAME with your values)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Verify remote was added
git remote -v
```

**Example**:
```bash
git remote add origin https://github.com/fawzanalfawzan/traffic-data-cleaning.git
```

## Step 6: Push to GitHub

```bash
# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

You'll be prompted for your GitHub username and password/token.

## Step 7: Authentication

### Option A: Personal Access Token (Recommended)

1. **Create Token**:
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token" → "Generate new token (classic)"
   - Name: `traffic-data-cleaning`
   - Select scopes: `repo` (full control of private repositories)
   - Click "Generate token"
   - **Copy the token** (you won't see it again!)

2. **Use Token**:
   - When prompted for password, paste the token instead

### Option B: GitHub CLI (Alternative)

```bash
# Install GitHub CLI (if not installed)
# macOS: brew install gh
# Then authenticate:
gh auth login
```

## Step 8: Verify Upload

1. Go to your GitHub repository page
2. Verify all files are present:
   - README.md
   - notebooks/
   - docs/
   - scripts/
   - config/
   - .gitignore
   - LICENSE
   - etc.

## Step 9: Add Repository Topics (Optional)

1. Go to your repository on GitHub
2. Click the gear icon (⚙️) next to "About"
3. Add topics:
   - `traffic-simulation`
   - `data-cleaning`
   - `map-matching`
   - `transportation`
   - `python`
   - `jupyter-notebook`
   - `architecture-alphabet`

## Troubleshooting

### Issue: "remote origin already exists"

```bash
# Remove existing remote
git remote remove origin

# Add new remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

### Issue: "Authentication failed"

- Make sure you're using a Personal Access Token, not your password
- Check that token has `repo` scope
- Try using GitHub CLI: `gh auth login`

### Issue: "Large files" error

If you get errors about large files:
1. Check `.gitignore` is working: `git status`
2. Remove large files from git history if accidentally added:
   ```bash
   git rm --cached large_file.csv
   git commit -m "Remove large file"
   ```

### Issue: "Branch protection" or "Permission denied"

- Make sure you're the repository owner
- Check repository settings → Branches
- Verify your GitHub account has write access

## Quick Reference Commands

```bash
# Check status
git status

# Add files
git add .

# Commit
git commit -m "Your commit message"

# Push
git push -u origin main

# View remotes
git remote -v

# View commit history
git log --oneline
```

## Next Steps After Upload

1. **Add README badges** (optional):
   - Go to repository → Settings → General
   - Scroll to "Social preview"
   - Upload a preview image

2. **Create releases** (optional):
   - Go to repository → Releases → "Create a new release"
   - Tag: `v1.0.0`
   - Title: `Initial Release`
   - Description: Copy from README.md

3. **Enable GitHub Pages** (optional):
   - Go to repository → Settings → Pages
   - Source: `main` branch → `/docs` folder
   - Save

---

**Need Help?** If you encounter any issues, check:
- [GitHub Docs](https://docs.github.com)
- [Git Documentation](https://git-scm.com/doc)
- Your repository's Issues page

---

**Last Updated**: December 2025

