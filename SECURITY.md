# Security Policy

## Reporting Security Vulnerabilities

**Do not open public issues for security vulnerabilities.** 

If you discover a security vulnerability, please email [your-email@example.com] with:
- Description of the vulnerability
- Steps to reproduce (if applicable)
- Potential impact
- Suggested fix (if available)

We will respond within 48 hours and work on a fix.

## Supported Versions

Currently supported versions:

| Version | Status | End of Life |
|---------|--------|-------------|
| 1.0.x   | ✅ Active | TBD |

## Security Considerations

### Data Handling
- DynamiR does not store or transmit sequences to external servers (except NCBI for GenBank queries)
- NCBI queries are encrypted via SSL/TLS
- Local files are processed in-memory only

### NCBI Integration
- GenBank queries use standard HTTPS connections
- Consider setting `NCBI_EMAIL` in config.py for better service
- Rate limiting is respected to avoid IP blocking

### Input Validation
- Sequence inputs are validated for valid RNA/DNA characters
- File paths are validated before opening
- User inputs are properly escaped

## Dependencies

- **BioPython**: Regularly updated, actively maintained
- **Python**: Use Python 3.7+ for security patches
- **Tkinter**: Included with Python, subject to Python security patches

Keep dependencies updated:
```bash
pip install --upgrade biopython
```

## Best Practices

1. Keep Python updated to latest patch version
2. Keep BioPython updated
3. Run the application in a controlled environment
4. Report vulnerabilities responsibly
5. Use strong passwords if storing results

## Compliance

DynamiR does not process protected health information (PHI) or personally identifiable information (PII) by design. It is suitable for research use but should not be used with sensitive data without proper safeguards.
