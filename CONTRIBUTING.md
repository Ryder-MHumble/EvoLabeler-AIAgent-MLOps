# Contributing to EvoLabeler

First off, thank you for considering contributing to EvoLabeler! It's people like you that make EvoLabeler such a great tool.

## 🌟 Ways to Contribute

There are many ways to contribute to EvoLabeler:

- 🐛 **Report Bugs**: Submit bug reports in [GitHub Issues](https://github.com/Ryder-MHumble/EvoLabeler-AIAgent-MLOps/issues)
- 💡 **Suggest Features**: Propose new features or improvements
- 📝 **Improve Documentation**: Help us improve our documentation
- 🔧 **Submit Pull Requests**: Fix bugs or implement new features
- 🌍 **Translate**: Help translate the project to other languages
- ⭐ **Star the Project**: Show your support by starring the repository

## 📋 Development Process

We use GitHub to host code, track issues and feature requests, as well as accept pull requests.

### Pull Request Process

1. **Fork the Repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/EvoLabeler-AIAgent-MLOps.git
   cd EvoLabeler-AIAgent-MLOps
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

3. **Make Your Changes**
   - Write clear, concise commit messages
   - Follow the existing code style
   - Add tests if applicable
   - Update documentation as needed

4. **Test Your Changes**
   ```bash
   # Backend tests
   cd backend
   poetry run pytest
   
   # Frontend tests
   cd evolauncher-frontend
   npm run test
   ```

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

6. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Open a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill out the PR template
   - Submit the PR

## 📝 Commit Message Convention

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that don't affect code meaning (formatting, etc.)
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `perf`: Performance improvements
- `test`: Adding missing tests
- `chore`: Changes to build process or auxiliary tools

### Examples

```bash
feat(agent): add uncertainty quantification to inference agent
fix(api): resolve project creation validation error
docs(readme): update installation instructions
style(frontend): format code with prettier
refactor(orchestrator): simplify residual connection logic
perf(crawler): optimize image download performance
test(api): add unit tests for project endpoints
chore(deps): update fastapi to 0.115.0
```

## 🧪 Testing Guidelines

### Backend Testing

```bash
cd backend
poetry run pytest tests/ -v
```

### Frontend Testing

```bash
cd evolauncher-frontend
npm run test
npm run test:e2e
```

### Code Coverage

Aim for at least 80% code coverage for new features.

```bash
# Backend coverage
poetry run pytest --cov=app tests/

# Frontend coverage
npm run test:coverage
```

## 💻 Code Style

### Python (Backend)

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints
- Maximum line length: 100 characters
- Use `black` for formatting
- Use `ruff` for linting

```bash
poetry run black app/
poetry run ruff check app/
```

### TypeScript/Vue (Frontend)

- Follow [Vue Style Guide](https://vuejs.org/style-guide/)
- Use TypeScript strict mode
- Use ESLint and Prettier
- Maximum line length: 100 characters

```bash
npm run lint
npm run format
```

## 🐛 Bug Reports

When filing a bug report, please include:

- **Title**: Clear and descriptive title
- **Description**: Detailed description of the bug
- **Steps to Reproduce**: Step-by-step instructions
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**:
  - OS: [e.g., macOS 14.0]
  - Python Version: [e.g., 3.13]
  - Node Version: [e.g., 18.16]
  - Package Versions: [relevant versions]
- **Screenshots**: If applicable
- **Logs**: Relevant error logs

### Bug Report Template

```markdown
## Bug Description
A clear and concise description of the bug.

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## Environment
- OS: macOS 14.0
- Python: 3.13
- Node: 18.16

## Additional Context
Any other context about the problem.
```

## 💡 Feature Requests

When suggesting a feature:

- **Title**: Clear and descriptive title
- **Problem**: Describe the problem your feature solves
- **Solution**: Describe your proposed solution
- **Alternatives**: Describe alternatives you've considered
- **Additional Context**: Any other context or screenshots

## 📚 Documentation

Help us improve documentation:

- Fix typos and grammatical errors
- Improve clarity and readability
- Add missing documentation
- Translate to other languages
- Add examples and tutorials

## 🔍 Code Review Process

All submissions require review. We use GitHub pull requests for this purpose:

1. At least one maintainer will review your PR
2. Feedback will be provided within 3-5 business days
3. Address review comments
4. Once approved, a maintainer will merge your PR

## 🎯 Areas Needing Help

We especially welcome contributions in these areas:

### High Priority
- [ ] Unit test coverage
- [ ] Integration tests
- [ ] Performance optimization
- [ ] Documentation improvements
- [ ] Internationalization (i18n)

### Medium Priority
- [ ] UI/UX improvements
- [ ] New agent implementations
- [ ] Additional MCP tools
- [ ] Error handling
- [ ] Logging improvements

### Low Priority
- [ ] Code refactoring
- [ ] Comment improvements
- [ ] Example projects
- [ ] Video tutorials

## 🌍 Translation

Help us translate EvoLabeler to other languages:

1. Check existing translations in `evolauncher-frontend/src/locales/`
2. Create a new file for your language (e.g., `fr.json`)
3. Translate all keys
4. Submit a PR

## ❓ Questions?

Feel free to ask questions:

- 💬 [GitHub Discussions](https://github.com/Ryder-MHumble/EvoLabeler-AIAgent-MLOps/discussions)
- 📧 Email: mhumble010221@gmail.com
- 🐛 [GitHub Issues](https://github.com/Ryder-MHumble/EvoLabeler-AIAgent-MLOps/issues)

## 📜 Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## 🙏 Thank You!

Your contributions make EvoLabeler better for everyone. We appreciate your time and effort!

---

<div align="center">

**Happy Contributing! 🎉**

</div>

