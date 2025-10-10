# GitHub Actions Workflow Management

This document provides comprehensive guidance for monitoring, analyzing, and fixing failed GitHub Actions workflows in the OpenSSL Tools project.

## Overview

The workflow management system consists of several tools designed to help you:

1. **Monitor** workflow runs and detect failures
2. **Analyze** failure patterns and root causes
3. **Automatically retry** failed jobs
4. **Generate health reports** and recommendations
5. **Implement best practices** for workflow resilience

## Tools Available

### 1. Workflow Monitor (`scripts/monitor-workflows.py`)

Monitors workflow runs and identifies failed jobs for automated remediation.

**Usage:**
```bash
# Check for failed jobs in the last 24 hours
python scripts/monitor-workflows.py

# Check for failed jobs in the last 48 hours
python scripts/monitor-workflows.py --hours 48

# Save report to file
python scripts/monitor-workflows.py --output workflow-report.txt
```

**Features:**
- Detects failed jobs automatically
- Categorizes failure types (dependency, build, test, timeout, etc.)
- Generates detailed failure reports
- Provides fix suggestions based on failure patterns

### 2. Workflow Recovery (`scripts/workflow-recovery.py`)

Automatically retries failed jobs and implements recovery strategies.

**Usage:**
```bash
# Retry a specific workflow run
python scripts/workflow-recovery.py --run-id 12345678

# Auto-retry all failed jobs
python scripts/workflow-recovery.py --auto-retry

# Retry with custom max attempts
python scripts/workflow-recovery.py --auto-retry --max-retries 5
```

**Features:**
- Intelligent retry logic for transient failures
- Automatic failure categorization
- Configurable retry limits
- Progress monitoring

### 3. Workflow Health Check (`scripts/workflow-health-check.py`)

Monitors workflow health and provides recommendations for improvement.

**Usage:**
```bash
# Check health for the last 30 days
python scripts/workflow-health-check.py

# Check health for the last 7 days
python scripts/workflow-health-check.py --days 7

# Save health report
python scripts/workflow-health-check.py --output health-report.md
```

**Features:**
- Comprehensive health metrics
- Success rate analysis
- Performance monitoring
- Configuration validation
- Best practice recommendations

### 4. Workflow Manager (`scripts/workflow-manager.py`)

Comprehensive tool that combines all functionality.

**Usage:**
```bash
# Check current status
python scripts/workflow-manager.py status

# Auto-fix failed workflows
python scripts/workflow-manager.py fix

# Perform health check
python scripts/workflow-manager.py health

# Retry specific run
python scripts/workflow-manager.py retry 12345678

# Monitor continuously
python scripts/workflow-manager.py monitor --interval 30

# Setup notifications
python scripts/workflow-manager.py notifications
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install requests pyyaml
```

### 2. Set GitHub Token

```bash
export GITHUB_TOKEN=your_github_token_here
```

### 3. Make Scripts Executable

```bash
chmod +x scripts/monitor-workflows.py
chmod +x scripts/workflow-recovery.py
chmod +x scripts/workflow-health-check.py
chmod +x scripts/workflow-manager.py
```

## Enhanced Workflow Features

### Retry Logic

The enhanced workflow (`conan-ci-enhanced.yml`) includes:

- **Automatic retries** for transient failures
- **Timeout configurations** to prevent hanging jobs
- **Continue-on-error** for non-critical steps
- **Resource optimization** with parallel job limits
- **Comprehensive error handling** and cleanup

### Key Improvements

1. **Resilience**: Built-in retry logic for common failure scenarios
2. **Performance**: Optimized parallel execution and caching
3. **Monitoring**: Better error reporting and job status tracking
4. **Resource Management**: Proper cleanup and resource limits

## Common Failure Scenarios and Solutions

### 1. Dependency Issues

**Symptoms:**
- "package not found" errors
- Import failures
- Version conflicts

**Solutions:**
- Update package versions
- Check import paths
- Verify dependency configurations

### 2. Build Errors

**Symptoms:**
- Compilation failures
- Make errors
- Build script issues

**Solutions:**
- Check compiler settings
- Update build scripts
- Verify environment setup

### 3. Test Failures

**Symptoms:**
- Test assertion failures
- Test timeouts
- Test environment issues

**Solutions:**
- Review test cases
- Update test data
- Check test environment

### 4. Timeout Issues

**Symptoms:**
- Jobs timing out
- Long execution times
- Resource exhaustion

**Solutions:**
- Increase timeout limits
- Optimize build performance
- Implement caching strategies

### 5. Network Issues

**Symptoms:**
- Connection failures
- Download timeouts
- External service errors

**Solutions:**
- Add retry logic
- Check external dependencies
- Implement fallback mechanisms

## Best Practices

### 1. Workflow Design

- Use `fail-fast: false` to allow all jobs to complete
- Implement proper timeout configurations
- Add retry logic for transient failures
- Use `continue-on-error` for non-critical steps

### 2. Monitoring

- Set up notifications for workflow failures
- Monitor success rates regularly
- Track performance metrics
- Analyze failure patterns

### 3. Recovery

- Implement automatic retry mechanisms
- Categorize failures for appropriate responses
- Use intelligent retry strategies
- Monitor retry success rates

### 4. Optimization

- Use caching to improve performance
- Optimize parallel execution
- Implement resource limits
- Regular cleanup of artifacts

## Automation Examples

### Daily Health Check

```bash
#!/bin/bash
# Run daily health check and send report
python scripts/workflow-health-check.py --days 7 --output daily-health-report.md
# Send report via email or Slack
```

### Continuous Monitoring

```bash
#!/bin/bash
# Monitor workflows continuously with auto-fix
export AUTO_FIX_ENABLED=true
python scripts/workflow-manager.py monitor --interval 30
```

### Weekly Analysis

```bash
#!/bin/bash
# Weekly comprehensive analysis
python scripts/workflow-health-check.py --days 30 --output weekly-report.md
python scripts/monitor-workflows.py --hours 168 --output weekly-failures.txt
```

## Troubleshooting

### Common Issues

1. **Token Permissions**: Ensure your GitHub token has the necessary permissions
2. **Rate Limiting**: GitHub API has rate limits; scripts include retry logic
3. **Network Issues**: Scripts include timeout and retry mechanisms
4. **File Permissions**: Ensure scripts are executable

### Getting Help

1. Check the script logs for detailed error messages
2. Verify GitHub token permissions
3. Test with a simple workflow run first
4. Review the generated reports for insights

## Integration with CI/CD

### GitHub Actions Integration

You can integrate these tools into your CI/CD pipeline:

```yaml
- name: Workflow Health Check
  run: |
    python scripts/workflow-health-check.py --days 7
    if [ $? -ne 0 ]; then
      echo "Health check failed"
      exit 1
    fi
```

### Scheduled Monitoring

```yaml
- name: Daily Workflow Monitoring
  run: |
    python scripts/workflow-manager.py status --hours 24
    python scripts/workflow-manager.py fix --max-retries 3
```

## Conclusion

This workflow management system provides comprehensive tools for maintaining healthy GitHub Actions workflows. By implementing these tools and following the best practices, you can significantly improve the reliability and performance of your CI/CD pipeline.

For questions or issues, please refer to the troubleshooting section or create an issue in the repository.
