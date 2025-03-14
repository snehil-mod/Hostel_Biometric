# GitHub Setup Guide

This guide will help you push your Hostel Biometric System to GitHub.

## Prerequisites

- Git installed on your computer
- GitHub account
- Your project files ready

## Steps to Push to GitHub

1. **Fix the Git ownership issue**:
   ```bash
   git config --global --add safe.directory E:/Projects/Hostel_Biometric
   ```

2. **Initialize Git** (if not already done):
   ```bash
   cd E:/Projects/Hostel_Biometric
   git init
   ```

3. **Add your GitHub repository as remote**:
   ```bash
   git remote add origin https://github.com/snehil-mod/Hostel_Biometric.git
   ```

4. **Add all your files**:
   ```bash
   git add .
   ```

5. **Commit your changes**:
   ```bash
   git commit -m "Initial commit: Hostel Biometric System"
   ```

6. **Push to GitHub**:
   ```bash
   git push -u origin main
   ```
   (If your default branch is "master" instead of "main", use `git push -u origin master`)

## Troubleshooting

### If you have a nested repository issue:

1. **Remove the inner repository from Git tracking**:
   ```bash
   git rm -f --cached Hostel_Biometric_adv
   ```

2. **Delete the inner .git folder** (PowerShell):
   ```powershell
   Remove-Item -Path ".\Hostel_Biometric_adv\.git" -Recurse -Force
   ```

3. **Delete the entire inner folder** (if needed):
   ```powershell
   Remove-Item -Path ".\Hostel_Biometric_adv" -Recurse -Force
   ```

4. **Try adding and committing again**:
   ```bash
   git add .
   git commit -m "Remove nested repository"
   git push -u origin main
   ```

## After Pushing

1. Refresh your GitHub repository page to see your files
2. Verify that README.md is displayed correctly
3. Check that all necessary files are included

## Next Steps

- Set up GitHub Pages if you want to create a project website
- Add collaborators if you're working with others
- Set up GitHub Actions for CI/CD if needed 