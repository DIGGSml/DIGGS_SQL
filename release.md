# Release Guide

## Creating a Release

1. **Update version in setup.py** (executable/setup.py line 83)
2. **Create and push a git tag:**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
3. **GitHub Actions will automatically:**
   - Build the Windows executable
   - Create a ZIP archive
   - Create a GitHub release with the executable attached

## Version Naming Convention

- Use semantic versioning: `v1.0.0`, `v1.0.1`, `v2.0.0`
- Major version: Breaking changes
- Minor version: New features
- Patch version: Bug fixes

## Manual Release (if needed)

1. **Build locally:**
   ```bash
   cd executable
   python setup.py build
   ```
2. **Create ZIP archive of build folder**
3. **Create release on GitHub and upload ZIP**
