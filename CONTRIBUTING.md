# Contributing to GLM-5.1 API Toolkit

Thank you for considering contributing to the GLM-5.1 API Toolkit! This document provides guidelines and instructions for contributing.

## Ways to Contribute

1. **Report Bugs**: Submit a detailed bug report through GitHub Issues
2. **Suggest Features**: Propose new features or improvements
3. **Write Code**: Submit pull requests for bug fixes or new features
4. **Improve Documentation**: Help improve or translate documentation
5. **Test**: Help test new features and report issues

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/GLM-5.1-Toolkit.git
   cd GLM-5.1-Toolkit
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

5. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Coding Standards

- Follow PEP 8 style guidelines
- Write clear, descriptive commit messages
- Add docstrings for all public functions and classes
- Include type hints where appropriate
- Write unit tests for new features

## Commit Message Format

We use Conventional Commits format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

## Pull Request Process

1. Create a new branch for your feature/fix
2. Make your changes
3. Ensure all tests pass
4. Update documentation if needed
5. Submit a pull request with a clear description

## Testing

Run tests with:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=glm_toolkit tests/
```

## Code Review

All submissions require review. We use GitHub pull requests for this purpose.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
