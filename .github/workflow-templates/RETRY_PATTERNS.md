# Standardized Retry Logic Patterns

This document describes the standardized retry patterns used across Ansible collection CI/CD workflows.

## Overview

All workflows use the `nick-fields/retry@v3` action to handle transient failures and ensure reliable test execution and cleanup.

## Retry Patterns

### 1. Collection Build/Install Pattern

**Purpose**: Build and install the Ansible collection with retry logic to handle transient network or build issues.

**Configuration**:
- **Timeout**: 2 minutes
- **Max Attempts**: 3
- **Retry On**: error
- **Continue on Error**: No (fails the workflow if all attempts fail)

**Usage**:
```yaml
- name: Build/Install the collection
  uses: nick-fields/retry@v3
  with:
    timeout_minutes: 2
    max_attempts: 3
    retry_on: error
    command: |
      collection_file=$( basename $(ansible-galaxy collection build -f | awk -F" " '{print $NF}'))
      ansible-galaxy collection install $collection_file
```

**Rationale**: Collection builds are typically fast but can fail due to network issues or temporary file system problems. Three attempts with a 2-minute timeout provides sufficient resilience without excessive wait times.

### 2. Molecule Test Execution Pattern

**Purpose**: Execute Molecule integration tests with retry logic to handle transient AWS, network, or test infrastructure issues.

**Configuration**:
- **Timeout**: 30 minutes
- **Max Attempts**: 3
- **Retry On**: error
- **Continue on Error**: Yes (allows cleanup to run even if tests fail)

**Usage**:
```yaml
- name: Run role tests
  id: molecule-role-test
  uses: nick-fields/retry@v3
  env:
    MOLECULE_INSTANCE_NAME: ${{ matrix.molecule.distro }}-${{ matrix.collection_role }}
    MOLECULE_IMAGE_OWNER: ${{ matrix.molecule.image_owner }}
    MOLECULE_IMAGE_ARCH: ${{ matrix.molecule.image_arch }}
    MOLECULE_IMAGE_NAME: '${{ matrix.molecule.image_name }}'
    MOLECULE_INSTANCE_TYPE: ${{ matrix.molecule.instance_type }}
    MOLECULE_REGION: ${{ env.AWS_REGION}}
  with:
    timeout_minutes: 30
    max_attempts: 3
    retry_on: error
    command: >-
      molecule --version &&
      ansible --version &&
      molecule test --destroy never -s ${{ matrix.collection_role }} -- -v
  continue-on-error: true
```

**Rationale**: Integration tests can fail due to:
- AWS API rate limits or temporary service issues
- Network connectivity problems
- Transient test infrastructure issues
- Race conditions in test execution

The `continue-on-error: true` setting ensures that cleanup always runs, preventing resource leaks. The test outcome is captured in the step ID and asserted later.

### 3. EC2 Instance Cleanup Pattern

**Purpose**: Ensure EC2 instances are destroyed even if tests fail, preventing resource leaks and cost overruns.

**Configuration**:
- **Timeout**: 10 minutes
- **Max Attempts**: 3
- **Retry On**: error
- **Continue on Error**: No (this step must succeed)
- **Always Run**: Yes (runs even if previous steps fail)

**Usage**:
```yaml
- name: Ensure instances are destroyed
  uses: nick-fields/retry@v3
  env:
    MOLECULE_INSTANCE_NAME: ${{ matrix.molecule.distro }}-${{ matrix.collection_role }}
    MOLECULE_IMAGE_OWNER: ${{ matrix.molecule.image_owner }}
    MOLECULE_IMAGE_ARCH: ${{ matrix.molecule.image_arch }}
    MOLECULE_IMAGE_NAME: '${{ matrix.molecule.image_name }}'
    MOLECULE_INSTANCE_TYPE: ${{ matrix.molecule.instance_type }}
    MOLECULE_REGION: ${{ env.AWS_REGION}}
  with:
    timeout_minutes: 10
    max_attempts: 3
    retry_on: error
    command: >-
      molecule --version &&
      ansible --version &&
      molecule destroy -s ${{ matrix.collection_role }}
```

**Rationale**: Instance cleanup is critical to prevent:
- Resource leaks
- Cost overruns from orphaned EC2 instances
- VPC subnet exhaustion
- Security group conflicts

The cleanup step runs even if tests fail (due to `continue-on-error: true` on the test step) and retries up to 3 times to handle AWS API issues.

### 4. Test Assertion Pattern

**Purpose**: Assert that tests passed after cleanup is complete.

**Configuration**:
- Uses `nick-fields/assert-action@v2`
- Checks the outcome of the test step (not the retry wrapper)

**Usage**:
```yaml
- name: Assert molecule tests passed
  uses: nick-fields/assert-action@v2
  with:
    expected: success
    actual: ${{ steps.molecule-role-test.outcome }}
```

**Rationale**: By asserting after cleanup, we ensure:
1. Tests are properly evaluated
2. Resources are always cleaned up
3. Workflow fails if tests fail (after cleanup)
4. Clear failure indication in GitHub Actions UI

## Customization Guidelines

### Adjusting Timeouts

**Collection Build/Install**:
- Increase if your collection is very large (>100MB)
- Decrease for small collections (<10MB)
- Typical range: 1-5 minutes

**Molecule Test Execution**:
- Increase for complex tests with many tasks
- Increase for Windows tests (typically slower)
- Decrease for simple smoke tests
- Typical range: 15-45 minutes

**EC2 Instance Cleanup**:
- Rarely needs adjustment
- Increase if you have custom cleanup tasks
- Typical range: 5-15 minutes

### Adjusting Retry Attempts

**General Guidelines**:
- 3 attempts is the recommended default
- Increase to 5 for highly unreliable operations
- Decrease to 1 (no retry) for operations that should never be retried
- Never set to 0 (would disable the operation)

**When to Increase**:
- AWS API rate limiting is common in your environment
- Network connectivity is unreliable
- Tests have known transient failures

**When to Decrease**:
- Operation is idempotent and fast
- Failures are always permanent (not transient)
- You want faster feedback on failures

## Best Practices

1. **Always use retry logic for AWS operations**: AWS APIs can be rate-limited or temporarily unavailable.

2. **Always use retry logic for network operations**: Network issues are common in CI/CD environments.

3. **Always ensure cleanup runs**: Use `continue-on-error: true` on test steps and separate cleanup steps.

4. **Always assert test results**: Use the assert action to fail the workflow after cleanup.

5. **Use appropriate timeouts**: Balance between allowing operations to complete and failing fast.

6. **Monitor retry patterns**: If operations frequently require multiple retries, investigate root causes.

7. **Document custom retry patterns**: If you deviate from these standards, document why.

## Troubleshooting

### Tests Always Fail on First Attempt

**Symptoms**: Tests consistently fail on the first attempt but succeed on retry.

**Possible Causes**:
- Race condition in test setup
- Insufficient wait time for services to start
- AWS instance not fully ready

**Solutions**:
- Add explicit wait conditions in tests
- Increase boot wait time in Molecule configuration
- Add health checks before running tests

### Cleanup Always Requires Multiple Attempts

**Symptoms**: Cleanup step consistently needs 2-3 attempts to succeed.

**Possible Causes**:
- AWS API rate limiting
- Resources not fully released before cleanup
- Network connectivity issues

**Solutions**:
- Add delays before cleanup
- Increase cleanup timeout
- Check AWS service health status

### Timeouts Are Too Short

**Symptoms**: Operations timeout before completing, even on retry.

**Possible Causes**:
- Timeout value too low for operation complexity
- Performance degradation in CI environment
- Resource constraints (CPU, memory, network)

**Solutions**:
- Increase timeout values
- Optimize test execution
- Use larger instance types for tests
- Profile test execution to identify bottlenecks

## Integration with Composite Actions

The retry patterns are integrated into composite actions for easy reuse:

- **`build-install-collection`**: Implements collection build/install retry pattern
- **`molecule-test`**: Implements test execution and cleanup retry patterns

See the composite action documentation for usage examples.
