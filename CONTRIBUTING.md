# Contributing to v0rtex

Thank you for your interest in contributing to v0rtex! This guide will help you get started with development and understand our contribution process.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git
- pip or conda
- Chrome/Firefox browser (for testing)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/v0rtex.git
   cd v0rtex
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e ".[dev]"
   ```

4. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

## 🏗️ Project Structure

```
v0rtex/
├── src/v0rtex/           # Main source code
│   ├── core/             # Core scraping functionality
│   ├── utils/            # Utility modules
│   └── cli.py            # Command-line interface
├── tests/                # Test suite
├── docs/                 # Documentation
├── examples/             # Configuration examples
├── scripts/              # Build and utility scripts
└── requirements.txt      # Python dependencies
```

## 📝 Development Workflow

### 1. Branch Naming Convention
- **Feature**: `feat/feature-name`
- **Bug Fix**: `fix/issue-description`
- **Documentation**: `docs/topic`
- **Refactor**: `refactor/module-name`
- **Chore**: `chore/task-description`

### 2. Commit Message Format
We use [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```bash
feat(pagination): add infinite scroll support
fix(scraper): resolve memory leak in browser cleanup
docs(api): update configuration examples
test(core): add integration tests for pagination
```

### 3. Pull Request Process
1. Create a feature branch from `main`
2. Make your changes with clear commits
3. Add/update tests for new functionality
4. Update documentation as needed
5. Ensure all tests pass
6. Submit a pull request with clear description

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=v0rtex

# Run specific test file
pytest tests/test_scraper.py

# Run with verbose output
pytest -v
```

### Test Structure
- **Unit Tests**: Test individual functions/classes
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows
- **Performance Tests**: Test performance characteristics

### Writing Tests
- Follow AAA pattern (Arrange, Act, Assert)
- Use descriptive test names
- Mock external dependencies
- Test both success and failure cases
- Include edge cases and error conditions

## 📚 Documentation Standards

### Code Documentation
- Use Google-style docstrings for all public functions/classes
- Include type hints for all parameters and return values
- Document exceptions that may be raised
- Provide usage examples in docstrings

**Example**:
```python
def scrape_with_pagination(
    self, 
    config: PaginationConfig
) -> List[Dict[str, Any]]:
    """
    Scrape data with automatic pagination handling.
    
    Args:
        config: Pagination configuration object
        
    Returns:
        List of scraped data dictionaries
        
    Raises:
        PaginationError: If pagination strategy detection fails
        ScrapingError: If data extraction fails
        
    Example:
        >>> config = PaginationConfig(enabled=True, max_pages=10)
        >>> results = scraper.scrape_with_pagination(config)
    """
```

### Documentation Updates
- Update relevant documentation for any API changes
- Keep examples current and working
- Document breaking changes clearly
- Update architecture docs for structural changes

## 🔧 Code Standards

### Python Style Guide
- Follow [PEP 8](https://pep8.org/) style guidelines
- Use Black for code formatting
- Use isort for import sorting
- Use flake8 for linting
- Maximum line length: 88 characters (Black default)

### Code Quality
- Write self-documenting code with clear variable names
- Keep functions focused and single-purpose
- Use meaningful error messages
- Handle exceptions gracefully
- Add logging for debugging and monitoring

### Performance Considerations
- Profile code for bottlenecks
- Use appropriate data structures
- Minimize memory allocations
- Consider async operations where beneficial
- Add performance tests for critical paths

## 🚨 Error Handling

### Exception Hierarchy
```python
class V0rtexError(Exception):
    """Base exception for v0rtex framework."""
    pass

class ConfigurationError(V0rtexError):
    """Configuration-related errors."""
    pass

class ScrapingError(V0rtexError):
    """Scraping operation errors."""
    pass

class PaginationError(V0rtexError):
    """Pagination-related errors."""
    pass
```

### Error Handling Guidelines
- Use specific exception types
- Include context in error messages
- Log errors with appropriate levels
- Provide recovery suggestions
- Don't suppress exceptions without logging

## 🔒 Security Guidelines

### Anti-Detection Features
- Test anti-detection measures thoroughly
- Validate user inputs and configurations
- Sanitize data before processing
- Use secure random number generation
- Implement rate limiting appropriately

### Data Protection
- Never log sensitive information
- Encrypt session data when possible
- Validate external service responses
- Use secure communication protocols
- Follow OWASP security guidelines

## 📊 Performance Guidelines

### Memory Management
- Use generators for large datasets
- Implement proper cleanup in destructors
- Monitor memory usage in tests
- Use context managers for resource management
- Profile memory usage regularly

### Optimization
- Profile before optimizing
- Use appropriate algorithms and data structures
- Consider caching for expensive operations
- Implement lazy loading where beneficial
- Test performance impact of changes

## 🚀 Release Process

### Version Management
- Follow [Semantic Versioning](https://semver.org/)
- Update version in `__init__.py`
- Update CHANGELOG.md with changes
- Tag releases in git
- Update PyPI package

### Release Checklist
- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] Version bumped
- [ ] Release notes prepared
- [ ] PyPI package updated

## 🤝 Community Guidelines

### Communication
- Be respectful and inclusive
- Use clear and constructive language
- Ask questions when unsure
- Share knowledge and help others
- Report issues promptly

### Issue Reporting
- Use issue templates
- Provide clear reproduction steps
- Include relevant logs and error messages
- Specify environment details
- Search existing issues first

## 📞 Getting Help

### Resources
- **Documentation**: Check `/docs` folder first
- **Issues**: Search existing issues on GitHub
- **Discussions**: Use GitHub Discussions for questions
- **Wiki**: Check project wiki for guides

### Contact
- **Maintainers**: @v0rtex-team
- **Discussions**: GitHub Discussions
- **Security**: security@v0rtex.dev

## 🙏 Recognition

Contributors will be recognized in:
- Project README
- Release notes
- Contributor hall of fame
- Documentation acknowledgments

Thank you for contributing to v0rtex! 🎉