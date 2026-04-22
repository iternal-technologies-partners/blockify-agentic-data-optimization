# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

- **Email:** support@iternal.ai (with subject line: `[SECURITY] Blockify Vulnerability Report`)
- **Do not** open a public GitHub issue for security concerns

### What to Include

- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested mitigation (if known)
- Your contact information for follow-up

### Our Commitment

- We will acknowledge your report within 2 business days
- We will provide an initial assessment within 5 business days
- We will coordinate disclosure timing with you once a fix is ready
- We credit researchers in release notes (if desired)

## Handling API Keys and Secrets

> **Never commit API keys, tokens, or credentials to this repository.**

- Use `.env` files for local development (already in `.gitignore`)
- Use `.env.example` files as templates (committed, but empty values only)
- For production deployments, use secret management systems (Kubernetes Secrets, Vault, AWS Secrets Manager, etc.)
- Rotate any accidentally committed credentials immediately

## Enterprise Support

For enterprise customers running the productionized Blockify containers, additional security features are available including audit logging, role-based access control, and hardened deployment configurations. Contact sales@iternal.ai for details.
