# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

We take the security of EvoLabeler seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Please Do Not

- Open a public GitHub issue for security vulnerabilities
- Discuss the vulnerability publicly before it has been addressed

### Please Do

1. **Email us directly**: Send an email to mhumble010221@gmail.com with:
   - Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting)
   - Full paths of source file(s) related to the issue
   - Location of the affected source code (tag/branch/commit or direct URL)
   - Any special configuration required to reproduce the issue
   - Step-by-step instructions to reproduce the issue
   - Proof-of-concept or exploit code (if possible)
   - Impact of the issue, including how an attacker might exploit it

2. **Wait for a response**: We will acknowledge your email within 48 hours and send a more detailed response within 5 business days indicating the next steps.

3. **Keep it confidential**: Please keep the issue confidential until we've had a chance to address it.

## Security Update Process

1. **Acknowledgment**: We will confirm receipt of your vulnerability report
2. **Assessment**: We will assess the vulnerability and determine its impact
3. **Fix Development**: We will develop a fix for the vulnerability
4. **Release**: We will release a security update
5. **Disclosure**: After the fix is released, we will publicly disclose the vulnerability

## Security Best Practices

### For Developers

1. **API Keys**: Never commit API keys or secrets to the repository
2. **Environment Variables**: Use `.env` files for sensitive configuration
3. **Dependencies**: Keep all dependencies up to date
4. **Input Validation**: Always validate and sanitize user inputs
5. **Authentication**: Use strong authentication mechanisms
6. **HTTPS**: Always use HTTPS in production

### For Users

1. **API Keys**: Keep your API keys secure and never share them
2. **Environment Files**: Never commit `.env` files to version control
3. **Updates**: Keep your installation up to date with the latest security patches
4. **Strong Passwords**: Use strong, unique passwords for database access
5. **Network Security**: Use firewalls and secure network configurations
6. **Access Control**: Implement proper access controls for your deployment

## Known Security Considerations

### API Security

- All API endpoints should be accessed over HTTPS in production
- API keys should be rotated regularly
- Rate limiting should be implemented to prevent abuse

### Database Security

- Use Supabase Row Level Security (RLS) policies
- Never expose service_role keys in client-side code
- Regularly audit database access logs

### File Upload Security

- File uploads are validated for type and size
- Uploaded files are scanned for malware (planned feature)
- Files are stored in isolated directories

### Frontend Security

- All user inputs are sanitized
- XSS protection is enabled
- CSP headers are configured

## Security Tools

We use the following tools to maintain security:

- **Backend**:
  - Ruff for Python linting
  - Bandit for security scanning
  - Safety for dependency vulnerability checking

- **Frontend**:
  - ESLint for JavaScript/TypeScript linting
  - npm audit for dependency vulnerability checking

## Disclosure Policy

- Security vulnerabilities will be disclosed after a fix is available
- We will credit security researchers who report vulnerabilities (if desired)
- A security advisory will be published on GitHub

## Contact

For security concerns, please contact:
- Email: mhumble010221@gmail.com
- GitHub: [@Ryder-MHumble](https://github.com/Ryder-MHumble)

## Acknowledgments

We would like to thank the following security researchers for their responsible disclosure:

- (List will be updated as vulnerabilities are reported and fixed)

---

**Last Updated**: 2024-12-04


