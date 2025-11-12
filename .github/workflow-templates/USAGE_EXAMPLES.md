# Usage Examples

This document provides comprehensive examples for using the reusable CI/CD workflow templates and composite actions.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Reusable Workflow Examples](#reusable-workflow-examples)
3. [Composite Action Examples](#composite-action-examples)
4. [Complete Integration Examples](#complete-integration-examples)
5. [Advanced Patterns](#advanced-patterns)
6. [Migration Guide](#migration-guide)

## Quick Start

### Prerequisites

1. Configure required secrets in your repository (see [SECRETS_AND_VARIABLES.md](SECRETS_AND_VARIABLES.md))
2. Copy workflow templates to your repository
3. Create matrix configuration files for your test platforms
4. Update collection-specific variables

### Minimal Setup

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  lint:
    uses: ./.github/workflow-templates/ansible-lint-reusable.yml
```

## Reusable Workflow Examples

### Example 1: Ansible Lint

**File**: `.github/workflows/ansible-lint.yml`

```yaml
name: Ansible Lint

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  ansible_lint:
    uses: ./.github/workflow-templates/ansible-lint-reusable.yml
    with:
      ansible_lint_version: 'v25.8.2'
```

**Customization Options**:

```yaml
jobs:
  ansible_lint:
    uses: ./.github/workflow-templates/ansible-lint-reusable.yml
    with:
      checkout_ref: 'develop'                    # Test specific branch
      ansible_lint_version: 'v24.7.0'            # Use older version
      working_directory: 'ansible-collections'   # Custom directory
```

### Example 2: Python Linting

**File**: `.github/workflows/python-lint.yml`

```yaml
name: Python Lint

on:
  push:
    paths:
      - 'plugins/**'
  pull_request:
    paths:
      - 'plugins/**'

jobs:
  python_lint:
    uses: ./.github/workflow-templates/python-lint-reusable.yml
    with:
      python_version: '3.11'
      target_directory: 'plugins/'
      run_flake8: true
      run_pylint: true
      run_bandit: true
```

**Selective Linting**:

```yaml
jobs:
  # Only run flake8 for quick checks
  quick_lint:
    uses: ./.github/workflow-templates/python-lint-reusable.yml
    with:
      run_flake8: true
      run_pylint: false
      run_bandit: false

  # Full security scan
  security_lint:
    uses: ./.github/workflow-templates/python-lint-reusable.yml
    with:
      run_flake8: false
      run_pylint: false
      run_bandit: true
```

### Example 3: Ansible Test (Sanity)

**File**: `.github/workflows/ansible-test.yml`

```yaml
name: Ansible Test

on:
  push:
    branches: [ main ]
    paths:
      - 'plugins/**'
  pull_request:
    paths:
      - 'plugins/**'

jobs:
  ansible_test:
    uses: ./.github/workflow-templates/ansible-test-reusable.yml
    with:
      ansible_core_version: 'stable-2.18'
      testing_type: 'sanity'
```

**Multiple Ansible Versions**:

```yaml
jobs:
  ansible_test:
    strategy:
      matrix:
        ansible_version: ['stable-2.16', 'stable-2.17', 'stable-2.18']
    uses: ./.github/workflow-templates/ansible-test-reusable.yml
    with:
      ansible_core_version: ${{ matrix.ansible_version }}
      testing_type: 'sanity'
```

### Example 4: Molecule Integration Testing (Linux)

**File**: `.github/workflows/integration-test-linux.yml`

```yaml
name: Integration Test - Linux

on:
  schedule:
    - cron: '0 4 * * *'  # Daily at 4 AM UTC
  push:
    paths:
      - 'roles/**'
      - 'molecule/**'
  pull_request_target:
    types: [ labeled ]

jobs:
  integration_test:
    if: |
      github.event_name == 'push' ||
      github.event_name == 'schedule' ||
      (github.event_name == 'pull_request_target' &&
      github.event.label.name == 'ok-to-test')
    uses: ./.github/workflow-templates/molecule-integration-test-reusable.yml
    with:
      test_matrix: |
        {
          "molecule": [
            {
              "distro": "ubuntu-22.04",
              "image_owner": "099720109477",
              "image_arch": "x86_64",
              "image_name": "ubuntu/images/hvm-ssd/ubuntu-jammy-22.04*",
              "instance_type": "t2.micro"
            }
          ],
          "collection_role": ["my_role"]
        }
      molecule_scenarios: '["my_role"]'
      aws_region: 'us-west-2'
    secrets:
      AWS_OIDC_ROLE: ${{ secrets.AWS_OIDC_ROLE }}
      MOLECULE_VPC_SUBNET_ID: ${{ secrets.MOLECULE_VPC_SUBNET_ID }}
      COLLECTION_API_CLIENT_ID: ${{ secrets.MY_API_CLIENT_ID }}
      COLLECTION_API_CLIENT_SECRET: ${{ secrets.MY_API_CLIENT_SECRET }}
```

**Using External Matrix File**:

```yaml
jobs:
  load_matrix:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.set-matrix.outputs.matrix }}
    steps:
      - uses: actions/checkout@v5
      - id: set-matrix
        run: |
          MATRIX=$(cat .github/workflow-templates/matrix-configs/linux-test-matrix.json)
          # Add collection_role to matrix
          MATRIX=$(echo $MATRIX | jq '. + {"collection_role": ["role1", "role2"]}')
          echo "matrix=$MATRIX" >> $GITHUB_OUTPUT

  integration_test:
    needs: load_matrix
    uses: ./.github/workflow-templates/molecule-integration-test-reusable.yml
    with:
      test_matrix: ${{ needs.load_matrix.outputs.matrix }}
      molecule_scenarios: '["role1", "role2"]'
    secrets:
      AWS_OIDC_ROLE: ${{ secrets.AWS_OIDC_ROLE }}
      MOLECULE_VPC_SUBNET_ID: ${{ secrets.MOLECULE_VPC_SUBNET_ID }}
```

### Example 5: Molecule Integration Testing (Windows)

**File**: `.github/workflows/integration-test-windows.yml`

```yaml
name: Integration Test - Windows

on:
  schedule:
    - cron: '0 7 * * *'  # Daily at 7 AM UTC (staggered from Linux)
  push:
    paths:
      - 'roles/**'
      - 'molecule/win_*/**'

jobs:
  integration_test:
    uses: ./.github/workflow-templates/molecule-integration-test-reusable.yml
    with:
      test_matrix: |
        {
          "molecule": [
            {
              "distro": "WindowsServer2022",
              "image_owner": "801119661308",
              "image_arch": "x86_64",
              "image_name": "Windows_Server-2022-English-Full-Base-*",
              "instance_type": "t3a.medium"
            }
          ],
          "collection_role": ["win_my_role"]
        }
      molecule_scenarios: '["win_my_role"]'
      install_pywinrm: true  # Required for Windows
      test_timeout_minutes: 45  # Windows tests take longer
    secrets:
      AWS_OIDC_ROLE: ${{ secrets.AWS_OIDC_ROLE }}
      MOLECULE_VPC_SUBNET_ID: ${{ secrets.MOLECULE_VPC_SUBNET_ID }}
```

### Example 6: Collection Release

**File**: `.github/workflows/release.yml`

```yaml
name: Release

on:
  release:
    types: [ created ]

jobs:
  release:
    uses: ./.github/workflow-templates/collection-release-reusable.yml
    with:
      collection_namespace: 'mycompany'
      collection_name: 'mycollection'
      publish_to_galaxy: true
      publish_to_github: true
      publish_to_automation_hub: false
    secrets:
      GALAXY_API_KEY: ${{ secrets.GALAXY_API_KEY }}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**Publishing to Automation Hub**:

```yaml
jobs:
  release:
    uses: ./.github/workflow-templates/collection-release-reusable.yml
    with:
      collection_namespace: 'mycompany'
      collection_name: 'mycollection'
      publish_to_galaxy: true
      publish_to_github: true
      publish_to_automation_hub: true
      automation_hub_url: 'https://console.redhat.com/api/automation-hub/content/inbound-mycompany/'
    secrets:
      GALAXY_API_KEY: ${{ secrets.GALAXY_API_KEY }}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      AUTOMATION_HUB_TOKEN: ${{ secrets.AAP_KEY }}
```

## Composite Action Examples

### Example 7: Setup AWS Credentials

**In a Custom Workflow**:

```yaml
jobs:
  custom_job:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: actions/checkout@v5

      - name: Configure AWS
        uses: ./.github/actions/setup-aws-credentials
        with:
          aws-oidc-role: ${{ secrets.AWS_OIDC_ROLE }}
          aws-region: 'us-west-2'

      - name: Use AWS CLI
        run: aws ec2 describe-instances
```

**Multiple Regions**:

```yaml
jobs:
  multi_region:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        region: ['us-west-2', 'eu-west-1', 'ap-southeast-1']
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: actions/checkout@v5

      - name: Configure AWS for ${{ matrix.region }}
        uses: ./.github/actions/setup-aws-credentials
        with:
          aws-oidc-role: ${{ secrets.AWS_OIDC_ROLE }}
          aws-region: ${{ matrix.region }}

      - name: Deploy to ${{ matrix.region }}
        run: echo "Deploying to ${{ matrix.region }}"
```

### Example 8: Setup Python and Ansible

**In a Custom Workflow**:

```yaml
jobs:
  custom_test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5

      - name: Setup Python and Ansible
        uses: ./.github/actions/setup-python-ansible
        with:
          python-version: '3.11'
          requirements-file: '.devcontainer/requirements.txt'

      - name: Run custom Ansible playbook
        run: ansible-playbook playbooks/test.yml
```

**With Windows Support**:

```yaml
jobs:
  windows_test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5

      - name: Setup Python and Ansible with WinRM
        uses: ./.github/actions/setup-python-ansible
        with:
          python-version: '3.11'
          requirements-file: '.devcontainer/requirements.txt'
          install-pywinrm: 'true'

      - name: Test Windows connectivity
        run: ansible windows -m win_ping
```

**With Additional Dependencies**:

```yaml
jobs:
  custom_deps:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5

      - name: Setup Python and Ansible with extras
        uses: ./.github/actions/setup-python-ansible
        with:
          python-version: '3.11'
          requirements-file: '.devcontainer/requirements.txt'
          additional-dependencies: 'jmespath netaddr'

      - name: Run playbook with filters
        run: ansible-playbook playbooks/advanced.yml
```

### Example 9: Build and Install Collection

**In a Custom Workflow**:

```yaml
jobs:
  test_collection:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Ansible
        run: pip install ansible

      - name: Build and Install Collection
        uses: ./.github/actions/build-install-collection

      - name: Test collection
        run: ansible-playbook tests/test.yml
```

**With Custom Timeout**:

```yaml
jobs:
  large_collection:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5

      - name: Setup Python and Ansible
        uses: ./.github/actions/setup-python-ansible

      - name: Build and Install Large Collection
        uses: ./.github/actions/build-install-collection
        with:
          timeout-minutes: '5'
          max-attempts: '5'
          force-build: 'true'
```

### Example 10: Molecule Test

**In a Custom Workflow**:

```yaml
jobs:
  molecule_test:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: actions/checkout@v5

      - name: Configure AWS
        uses: ./.github/actions/setup-aws-credentials
        with:
          aws-oidc-role: ${{ secrets.AWS_OIDC_ROLE }}

      - name: Setup Python and Ansible
        uses: ./.github/actions/setup-python-ansible

      - name: Build and Install Collection
        uses: ./.github/actions/build-install-collection

      - name: Run Molecule Test
        uses: ./.github/actions/molecule-test
        with:
          scenario-name: 'my_scenario'
          molecule-instance-name: 'test-ubuntu'
          molecule-image-owner: '099720109477'
          molecule-image-arch: 'x86_64'
          molecule-image-name: 'ubuntu/images/hvm-ssd/ubuntu-jammy-22.04*'
          molecule-instance-type: 't2.micro'
          molecule-region: 'us-west-2'
        env:
          MOLECULE_VPC_SUBNET_ID: ${{ secrets.MOLECULE_VPC_SUBNET_ID }}
```

## Complete Integration Examples

### Example 11: Full CI/CD Pipeline

**File**: `.github/workflows/ci-cd.yml`

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  pull_request_target:
    types: [ labeled ]
  release:
    types: [ created ]
  schedule:
    - cron: '0 4 * * *'

jobs:
  # Quality Gates
  ansible_lint:
    if: github.event_name != 'release'
    uses: ./.github/workflow-templates/ansible-lint-reusable.yml

  python_lint:
    if: github.event_name != 'release'
    uses: ./.github/workflow-templates/python-lint-reusable.yml
    with:
      target_directory: 'plugins/'

  ansible_test:
    if: github.event_name != 'release'
    uses: ./.github/workflow-templates/ansible-test-reusable.yml

  # Integration Testing
  integration_test_linux:
    if: |
      github.event_name == 'push' ||
      github.event_name == 'schedule' ||
      (github.event_name == 'pull_request_target' &&
      github.event.label.name == 'ok-to-test')
    needs: [ansible_lint, python_lint, ansible_test]
    uses: ./.github/workflow-templates/molecule-integration-test-reusable.yml
    with:
      test_matrix: |
        {
          "molecule": [
            {
              "distro": "ubuntu-22.04",
              "image_owner": "099720109477",
              "image_arch": "x86_64",
              "image_name": "ubuntu/images/hvm-ssd/ubuntu-jammy-22.04*",
              "instance_type": "t2.micro"
            }
          ],
          "collection_role": ["install", "configure", "uninstall"]
        }
      molecule_scenarios: '["install", "configure", "uninstall"]'
    secrets:
      AWS_OIDC_ROLE: ${{ secrets.AWS_OIDC_ROLE }}
      MOLECULE_VPC_SUBNET_ID: ${{ secrets.MOLECULE_VPC_SUBNET_ID }}
      COLLECTION_API_CLIENT_ID: ${{ secrets.API_CLIENT_ID }}
      COLLECTION_API_CLIENT_SECRET: ${{ secrets.API_CLIENT_SECRET }}

  # Release
  release:
    if: github.event_name == 'release'
    uses: ./.github/workflow-templates/collection-release-reusable.yml
    with:
      collection_namespace: 'mycompany'
      collection_name: 'mycollection'
      publish_to_galaxy: true
      publish_to_github: true
    secrets:
      GALAXY_API_KEY: ${{ secrets.GALAXY_API_KEY }}
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Example 12: Multi-Platform Testing

**File**: `.github/workflows/multi-platform-test.yml`

```yaml
name: Multi-Platform Testing

on:
  schedule:
    - cron: '0 2 * * *'  # Linux tests at 2 AM
  workflow_dispatch:

jobs:
  # Load matrix configurations
  load_matrices:
    runs-on: ubuntu-latest
    outputs:
      linux_matrix: ${{ steps.set-matrices.outputs.linux_matrix }}
      windows_matrix: ${{ steps.set-matrices.outputs.windows_matrix }}
    steps:
      - uses: actions/checkout@v5
      - id: set-matrices
        run: |
          LINUX_MATRIX=$(cat .github/workflow-templates/matrix-configs/linux-test-matrix.json | jq '. + {"collection_role": ["install", "configure"]}')
          WINDOWS_MATRIX=$(cat .github/workflow-templates/matrix-configs/windows-test-matrix.json | jq '. + {"collection_role": ["win_install"]}')
          echo "linux_matrix=$LINUX_MATRIX" >> $GITHUB_OUTPUT
          echo "windows_matrix=$WINDOWS_MATRIX" >> $GITHUB_OUTPUT

  # Linux testing
  test_linux:
    needs: load_matrices
    uses: ./.github/workflow-templates/molecule-integration-test-reusable.yml
    with:
      test_matrix: ${{ needs.load_matrices.outputs.linux_matrix }}
      molecule_scenarios: '["install", "configure"]'
      aws_region: 'us-west-2'
    secrets:
      AWS_OIDC_ROLE: ${{ secrets.AWS_OIDC_ROLE }}
      MOLECULE_VPC_SUBNET_ID: ${{ secrets.MOLECULE_VPC_SUBNET_ID }}

  # Windows testing (staggered schedule)
  test_windows:
    needs: [load_matrices, test_linux]
    uses: ./.github/workflow-templates/molecule-integration-test-reusable.yml
    with:
      test_matrix: ${{ needs.load_matrices.outputs.windows_matrix }}
      molecule_scenarios: '["win_install"]'
      install_pywinrm: true
      test_timeout_minutes: 45
    secrets:
      AWS_OIDC_ROLE: ${{ secrets.AWS_OIDC_ROLE }}
      MOLECULE_VPC_SUBNET_ID: ${{ secrets.MOLECULE_VPC_SUBNET_ID }}
```

## Advanced Patterns

### Example 13: Conditional Testing Based on Changed Files

```yaml
name: Smart CI

on:
  pull_request:
    branches: [ main ]

jobs:
  detect_changes:
    runs-on: ubuntu-latest
    outputs:
      roles_changed: ${{ steps.filter.outputs.roles }}
      plugins_changed: ${{ steps.filter.outputs.plugins }}
    steps:
      - uses: actions/checkout@v5
      - uses: dorny/paths-filter@v2
        id: filter
        with:
          filters: |
            roles:
              - 'roles/**'
              - 'molecule/**'
            plugins:
              - 'plugins/**'

  lint_ansible:
    needs: detect_changes
    if: needs.detect_changes.outputs.roles_changed == 'true'
    uses: ./.github/workflow-templates/ansible-lint-reusable.yml

  lint_python:
    needs: detect_changes
    if: needs.detect_changes.outputs.plugins_changed == 'true'
    uses: ./.github/workflow-templates/python-lint-reusable.yml

  test_integration:
    needs: detect_changes
    if: needs.detect_changes.outputs.roles_changed == 'true'
    uses: ./.github/workflow-templates/molecule-integration-test-reusable.yml
    with:
      test_matrix: |
        {
          "molecule": [
            {
              "distro": "ubuntu-22.04",
              "image_owner": "099720109477",
              "image_arch": "x86_64",
              "image_name": "ubuntu/images/hvm-ssd/ubuntu-jammy-22.04*",
              "instance_type": "t2.micro"
            }
          ],
          "collection_role": ["install"]
        }
      molecule_scenarios: '["install"]'
    secrets:
      AWS_OIDC_ROLE: ${{ secrets.AWS_OIDC_ROLE }}
      MOLECULE_VPC_SUBNET_ID: ${{ secrets.MOLECULE_VPC_SUBNET_ID }}
```

### Example 14: Matrix Exclusions

```yaml
name: Selective Testing

on:
  push:
    branches: [ main ]

jobs:
  test:
    uses: ./.github/workflow-templates/molecule-integration-test-reusable.yml
    with:
      test_matrix: |
        {
          "molecule": [
            {
              "distro": "ubuntu-20.04",
              "image_owner": "099720109477",
              "image_arch": "x86_64",
              "image_name": "ubuntu/images/hvm-ssd/ubuntu-focal-20.04*",
              "instance_type": "t2.micro"
            },
            {
              "distro": "amazon-2023",
              "image_owner": "137112412989",
              "image_arch": "x86_64",
              "image_name": "al2023-ami-2023*",
              "instance_type": "t2.micro"
            }
          ],
          "collection_role": ["install", "configure", "downgrade"],
          "exclude": [
            {
              "molecule": {
                "distro": "amazon-2023"
              },
              "collection_role": "downgrade"
            }
          ]
        }
      molecule_scenarios: '["install", "configure", "downgrade"]'
    secrets:
      AWS_OIDC_ROLE: ${{ secrets.AWS_OIDC_ROLE }}
      MOLECULE_VPC_SUBNET_ID: ${{ secrets.MOLECULE_VPC_SUBNET_ID }}
```

### Example 15: Environment-Specific Deployments

```yaml
name: Environment Deployments

on:
  push:
    branches: [ main, staging, develop ]

jobs:
  determine_environment:
    runs-on: ubuntu-latest
    outputs:
      environment: ${{ steps.set-env.outputs.environment }}
    steps:
      - id: set-env
        run: |
          if [ "${{ github.ref }}" = "refs/heads/main" ]; then
            echo "environment=production" >> $GITHUB_OUTPUT
          elif [ "${{ github.ref }}" = "refs/heads/staging" ]; then
            echo "environment=staging" >> $GITHUB_OUTPUT
          else
            echo "environment=development" >> $GITHUB_OUTPUT
          fi

  test:
    needs: determine_environment
    uses: ./.github/workflow-templates/molecule-integration-test-reusable.yml
    with:
      test_matrix: |
        {
          "molecule": [
            {
              "distro": "ubuntu-22.04",
              "image_owner": "099720109477",
              "image_arch": "x86_64",
              "image_name": "ubuntu/images/hvm-ssd/ubuntu-jammy-22.04*",
              "instance_type": "t2.micro"
            }
          ],
          "collection_role": ["install"]
        }
      molecule_scenarios: '["install"]'
    secrets:
      AWS_OIDC_ROLE: ${{ secrets[format('AWS_OIDC_ROLE_{0}', needs.determine_environment.outputs.environment)] }}
      MOLECULE_VPC_SUBNET_ID: ${{ secrets[format('VPC_SUBNET_{0}', needs.determine_environment.outputs.environment)] }}
```

## Migration Guide

### Migrating from Inline Workflows

**Before** (inline workflow):

```yaml
name: Test

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install ansible
      - run: ansible-lint
```

**After** (reusable workflow):

```yaml
name: Test

on: [push]

jobs:
  test:
    uses: ./.github/workflow-templates/ansible-lint-reusable.yml
```

### Migrating Complex Molecule Workflows

**Before**:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        distro: [ubuntu-20.04, ubuntu-22.04]
    steps:
      - uses: actions/checkout@v5
      - name: Configure AWS
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_OIDC_ROLE }}
          aws-region: us-west-2
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Build collection
        run: |
          ansible-galaxy collection build
          ansible-galaxy collection install *.tar.gz
      - name: Run tests
        run: molecule test
```

**After**:

```yaml
jobs:
  test:
    uses: ./.github/workflow-templates/molecule-integration-test-reusable.yml
    with:
      test_matrix: |
        {
          "molecule": [
            {
              "distro": "ubuntu-20.04",
              "image_owner": "099720109477",
              "image_arch": "x86_64",
              "image_name": "ubuntu/images/hvm-ssd/ubuntu-focal-20.04*",
              "instance_type": "t2.micro"
            },
            {
              "distro": "ubuntu-22.04",
              "image_owner": "099720109477",
              "image_arch": "x86_64",
              "image_name": "ubuntu/images/hvm-ssd/ubuntu-jammy-22.04*",
              "instance_type": "t2.micro"
            }
          ],
          "collection_role": ["my_role"]
        }
      molecule_scenarios: '["my_role"]'
    secrets:
      AWS_OIDC_ROLE: ${{ secrets.AWS_OIDC_ROLE }}
      MOLECULE_VPC_SUBNET_ID: ${{ secrets.MOLECULE_VPC_SUBNET_ID }}
```

## Troubleshooting

### Common Issues

**Issue**: Workflow not found

```
Error: ./.github/workflow-templates/ansible-lint-reusable.yml is not a valid workflow file
```

**Solution**: Ensure the workflow file exists and has correct YAML syntax. Verify the path is correct.

**Issue**: Secret not accessible

```
Error: Secret AWS_OIDC_ROLE is not available
```

**Solution**: Ensure secrets are passed explicitly in the `secrets:` section of the workflow call.

**Issue**: Matrix too large

```
Error: Matrix includes too many combinations
```

**Solution**: Use exclusions or split into multiple workflows. GitHub Actions has a limit of 256 jobs per workflow.

## Best Practices

1. **Start Simple**: Begin with basic workflows and add complexity as needed
2. **Use Matrix Files**: Externalize matrix configurations for easier maintenance
3. **Stagger Schedules**: Avoid running all tests simultaneously to prevent resource contention
4. **Monitor Costs**: Track AWS costs from EC2 instances
5. **Test Locally**: Validate Molecule scenarios locally before adding to CI/CD
6. **Document Changes**: Keep workflow documentation up to date
7. **Version Control**: Commit workflow changes with descriptive messages
8. **Security First**: Always use secrets for sensitive data
9. **Fail Fast**: Use `fail-fast: false` only when you need all results
10. **Clean Up**: Ensure instances are always destroyed to prevent cost overruns

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Reusable Workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
- [Composite Actions](https://docs.github.com/en/actions/creating-actions/creating-a-composite-action)
- [Molecule Documentation](https://molecule.readthedocs.io/)
- [Ansible Documentation](https://docs.ansible.com/)

## Support

For issues or questions:

1. Review this documentation
2. Check workflow logs for error messages
3. Verify secrets and variables are configured correctly
4. Test locally before running in CI/CD
5. Contact repository maintainers for assistance
