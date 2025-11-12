# Ansible CI/CD Standardization Templates

This directory contains reusable workflow templates, composite actions, and configuration files for standardizing CI/CD pipelines across Ansible collection repositories.

## Overview

These templates were created based on the comprehensive CI/CD patterns from the `COG-GTM/ansible_collection_falcon` repository. They provide a standardized, reusable approach to:

- Quality gate workflows (linting, testing)
- Integration testing with Molecule and AWS EC2
- Collection release and publication
- Multi-platform testing (Linux, Windows)

## Quick Start

1. **Configure Secrets**: Set up required secrets in your repository (see [SECRETS_AND_VARIABLES.md](SECRETS_AND_VARIABLES.md))
2. **Copy Templates**: Copy the workflow templates and composite actions to your repository
3. **Customize Matrix**: Update matrix configuration files for your target platforms
4. **Create Workflows**: Reference the reusable workflows in your `.github/workflows/` directory

**Minimal Example**:

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  lint:
    uses: ./.github/workflow-templates/ansible-lint-reusable.yml
```

See [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) for comprehensive examples.

## Directory Structure

```
.github/
├── workflow-templates/              # Reusable workflow templates
│   ├── ansible-lint-reusable.yml
│   ├── python-lint-reusable.yml
│   ├── ansible-test-reusable.yml
│   ├── molecule-integration-test-reusable.yml
│   ├── collection-release-reusable.yml
│   ├── matrix-configs/              # Test matrix configurations
│   │   ├── linux-test-matrix.json
│   │   ├── windows-test-matrix.json
│   │   └── README.md
│   ├── RETRY_PATTERNS.md            # Retry logic documentation
│   ├── MOLECULE_SCENARIOS.md        # Molecule parameterization guide
│   ├── SECRETS_AND_VARIABLES.md     # Required secrets documentation
│   ├── USAGE_EXAMPLES.md            # Comprehensive usage examples
│   └── README.md                    # This file
└── actions/                         # Composite actions
    ├── setup-aws-credentials/
    │   └── action.yml
    ├── setup-python-ansible/
    │   └── action.yml
    ├── build-install-collection/
    │   └── action.yml
    └── molecule-test/
        └── action.yml
```

## Components

### Reusable Workflow Templates

#### 1. ansible-lint-reusable.yml

Simple Ansible linting workflow using `ansible-lint`.

**Key Features**:
- Configurable ansible-lint version
- Custom working directory support
- Checkout ref parameterization

**Usage**:
```yaml
jobs:
  lint:
    uses: ./.github/workflow-templates/ansible-lint-reusable.yml
    with:
      ansible_lint_version: 'v25.8.2'
```

#### 2. python-lint-reusable.yml

Parallel Python linting with flake8, pylint, and bandit.

**Key Features**:
- Three parallel linting jobs
- Configurable Python version
- Selective linter execution
- Custom target directory

**Usage**:
```yaml
jobs:
  lint:
    uses: ./.github/workflow-templates/python-lint-reusable.yml
    with:
      python_version: '3.11'
      target_directory: 'plugins/'
      run_bandit: true
```

#### 3. ansible-test-reusable.yml

Ansible sanity testing with ansible-test.

**Key Features**:
- Configurable ansible-core version
- Multiple testing types (sanity, units, integration)
- Pre-test command customization

**Usage**:
```yaml
jobs:
  test:
    uses: ./.github/workflow-templates/ansible-test-reusable.yml
    with:
      ansible_core_version: 'stable-2.18'
      testing_type: 'sanity'
```

#### 4. molecule-integration-test-reusable.yml

Comprehensive Molecule integration testing with AWS EC2.

**Key Features**:
- Dynamic matrix configuration
- AWS OIDC authentication
- Retry logic for tests and cleanup
- Windows support (pywinrm)
- Parameterized timeouts and retry attempts
- Collection-specific secret support

**Usage**:
```yaml
jobs:
  test:
    uses: ./.github/workflow-templates/molecule-integration-test-reusable.yml
    with:
      test_matrix: ${{ toJson(matrix_config) }}
      molecule_scenarios: '["install", "configure"]'
    secrets:
      AWS_OIDC_ROLE: ${{ secrets.AWS_OIDC_ROLE }}
      MOLECULE_VPC_SUBNET_ID: ${{ secrets.MOLECULE_VPC_SUBNET_ID }}
```

#### 5. collection-release-reusable.yml

Collection release and publication workflow.

**Key Features**:
- Ansible Galaxy publication
- GitHub release artifact upload
- Red Hat Automation Hub publication
- Parameterized collection namespace/name

**Usage**:
```yaml
jobs:
  release:
    uses: ./.github/workflow-templates/collection-release-reusable.yml
    with:
      collection_namespace: 'mycompany'
      collection_name: 'mycollection'
      publish_to_galaxy: true
    secrets:
      GALAXY_API_KEY: ${{ secrets.GALAXY_API_KEY }}
```

### Composite Actions

#### 1. setup-aws-credentials

Configures AWS credentials using OIDC authentication.

**Inputs**: `aws-oidc-role`, `aws-region`, `role-session-name`

**Usage**:
```yaml
- uses: ./.github/actions/setup-aws-credentials
  with:
    aws-oidc-role: ${{ secrets.AWS_OIDC_ROLE }}
    aws-region: 'us-west-2'
```

#### 2. setup-python-ansible

Sets up Python with caching and installs Ansible dependencies.

**Inputs**: `python-version`, `requirements-file`, `install-pywinrm`, `additional-dependencies`

**Usage**:
```yaml
- uses: ./.github/actions/setup-python-ansible
  with:
    python-version: '3.11'
    requirements-file: '.devcontainer/requirements.txt'
```

#### 3. build-install-collection

Builds and installs Ansible collection with retry logic.

**Inputs**: `timeout-minutes`, `max-attempts`, `force-build`

**Usage**:
```yaml
- uses: ./.github/actions/build-install-collection
  with:
    timeout-minutes: '2'
    max-attempts: '3'
```

#### 4. molecule-test

Executes Molecule test with retry logic and guaranteed cleanup.

**Inputs**: Multiple inputs for scenario configuration, instance details, and timeouts

**Outputs**: `test-outcome`

**Usage**:
```yaml
- uses: ./.github/actions/molecule-test
  with:
    scenario-name: 'my_scenario'
    molecule-instance-name: 'test-ubuntu'
    molecule-image-owner: '099720109477'
    molecule-image-arch: 'x86_64'
    molecule-image-name: 'ubuntu/images/hvm-ssd/ubuntu-jammy-22.04*'
    molecule-instance-type: 't2.micro'
    molecule-region: 'us-west-2'
```

### Matrix Configuration Files

Pre-configured test matrices for common platforms:

- **linux-test-matrix.json**: 8 Linux distributions (Ubuntu, Amazon Linux, SLES, AlmaLinux, RHEL) on x86_64 and arm64
- **windows-test-matrix.json**: Windows Server 2022

See [matrix-configs/README.md](matrix-configs/README.md) for detailed documentation.

## Documentation

### Core Documentation

- **[USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)**: Comprehensive usage examples for all templates and actions
- **[SECRETS_AND_VARIABLES.md](SECRETS_AND_VARIABLES.md)**: Required secrets and variables documentation
- **[RETRY_PATTERNS.md](RETRY_PATTERNS.md)**: Standardized retry logic patterns
- **[MOLECULE_SCENARIOS.md](MOLECULE_SCENARIOS.md)**: Molecule scenario parameterization guide
- **[matrix-configs/README.md](matrix-configs/README.md)**: Matrix configuration documentation

### Quick Reference

| Topic | Documentation |
|-------|---------------|
| Getting Started | [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md#quick-start) |
| Required Secrets | [SECRETS_AND_VARIABLES.md](SECRETS_AND_VARIABLES.md#required-secrets) |
| Matrix Configuration | [matrix-configs/README.md](matrix-configs/README.md) |
| Retry Logic | [RETRY_PATTERNS.md](RETRY_PATTERNS.md) |
| Molecule Variables | [MOLECULE_SCENARIOS.md](MOLECULE_SCENARIOS.md#environment-variables) |
| Troubleshooting | [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md#troubleshooting) |

## Key Features

### 1. Standardized Retry Logic

All workflows use `nick-fields/retry@v3` with standardized patterns:

- **Collection Build**: 2 min timeout, 3 attempts
- **Molecule Tests**: 30 min timeout, 3 attempts, continue-on-error
- **EC2 Cleanup**: 10 min timeout, 3 attempts, guaranteed execution

See [RETRY_PATTERNS.md](RETRY_PATTERNS.md) for details.

### 2. Parameterized Molecule Scenarios

Molecule scenarios use environment variables for complete parameterization:

- Platform configuration (AMI owner, architecture, name pattern)
- Instance configuration (type, region, subnet)
- Security settings (CIDR restrictions, boot wait time)
- Collection-specific variables (API credentials, CID, tokens)

See [MOLECULE_SCENARIOS.md](MOLECULE_SCENARIOS.md) for details.

### 3. Dynamic Matrix Configuration

Test matrices are externalized to JSON files for easy maintenance:

```yaml
strategy:
  matrix: ${{ fromJson(inputs.test_matrix) }}
```

Supports matrix exclusions and custom configurations.

See [matrix-configs/README.md](matrix-configs/README.md) for details.

### 4. Security Patterns

- **OIDC Authentication**: AWS authentication without long-lived credentials
- **Secret Management**: Comprehensive secret documentation and best practices
- **PR Security**: `pull_request_target` with `ok-to-test` label pattern
- **Least Privilege**: IAM roles with minimum required permissions

See [SECRETS_AND_VARIABLES.md](SECRETS_AND_VARIABLES.md#security-best-practices) for details.

### 5. Multi-Platform Support

- **Linux**: 8 distributions across x86_64 and arm64
- **Windows**: Windows Server 2022 with pywinrm support
- **Conditional Dependencies**: Platform-specific dependency installation

## Implementation Strategy

This template collection implements a 5-step standardization strategy:

### Step 1: Reusable Workflow Templates

Convert existing workflows to use `workflow_call` triggers with parameterized inputs for:
- Python versions
- Molecule scenarios
- Matrix configurations
- Timeout values
- Collection-specific settings

### Step 2: Composite Actions

Extract common step sequences into reusable composite actions:
- AWS OIDC authentication
- Python and Ansible setup
- Collection build/install
- Molecule test execution with cleanup

### Step 3: Standardized Retry Logic

Preserve and document retry patterns using `nick-fields/retry@v3`:
- Build/install operations
- Test execution
- EC2 cleanup (guaranteed)

### Step 4: Matrix Configuration Files

Externalize OS matrix configurations to JSON files:
- Linux distributions (Ubuntu, Amazon Linux, SLES, AlmaLinux, RHEL)
- Windows Server versions
- Architecture variants (x86_64, arm64)
- Dynamic loading with `fromJson()`

### Step 5: Parameterized Molecule Scenarios

Document and leverage environment variable parameterization:
- Platform settings with defaults
- Instance configuration
- Collection-specific variables
- Reusable across all scenarios

## Required Secrets

Minimum required secrets for integration testing:

- `AWS_OIDC_ROLE`: IAM role ARN for AWS authentication
- `MOLECULE_VPC_SUBNET_ID`: VPC subnet for EC2 instances

Additional secrets for collection-specific operations:

- `COLLECTION_API_CLIENT_ID`: API client ID
- `COLLECTION_API_CLIENT_SECRET`: API client secret
- `COLLECTION_CID`: Customer/Client ID
- `COLLECTION_PROV_TOKEN`: Provisioning token

Release secrets:

- `GALAXY_API_KEY`: Ansible Galaxy API key
- `AUTOMATION_HUB_TOKEN`: Red Hat Automation Hub token
- `GITHUB_TOKEN`: GitHub token (usually automatic)

See [SECRETS_AND_VARIABLES.md](SECRETS_AND_VARIABLES.md) for complete documentation.

## Best Practices

1. **Start Simple**: Begin with basic linting workflows, add complexity incrementally
2. **Use Matrix Files**: Externalize matrix configurations for easier maintenance
3. **Stagger Schedules**: Run Linux tests at different times than Windows tests
4. **Monitor Costs**: Track AWS EC2 costs from test infrastructure
5. **Test Locally**: Validate Molecule scenarios locally before adding to CI/CD
6. **Security First**: Always use OIDC authentication and secret management
7. **Clean Up Resources**: Ensure EC2 instances are always destroyed
8. **Document Changes**: Keep workflow documentation up to date
9. **Version Control**: Commit workflow changes with descriptive messages
10. **Fail Fast**: Use appropriate timeout values and retry attempts

## Migration Guide

### From Inline Workflows

**Before**:
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-python@v5
      - run: pip install ansible
      - run: ansible-lint
```

**After**:
```yaml
jobs:
  test:
    uses: ./.github/workflow-templates/ansible-lint-reusable.yml
```

### From Complex Molecule Workflows

Replace 50+ lines of workflow configuration with a single reusable workflow call. See [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md#migration-guide) for detailed examples.

## Troubleshooting

### Common Issues

1. **Workflow not found**: Verify file path and YAML syntax
2. **Secret not accessible**: Ensure secrets are passed in `secrets:` section
3. **Matrix too large**: Use exclusions or split into multiple workflows
4. **AMI not found**: Verify image owner, architecture, and name pattern
5. **Instance type unavailable**: Check instance type availability in region

See [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md#troubleshooting) for detailed troubleshooting.

## Examples

### Complete CI/CD Pipeline

```yaml
name: CI/CD

on: [push, pull_request, release]

jobs:
  lint:
    uses: ./.github/workflow-templates/ansible-lint-reusable.yml

  test:
    needs: lint
    uses: ./.github/workflow-templates/molecule-integration-test-reusable.yml
    with:
      test_matrix: ${{ toJson(matrix) }}
      molecule_scenarios: '["install"]'
    secrets:
      AWS_OIDC_ROLE: ${{ secrets.AWS_OIDC_ROLE }}
      MOLECULE_VPC_SUBNET_ID: ${{ secrets.MOLECULE_VPC_SUBNET_ID }}

  release:
    if: github.event_name == 'release'
    needs: test
    uses: ./.github/workflow-templates/collection-release-reusable.yml
    with:
      collection_namespace: 'mycompany'
      collection_name: 'mycollection'
    secrets:
      GALAXY_API_KEY: ${{ secrets.GALAXY_API_KEY }}
```

See [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) for 15+ comprehensive examples.

## Contributing

When contributing to these templates:

1. Test changes thoroughly before committing
2. Update documentation to reflect changes
3. Follow existing patterns and conventions
4. Add examples for new features
5. Maintain backward compatibility when possible

## Support

For issues or questions:

1. Review the documentation in this directory
2. Check workflow logs for error messages
3. Verify secrets and variables are configured correctly
4. Test locally before running in CI/CD
5. Contact repository maintainers for assistance

## License

These templates are based on the CI/CD patterns from the `COG-GTM/ansible_collection_falcon` repository and are provided as-is for use across Ansible collection repositories.

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Reusable Workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
- [Composite Actions](https://docs.github.com/en/actions/creating-actions/creating-a-composite-action)
- [Molecule Documentation](https://molecule.readthedocs.io/)
- [Ansible Documentation](https://docs.ansible.com/)
- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
