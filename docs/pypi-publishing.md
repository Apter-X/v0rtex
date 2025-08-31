# PyPI Publishing Guide

This guide explains how to publish the v0rtex package to PyPI (Python Package Index) using our automated GitHub Actions workflow.

## 🚀 Overview

The release workflow automatically:
1. Builds the Python package when you push a version tag
2. Publishes to PyPI (or TestPyPI for pre-releases)
3. Creates a GitHub release with artifacts
4. Generates changelog from conventional commits

## 📋 Prerequisites

### 1. PyPI Account Setup

1. **Create PyPI Account**: Sign up at [pypi.org](https://pypi.org/account/register/)
2. **Enable Two-Factor Authentication**: Required for API tokens
3. **Create API Token**: 
   - Go to Account Settings → API tokens
   - Create a new token with "Entire account (all projects)" scope
   - Copy the token (starts with `pypi-`)

### 2. TestPyPI Account Setup (Optional)

1. **Create TestPyPI Account**: Sign up at [test.pypi.org](https://test.pypi.org/account/register/)
2. **Create API Token**: Same process as PyPI
3. **TestPyPI is used for**: Alpha, beta, and release candidate versions

## 🔐 GitHub Secrets Configuration

Add these secrets to your GitHub repository:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add the following secrets:

### Required Secrets

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `PYPI_API_TOKEN` | Your PyPI API token | `pypi-abc123...` |
| `TEST_PYPI_API_TOKEN` | Your TestPyPI API token | `pypi-xyz789...` |

### How to Add Secrets

```bash
# Navigate to your repository settings
# Settings → Secrets and variables → Actions → New repository secret

# Add each secret with the exact names above
```

## 🏷️ Version Tagging Strategy

### Release Types

| Tag Format | PyPI Destination | Use Case |
|------------|------------------|----------|
| `v1.0.0` | Production PyPI | Stable releases |
| `v1.0.0-alpha.1` | TestPyPI | Alpha releases |
| `v1.0.0-beta.1` | TestPyPI | Beta releases |
| `v1.0.0-rc.1` | TestPyPI | Release candidates |

### Creating a Release

```bash
# 1. Update version in pyproject.toml
# 2. Commit changes
git add pyproject.toml
git commit -m "chore: bump version to 1.0.0"

# 3. Create and push tag
git tag v1.0.0
git push origin v1.0.0

# 4. The workflow will automatically trigger
```

## 🔄 Workflow Steps

### 1. Build Process
- Sets up Python 3.11 environment
- Installs build dependencies (`build`, `twine`)
- Builds package using `python -m build`
- Creates both wheel (`.whl`) and source (`.tar.gz`) distributions

### 2. Publishing Logic
- **Alpha/Beta/RC versions**: Published to TestPyPI only
- **Stable versions**: Published to production PyPI
- Uses conditional logic based on tag format

### 3. GitHub Release
- Creates release with changelog
- Uploads built packages as release artifacts
- Includes installation instructions and links

### 4. Cleanup
- Removes build artifacts from runner
- Keeps repository clean

## 📦 Package Configuration

The package is configured in `pyproject.toml`:

```toml
[project]
name = "v0rtex"
version = "0.1.0"
description = "Dynamic JSON-based web scraper with anti-detection capabilities"
# ... other metadata
```

### Key Fields

- **name**: Must be unique on PyPI
- **version**: Follows semantic versioning
- **dependencies**: Listed in `requirements.txt`
- **build-system**: Uses setuptools with wheel

## 🧪 Testing the Workflow

### 1. Test with TestPyPI

```bash
# Create an alpha version
git tag v0.1.0-alpha.1
git push origin v0.1.0-alpha.1
```

This will publish to TestPyPI only, allowing you to test the workflow safely.

### 2. Verify Package

```bash
# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ v0rtex

# Or install from production PyPI (after stable release)
pip install v0rtex
```

## 🚨 Troubleshooting

### Common Issues

1. **Build Failures**
   - Check Python version compatibility
   - Verify all dependencies are in `requirements.txt`
   - Check for syntax errors in source code

2. **PyPI Upload Failures**
   - Verify API token is correct
   - Check if package name is available
   - Ensure version number is higher than existing versions

3. **GitHub Release Failures**
   - Check repository permissions
   - Verify `GITHUB_TOKEN` is available
   - Check tag format matches expected pattern

### Debug Steps

1. **Check Workflow Logs**: Go to Actions tab in GitHub
2. **Verify Secrets**: Ensure all required secrets are set
3. **Test Locally**: Try building package locally first
4. **Check Dependencies**: Ensure all imports are available

## 📚 Additional Resources

- [PyPI Packaging Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Python Build Documentation](https://pypa-build.readthedocs.io/)
- [Twine Documentation](https://twine.readthedocs.io/)

## 🔄 Maintenance

### Regular Tasks

1. **Update Dependencies**: Keep build tools updated
2. **Monitor PyPI**: Check for package downloads and issues
3. **Review Workflows**: Ensure automation continues working
4. **Update Documentation**: Keep this guide current

### Version Management

- Use semantic versioning consistently
- Document breaking changes clearly
- Maintain changelog for each release
- Consider automated version bumping for minor releases

---

For questions or issues, please open an issue in the GitHub repository or contact the maintainers.
