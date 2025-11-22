# Contributing to MedAiTools

Thank you for your interest in contributing to MedAiTools! This guide will help you get started.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## How to Contribute

### Reporting Bugs

1. Check existing issues to avoid duplicates
2. Create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (Python version, OS, etc.)

### Suggesting Features

1. Open an issue with the "enhancement" label
2. Describe the feature and its benefits
3. Provide use cases if possible

### Submitting Code

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Write/update tests**
5. **Run tests**:
   ```bash
   pytest
   ```
6. **Format code**:
   ```bash
   black .
   flake8 .
   ```
7. **Commit with clear messages**:
   ```bash
   git commit -m "Add feature: description of what you added"
   ```
8. **Push and create a Pull Request**

## Development Guidelines

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for public functions
- Keep functions focused and small

```python
def process_document(
    filepath: str,
    options: dict | None = None
) -> dict:
    """
    Process a document and extract structured data.

    Args:
        filepath: Path to the document file
        options: Optional processing options

    Returns:
        Dictionary containing extracted data

    Raises:
        FileNotFoundError: If filepath doesn't exist
        ValueError: If document format is unsupported
    """
    pass
```

### Testing

- Write tests for new functionality
- Maintain test coverage
- Use pytest fixtures for common setup

### Documentation

- Update documentation for API changes
- Add docstrings to new functions
- Include usage examples where helpful

## Pull Request Process

1. Update documentation if needed
2. Ensure all tests pass
3. Get at least one code review
4. Squash commits if requested
5. Maintain backwards compatibility when possible

## Questions?

Open an issue or reach out to maintainers.
