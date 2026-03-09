# DynamiR Development & Maintenance

## GitHub Actions Workflows (Optional, for future automation)

You can add these files to `.github/workflows/` for CI/CD:

### `.github/workflows/tests.yml`
- Run tests on every push/PR
- Check code quality with flake8/black
- Build documentation

### `.github/workflows/release.yml`
- Automate releases
- Build and publish to PyPI

## Managing the Project

### Adding Changes

```bash
# 1. Create feature branch
git checkout -b feature/new-analysis-mode

# 2. Make changes and commit
git add .
git commit -m "Add new analysis mode"

# 3. Push and create PR
git push origin feature/new-analysis-mode
```

### Releases

Update version in:
- `setup.py`: version="X.Y.Z"
- Tag: `git tag vX.Y.Z`

### Code Quality

```bash
# Format code
black .

# Check style
flake8 .

# Type checking (if implemented)
mypy .

# Run tests (when implemented)
pytest
```

## Future Improvements

- [ ] Add comprehensive unit tests
- [ ] Implement CI/CD pipeline
- [ ] Add logging system
- [ ] Create Docker image
- [ ] Add API documentation
- [ ] Implement caching for NCBI queries
- [ ] Add progress bars for long operations
- [ ] Support for additional file formats
- [ ] Configuration file support
- [ ] Batch processing capabilities
