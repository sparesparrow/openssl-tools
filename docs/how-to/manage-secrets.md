# Secrets Management Guide

This guide provides comprehensive instructions for managing secrets and credentials used by the OpenSSL Tools repository.

## Table of Contents

- [Overview](#overview)
- [Secret Categories](#secret-categories)
- [GitHub Secrets Setup](#github-secrets-setup)
- [Secret Rotation](#secret-rotation)
- [Security Best Practices](#security-best-practices)
- [Troubleshooting](#troubleshooting)
- [Emergency Procedures](#emergency-procedures)

## Overview

The OpenSSL Tools repository uses various secrets and credentials for:

- **Authentication**: Access to external services
- **Package Management**: Conan and Artifactory integration
- **CI/CD**: GitHub Actions and workflow automation
- **Security**: Package signing and validation

## Secret Categories

### 1. Core Authentication Secrets

These are the essential secrets required for basic functionality:

```yaml
# GitHub Integration
OPENSSL_TOOLS_TOKEN: "ghp_xxxxxxxxxxxxxxxxxxxx"
GITHUB_TOKEN: "ghp_xxxxxxxxxxxxxxxxxxxx"

# Conan Package Management
CONAN_LOGIN_USERNAME: "openssl-ci"
CONAN_PASSWORD: "secure-password-here"
```

### 2. Artifactory Secrets

Required for JFrog Artifactory integration:

```yaml
# Artifactory Connection
ARTIFACTORY_URL: "https://your-instance.jfrog.io"
ARTIFACTORY_USERNAME: "openssl-ci"
ARTIFACTORY_PASSWORD: "secure-password-here"
ARTIFACTORY_API_KEY: "AKCp8xxxxxxxxxxxxxxxxxxxx"

# Optional: Package Signing
ARTIFACTORY_SIGNING_KEY: "-----BEGIN PRIVATE KEY-----..."
ARTIFACTORY_SIGNING_PASSPHRASE: "signing-passphrase-here"
```

### 3. Build and Deployment Secrets

Used for build processes and deployment:

```yaml
# Build Configuration
BUILD_SECRET_KEY: "build-secret-key-here"
CACHE_SECRET: "cache-secret-here"

# Deployment
DEPLOY_TOKEN: "deploy-token-here"
RELEASE_SECRET: "release-secret-here"
```

### 4. External Service Secrets

For integration with external services:

```yaml
# Package Registries
NPM_TOKEN: "npm_xxxxxxxxxxxxxxxxxxxx"
PYPI_TOKEN: "pypi-xxxxxxxxxxxxxxxxxxxx"

# Monitoring and Analytics
SENTRY_DSN: "https://xxxxxxxxxxxxxxxxxxxx@sentry.io/xxxxxxx"
ANALYTICS_KEY: "analytics-key-here"
```

## GitHub Secrets Setup

### 1. Accessing Secrets Management

1. Go to your GitHub repository
2. Click on **Settings** tab
3. Navigate to **Secrets and variables** → **Actions**
4. Click **New repository secret**

### 2. Adding Secrets

For each secret:

1. **Name**: Use the exact name from the secret categories above
2. **Value**: Enter the secret value
3. **Description**: Add a brief description (optional)
4. **Click**: **Add secret**

### 3. Required Secrets Checklist

- [ ] `OPENSSL_TOOLS_TOKEN`
- [ ] `GITHUB_TOKEN`
- [ ] `CONAN_LOGIN_USERNAME`
- [ ] `CONAN_PASSWORD`
- [ ] `ARTIFACTORY_URL`
- [ ] `ARTIFACTORY_USERNAME`
- [ ] `ARTIFACTORY_PASSWORD`
- [ ] `ARTIFACTORY_API_KEY`

### 4. Optional Secrets Checklist

- [ ] `ARTIFACTORY_SIGNING_KEY`
- [ ] `ARTIFACTORY_SIGNING_PASSPHRASE`
- [ ] `BUILD_SECRET_KEY`
- [ ] `CACHE_SECRET`
- [ ] `DEPLOY_TOKEN`
- [ ] `RELEASE_SECRET`

## Secret Rotation

### 1. Rotation Schedule

- **Critical Secrets**: Every 90 days
- **Standard Secrets**: Every 180 days
- **Low-Risk Secrets**: Every 365 days

### 2. Rotation Process

#### Step 1: Generate New Secret

1. Generate a new secret value
2. Test the new secret locally
3. Verify it works with the service

#### Step 2: Update GitHub Secrets

1. Go to GitHub repository settings
2. Navigate to **Secrets and variables** → **Actions**
3. Click on the secret to update
4. Enter the new value
5. Click **Update secret**

#### Step 3: Test Workflows

1. Trigger a test workflow
2. Verify all steps complete successfully
3. Check logs for any authentication errors

#### Step 4: Clean Up Old Secret

1. Once confirmed working, revoke the old secret
2. Update any local configurations
3. Document the change

### 3. Rotation Checklist

- [ ] Generate new secret
- [ ] Test new secret locally
- [ ] Update GitHub secret
- [ ] Test workflow execution
- [ ] Revoke old secret
- [ ] Update documentation
- [ ] Notify team members

## Security Best Practices

### 1. Secret Generation

#### Strong Passwords
- Minimum 16 characters
- Mix of uppercase, lowercase, numbers, symbols
- Avoid dictionary words
- Use password managers

#### API Keys
- Use service-specific key generation
- Set appropriate expiration dates
- Limit permissions to minimum required
- Use different keys for different environments

### 2. Secret Storage

#### GitHub Secrets
- Use GitHub's built-in secret management
- Never commit secrets to code
- Use environment-specific secrets when possible
- Regularly audit secret access

#### Local Development
- Use environment variables
- Never hardcode secrets in code
- Use `.env` files (excluded from git)
- Use secret management tools

### 3. Access Control

#### Principle of Least Privilege
- Grant minimum required permissions
- Use dedicated service accounts
- Regularly review access permissions
- Implement proper authentication

#### Monitoring and Auditing
- Log secret usage
- Monitor for unauthorized access
- Regular security audits
- Incident response procedures

### 4. Secret Sharing

#### Secure Communication
- Use encrypted channels
- Verify recipient identity
- Use temporary sharing methods
- Document sharing events

#### Team Access
- Limit access to necessary personnel
- Use role-based access control
- Regular access reviews
- Proper onboarding/offboarding

## Troubleshooting

### Common Issues

#### 1. Authentication Failures

**Symptoms**:
- Workflows fail with authentication errors
- Package uploads fail
- API calls return 401/403 errors

**Solutions**:
- Verify secret names match exactly
- Check secret values are correct
- Ensure secrets are not expired
- Verify user permissions

#### 2. Secret Not Found

**Symptoms**:
- Workflow fails with "secret not found" error
- Environment variable is empty

**Solutions**:
- Check secret name spelling
- Verify secret is set in correct repository
- Ensure secret is accessible to workflow
- Check repository permissions

#### 3. Invalid Secret Format

**Symptoms**:
- Service rejects secret format
- Parsing errors in workflows

**Solutions**:
- Check secret format requirements
- Verify encoding (base64, etc.)
- Remove extra whitespace
- Test secret format locally

### Debugging Steps

1. **Check Secret Names**: Ensure exact case and spelling
2. **Verify Values**: Test secrets manually
3. **Check Permissions**: Verify user has access
4. **Review Logs**: Check workflow logs for details
5. **Test Locally**: Test commands with secrets locally

### Getting Help

- Check workflow logs for specific errors
- Review service documentation
- Consult security team
- Open GitHub issue for repository-specific problems

## Emergency Procedures

### 1. Secret Compromise

If a secret is compromised:

1. **Immediately revoke** the compromised secret
2. **Generate new secret** with different value
3. **Update GitHub secrets** with new value
4. **Test workflows** to ensure functionality
5. **Investigate** how compromise occurred
6. **Document incident** and lessons learned

### 2. Secret Loss

If a secret is lost:

1. **Generate new secret** from service
2. **Update GitHub secrets** with new value
3. **Test workflows** to ensure functionality
4. **Update documentation** with new secret
5. **Notify team members** of change

### 3. Service Outage

If a service is unavailable:

1. **Check service status** page
2. **Use backup secrets** if available
3. **Implement fallback** procedures
4. **Monitor service** for restoration
5. **Update team** on status

## Monitoring and Alerting

### 1. Secret Usage Monitoring

- Monitor secret access patterns
- Alert on unusual usage
- Track secret rotation compliance
- Log all secret operations

### 2. Workflow Monitoring

- Monitor workflow success rates
- Alert on authentication failures
- Track secret-related errors
- Monitor service availability

### 3. Security Monitoring

- Monitor for secret exposure
- Alert on unauthorized access
- Track permission changes
- Monitor compliance violations

## Compliance and Auditing

### 1. Regular Audits

- Quarterly secret inventory
- Annual security review
- Compliance assessments
- Penetration testing

### 2. Documentation

- Maintain secret inventory
- Document rotation procedures
- Track access permissions
- Record incident responses

### 3. Training

- Security awareness training
- Secret management procedures
- Incident response training
- Regular updates and refreshers

## Conclusion

Proper secrets management is critical for the security and functionality of the OpenSSL Tools repository. Follow this guide to ensure secrets are managed securely and effectively.

For additional support or questions, please refer to the troubleshooting section or open an issue on GitHub.

## Appendix

### A. Secret Naming Conventions

- Use UPPER_CASE with underscores
- Be descriptive but concise
- Include service name when applicable
- Avoid abbreviations when possible

### B. Secret Value Requirements

- Minimum 16 characters for passwords
- Use strong, unique values
- Avoid predictable patterns
- Include special characters

### C. Rotation Schedule Template

| Secret Type | Rotation Frequency | Last Rotated | Next Due |
|-------------|-------------------|--------------|----------|
| API Keys | 90 days | YYYY-MM-DD | YYYY-MM-DD |
| Passwords | 90 days | YYYY-MM-DD | YYYY-MM-DD |
| Tokens | 180 days | YYYY-MM-DD | YYYY-MM-DD |

### D. Emergency Contacts

- Security Team: security@yourdomain.com
- DevOps Team: devops@yourdomain.com
- On-Call: +1-XXX-XXX-XXXX