# Contributing to DynamiR

Thank you for considering contributing to DynamiR! This document provides guidelines and instructions for contributing.

## 📋 Code of Conduct

Please be respectful and constructive in all interactions. We aim to maintain an inclusive and welcoming community.

## 🐛 Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps which reproduce the problem**
- **Provide specific examples to demonstrate the steps**
- **Describe the behavior you observed after following the steps**
- **Explain which behavior you expected to see instead and why**
- **Include screenshots and animated GIFs if possible**
- **Include your operating system and Python version**

## ✨ Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title**
- **Provide a step-by-step description of the suggested enhancement**
- **Provide specific examples to demonstrate the steps**
- **Describe the current behavior and expected new behavior**
- **Explain why this enhancement would be useful**

## 🔧 Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/dynamiR.git
   cd dynamiR
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -r requirements.txt
   # Optional: pip install pytest pytest-cov black flake8
   ```

4. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 💻 Making Changes

### Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep lines under 100 characters when possible
- Use type hints where applicable

### Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line
- Example:
  ```
  Add microRNA sequence validation
  
  - Validates RNA characters (A, U, G, C)
  - Rejects invalid sequences
  - Fixes #123
  ```

### Pull Request Process

1. **Update the README.md** if you're adding new features
2. **Test your changes** thoroughly
3. **Submit a pull request** with a clear title and description
4. **Link related issues** in the PR description
5. **Be responsive** to review comments

## 📝 Pull Request Guidelines

- One feature/fix per pull request
- Include screenshots for UI changes
- Add unit tests for new functionality (if applicable)
- Ensure all tests pass before submitting
- Keep commits clean and organized
- Update documentation as needed

## 🧪 Testing

Before submitting a PR:

```bash
# Run tests (when available)
pytest

# Check code style
flake8 .

# Format code
black .
```

## 📚 Documentation

- Update README.md for user-facing changes
- Add docstrings to all new functions/classes
- Include examples in comments for complex algorithms
- Document any new dependencies

## 🎯 Areas for Contribution

- **Bug fixes**: Report or fix issues
- **Documentation**: Improve README, add guides, fix typos
- **Features**: Add new analysis modes or capabilities
- **Performance**: Optimize existing algorithms
- **Tests**: Add unit or integration tests
- **UI/UX**: Improve user interface and experience

## ❓ Questions?

Feel free to open a GitHub discussion or issue with your questions.

## 📜 License

By contributing, you agree that your contributions will be licensed under its MIT License.

---

Thank you for helping make DynamiR better! 🙏
