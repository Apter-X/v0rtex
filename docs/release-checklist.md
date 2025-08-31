# Release Checklist

This checklist ensures a smooth release process for v0rtex packages.

## 🏷️ Pre-Release Checklist

### 1. Code Quality
- [ ] All tests pass locally
- [ ] Code linting passes (black, isort, flake8)
- [ ] Type checking passes (mypy)
- [ ] Documentation is up to date
- [ ] CHANGELOG.md is updated (if manual)

### 2. Version Management
- [ ] Update version in `pyproject.toml`
- [ ] Ensure version follows semantic versioning
- [ ] Commit version change with conventional commit message

### 3. Dependencies
- [ ] Check `requirements.txt` is up to date
- [ ] Verify all dependencies are compatible
- [ ] Test installation in clean environment

## 🚀 Release Process

### 1. Create Release Tag
```bash
# Update version in pyproject.toml first
git add pyproject.toml
git commit -m "chore: bump version to X.Y.Z"

# Create and push tag
git tag vX.Y.Z
git push origin vX.Y.Z
```

### 2. Monitor Workflow
- [ ] Check GitHub Actions tab for workflow execution
- [ ] Verify build process completes successfully
- [ ] Confirm PyPI upload succeeds
- [ ] Check GitHub release is created

### 3. Verify Release
- [ ] Package appears on PyPI (or TestPyPI for pre-releases)
- [ ] GitHub release has correct artifacts
- [ ] Changelog is generated correctly
- [ ] Installation works: `pip install v0rtex`

## 📋 Release Types

### Alpha/Beta/RC Releases
```bash
git tag v1.0.0-alpha.1
git push origin v1.0.0-alpha.1
```
- Publishes to TestPyPI only
- Safe for testing release process
- Use for development milestones

### Stable Releases
```bash
git tag v1.0.0
git push origin v1.0.0
```
- Publishes to production PyPI
- Available to all users via `pip install`
- Use for production-ready versions

## 🔍 Post-Release Verification

### 1. PyPI Verification
- [ ] Package appears in search results
- [ ] Version information is correct
- [ ] Dependencies are properly listed
- [ ] Package description is accurate

### 2. Installation Testing
```bash
# Test in clean environment
python -m venv test_env
source test_env/bin/activate  # or test_env\Scripts\activate on Windows
pip install v0rtex
python -c "import v0rtex; print(v0rtex.__version__)"
```

### 3. GitHub Release
- [ ] Release notes are complete
- [ ] Artifacts are properly attached
- [ ] Tag points to correct commit
- [ ] Release is marked as latest

## 🚨 Troubleshooting

### Common Issues

#### Build Failures
- Check Python version compatibility
- Verify all imports are available
- Check for syntax errors

#### PyPI Upload Failures
- Verify API token is correct
- Check package name availability
- Ensure version number is higher

#### GitHub Release Issues
- Check repository permissions
- Verify workflow file syntax
- Check for conflicting tags

### Debug Commands
```bash
# Test build locally
python -m build

# Test PyPI upload (dry run)
python -m twine upload --repository testpypi dist/*

# Check package contents
tar -tzf dist/v0rtex-X.Y.Z.tar.gz
```

## 📚 Resources

- [PyPI Publishing Guide](pypi-publishing.md)
- [GitHub Actions Workflow](.github/workflows/release.yml)
- [Python Packaging Guide](https://packaging.python.org/)
- [Semantic Versioning](https://semver.org/)

---

**Remember**: Always test the release process with TestPyPI first before publishing to production PyPI!
