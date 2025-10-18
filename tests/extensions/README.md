# Conan Extensions Testing Suite

This directory contains comprehensive tests for all Conan extensions in the OpenSSL workspace.

## Test Structure

### Test Categories

1. **Commands Tests** (`test_commands.py`)
   - Custom command functionality
   - Command argument validation
   - Error handling and edge cases
   - Command integration scenarios

2. **Hooks Tests** (`test_hooks.py`)
   - Pre/post build hooks
   - Package hooks
   - Export hooks
   - Hook execution order and dependencies

3. **Deployers Tests** (`test_deployers.py`)
   - Cursor deployer functionality
   - Development environment deployment
   - Production deployment workflows
   - Rollback and recovery procedures

4. **Graph API Tests** (`test_graph_api.py`)
   - Dependency graph construction
   - Build graph analysis
   - Compliance graph validation
   - Graph persistence and querying

5. **Integration Tests** (`test_integration.py`)
   - Cross-extension workflows
   - End-to-end pipeline testing
   - Repository integration
   - Security workflow validation

6. **Performance Tests** (`test_performance.py`)
   - Execution time benchmarks
   - Resource usage monitoring
   - Scalability testing
   - Load and stress testing

## Test Configuration

### Common Fixtures (`conftest.py`)

- `temp_workspace`: Temporary workspace for testing
- `mock_conan_client`: Mocked Conan client
- `mock_subprocess`: Mocked subprocess calls
- `sample_conanfile`: Sample conanfile.py content
- `mock_fips_config`: Mock FIPS configuration
- `test_helper`: Extension test helper utilities

### Performance Monitoring

All tests include performance monitoring with:
- Execution time measurement
- Memory usage tracking
- CPU utilization monitoring
- Resource leak detection

## Running Tests

### Run All Tests

```bash
cd openssl-tools/tests/extensions
python test_runner.py
```

### Run Specific Test Categories

```bash
# Commands tests
pytest test_commands.py -v

# Hooks tests
pytest test_hooks.py -v

# Deployers tests
pytest test_deployers.py -v

# Graph API tests
pytest test_graph_api.py -v

# Integration tests
pytest test_integration.py -v

# Performance tests
pytest test_performance.py -v
```

### Run with Coverage

```bash
pytest --cov=extensions --cov-report=html
```

### Run Performance Benchmarks

```bash
pytest test_performance.py::TestPerformanceBenchmarks -v --tb=short
```

## Test Metrics and Reporting

### Success Criteria

- **Unit Tests**: >95% pass rate
- **Integration Tests**: >90% pass rate
- **Performance Tests**: Meet baseline performance metrics
- **FIPS Compliance**: All security tests pass

### Performance Baselines

| Operation | Baseline Time | Max Time |
|-----------|---------------|----------|
| Command Execution | <2.0s | <5.0s |
| Hook Execution | <1.0s | <2.0s |
| Deployment | <10.0s | <30.0s |
| Graph Construction | <5.0s | <10.0s |

### Resource Limits

- Memory Usage: <50MB increase per operation
- CPU Usage: <80% average utilization
- Disk I/O: <30s for large operations

## FIPS Compliance Testing

### FIPS Validation Tests

- Pre-build FIPS requirement checking
- Build artifact FIPS module validation
- Package FIPS compliance verification
- Post-deployment FIPS certification

### Security Workflow Tests

- SBOM generation and validation
- Vulnerability scanning integration
- Audit trail generation
- Compliance reporting

## Continuous Integration

### Automated Testing Pipeline

1. **Unit Tests**: Fast feedback on code changes
2. **Integration Tests**: Validate cross-extension workflows
3. **Performance Tests**: Detect performance regressions
4. **FIPS Tests**: Ensure security compliance

### Test Environments

- **Development**: Full test suite with coverage
- **Staging**: Integration and performance tests
- **Production**: FIPS compliance and security tests

## Troubleshooting

### Common Issues

1. **Mock Import Errors**
   - Ensure all extension modules are properly mocked
   - Check import paths in test files

2. **Performance Test Failures**
   - Verify system resources meet minimum requirements
   - Check for background processes affecting performance

3. **FIPS Test Failures**
   - Ensure FIPS configuration is properly mocked
   - Verify certificate validation logic

### Debug Mode

Run tests with debug output:

```bash
pytest -v -s --tb=long
```

### Profiling Tests

Profile slow tests:

```bash
pytest --profile test_performance.py
```

## Extension Development Guidelines

### Adding New Tests

1. Create test file in appropriate category
2. Use common fixtures from `conftest.py`
3. Include performance monitoring
4. Add FIPS compliance validation where applicable
5. Update test runner if needed

### Test Naming Conventions

- `test_*`: Unit tests
- `test_*_integration`: Integration tests
- `test_*_performance`: Performance tests
- `test_*_fips`: FIPS compliance tests

### Mock Strategy

- Mock external dependencies (Conan client, file system)
- Use realistic test data
- Validate mock interactions
- Test error conditions

## Metrics and Monitoring

### Test Dashboard

The test runner generates comprehensive reports including:

- Test execution summary
- Performance metrics
- FIPS compliance status
- Recommendations for improvements
- Cross-repository validation

### Alerting

Automated alerts for:
- Test failures >5%
- Performance regressions >20%
- FIPS compliance issues
- Resource usage anomalies

## Future Enhancements

### Planned Improvements

1. **Distributed Testing**: Run tests across multiple environments
2. **Load Testing**: Simulate production workloads
3. **Chaos Engineering**: Test failure scenarios
4. **AI-Powered Testing**: Generate tests from specifications

### Integration Points

- **CI/CD Pipeline**: Automated test execution
- **Monitoring Systems**: Real-time performance tracking
- **Security Scanners**: Automated vulnerability detection
- **Compliance Tools**: FIPS validation integration

## Support

For questions about the testing suite:

1. Check this README for common issues
2. Review test failure logs
3. Consult the main OpenSSL workspace documentation
4. File issues in the appropriate repository

