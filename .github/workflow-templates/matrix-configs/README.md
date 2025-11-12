# Matrix Configuration Files

This directory contains JSON configuration files for test matrix definitions used in CI/CD workflows.

## Overview

Matrix configuration files allow you to externalize and dynamically load test matrices in GitHub Actions workflows. This approach provides:

- **Centralized Configuration**: Single source of truth for test platforms
- **Easy Maintenance**: Update test matrices without modifying workflow files
- **Reusability**: Share matrix configurations across multiple workflows
- **Version Control**: Track changes to test matrices over time
- **Dynamic Loading**: Load matrices conditionally based on workflow inputs

## Available Matrix Configurations

### linux-test-matrix.json

Defines the test matrix for Linux-based integration tests.

**Platforms Included**:
- Ubuntu 20.04 (x86_64)
- Ubuntu 22.04 (x86_64)
- Amazon Linux 2023 (x86_64)
- Amazon Linux 2 (x86_64)
- SLES 15 SP5 (x86_64)
- AlmaLinux 8 (x86_64)
- RHEL 9 (x86_64)
- RHEL 9 (arm64)

**Instance Types**:
- `t2.micro` for x86_64 instances
- `t4g.micro` for arm64 instances

**Usage**:
```yaml
strategy:
  fail-fast: false
  matrix: ${{ fromJson(inputs.test_matrix) }}
```

### windows-test-matrix.json

Defines the test matrix for Windows-based integration tests.

**Platforms Included**:
- Windows Server 2022 (x86_64)

**Instance Types**:
- `t3a.medium` (larger instance required for Windows)

**Usage**:
```yaml
strategy:
  fail-fast: false
  matrix: ${{ fromJson(inputs.test_matrix) }}
```

## Matrix Structure

Each matrix configuration file contains a JSON object with a `molecule` array. Each element in the array defines a test platform with the following properties:

```json
{
  "molecule": [
    {
      "distro": "ubuntu-20.04",           // Human-readable distribution name
      "image_owner": "099720109477",      // AWS AMI owner ID
      "image_arch": "x86_64",             // Architecture (x86_64 or arm64)
      "image_name": "ubuntu/images/...",  // AMI name pattern
      "instance_type": "t2.micro"         // EC2 instance type
    }
  ]
}
```

### Property Descriptions

- **`distro`**: Human-readable name for the distribution. Used in job names and instance naming.
- **`image_owner`**: AWS account ID that owns the AMI. Used to filter AMIs in EC2.
- **`image_arch`**: CPU architecture (`x86_64` or `arm64`). Determines compatible instance types.
- **`image_name`**: AMI name pattern with wildcards. Used to find the latest matching AMI.
- **`instance_type`**: EC2 instance type. Must be compatible with the architecture.

## AWS AMI Owner IDs

Common AMI owner IDs for reference:

| Owner ID       | Description                    |
|----------------|--------------------------------|
| 099720109477   | Canonical (Ubuntu)             |
| 137112412989   | Amazon (Amazon Linux)          |
| 013907871322   | SUSE                           |
| 679593333241   | AlmaLinux                      |
| 309956199498   | Red Hat (RHEL)                 |
| 801119661308   | Amazon (Windows Server)        |

## Instance Type Selection

### Linux Testing

**t2.micro** (1 vCPU, 1 GB RAM):
- Suitable for most Linux distributions
- Cost-effective for CI/CD testing
- Sufficient for Ansible playbook execution

**t4g.micro** (2 vCPU, 1 GB RAM):
- ARM64 architecture (Graviton2)
- Required for arm64 testing
- Similar cost to t2.micro

### Windows Testing

**t3a.medium** (2 vCPU, 4 GB RAM):
- Required for Windows Server
- Windows has higher memory requirements
- Faster execution than smaller instances

## Customizing Matrix Configurations

### Adding a New Distribution

1. Find the AWS AMI owner ID and name pattern
2. Determine the appropriate instance type
3. Add a new entry to the matrix:

```json
{
  "distro": "debian-12",
  "image_owner": "136693071363",
  "image_arch": "x86_64",
  "image_name": "debian-12-amd64-*",
  "instance_type": "t2.micro"
}
```

### Removing a Distribution

Simply remove the corresponding entry from the matrix array.

### Changing Instance Types

Update the `instance_type` property. Ensure the instance type is compatible with the architecture:

- **x86_64**: t2, t3, t3a, m5, c5, etc.
- **arm64**: t4g, m6g, c6g, etc.

### Creating Custom Matrices

Create a new JSON file with your custom matrix configuration:

```json
{
  "molecule": [
    {
      "distro": "custom-distro",
      "image_owner": "123456789012",
      "image_arch": "x86_64",
      "image_name": "custom-image-*",
      "instance_type": "t2.small"
    }
  ]
}
```

## Using Matrix Configurations in Workflows

### Method 1: Direct File Reference

Load the matrix configuration file directly in your workflow:

```yaml
jobs:
  load-matrix:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.set-matrix.outputs.matrix }}
    steps:
      - uses: actions/checkout@v5
      - id: set-matrix
        run: |
          MATRIX=$(cat .github/workflow-templates/matrix-configs/linux-test-matrix.json)
          echo "matrix=$MATRIX" >> $GITHUB_OUTPUT

  test:
    needs: load-matrix
    strategy:
      matrix: ${{ fromJson(needs.load-matrix.outputs.matrix) }}
    steps:
      - run: echo "Testing ${{ matrix.molecule.distro }}"
```

### Method 2: Workflow Input

Pass the matrix as a workflow input (for reusable workflows):

```yaml
on:
  workflow_call:
    inputs:
      test_matrix:
        required: true
        type: string

jobs:
  test:
    strategy:
      matrix: ${{ fromJson(inputs.test_matrix) }}
    steps:
      - run: echo "Testing ${{ matrix.molecule.distro }}"
```

Then call the workflow with the matrix:

```yaml
jobs:
  test:
    uses: ./.github/workflow-templates/molecule-integration-test-reusable.yml
    with:
      test_matrix: ${{ toJson(fromJson(readFile('.github/workflow-templates/matrix-configs/linux-test-matrix.json'))) }}
```

### Method 3: Inline Matrix with Exclusions

Combine matrix files with exclusions for fine-grained control:

```yaml
strategy:
  fail-fast: false
  matrix: ${{ fromJson(inputs.test_matrix) }}
  exclude:
    - molecule:
        distro: amazon-2023
      collection_role: specific_role
```

## Matrix Expansion

When you combine the `molecule` matrix with a `collection_role` array, GitHub Actions creates a Cartesian product:

```yaml
strategy:
  matrix:
    molecule: [ubuntu-20.04, ubuntu-22.04]
    collection_role: [role1, role2]
```

This creates 4 jobs:
- ubuntu-20.04 × role1
- ubuntu-20.04 × role2
- ubuntu-22.04 × role1
- ubuntu-22.04 × role2

## Best Practices

1. **Keep matrices focused**: Separate Linux and Windows matrices for clarity.

2. **Use wildcards in AMI names**: This ensures you always get the latest AMI version.

3. **Document custom matrices**: Add comments or README sections for custom configurations.

4. **Test matrix changes**: Validate JSON syntax and test with a single platform before full rollout.

5. **Consider costs**: More platforms = more EC2 usage. Balance coverage with cost.

6. **Use exclusions sparingly**: Prefer separate matrix files over complex exclusion rules.

7. **Version control**: Commit matrix changes with descriptive messages.

8. **Monitor AMI availability**: Periodically verify that AMI patterns still match available images.

## Troubleshooting

### No AMI Found

**Symptom**: Workflow fails with "No AMI found matching criteria"

**Solutions**:
- Verify the `image_owner` ID is correct
- Check that the `image_name` pattern matches available AMIs
- Ensure the `image_arch` matches the AMI architecture
- Use AWS CLI to search for AMIs: `aws ec2 describe-images --owners <owner_id> --filters "Name=name,Values=<pattern>"`

### Instance Type Not Available

**Symptom**: Workflow fails with "Instance type not available in region"

**Solutions**:
- Verify the instance type supports the architecture
- Check instance type availability in your AWS region
- Use an alternative instance type from the same family

### Matrix Too Large

**Symptom**: Workflow creates too many jobs, hitting GitHub Actions limits

**Solutions**:
- Split the matrix into multiple workflows
- Use exclusions to reduce job count
- Run tests on a subset of platforms for PRs, full matrix for releases

## Examples

### Example 1: Minimal Linux Matrix

```json
{
  "molecule": [
    {
      "distro": "ubuntu-22.04",
      "image_owner": "099720109477",
      "image_arch": "x86_64",
      "image_name": "ubuntu/images/hvm-ssd/ubuntu-jammy-22.04*",
      "instance_type": "t2.micro"
    }
  ]
}
```

### Example 2: Multi-Architecture Matrix

```json
{
  "molecule": [
    {
      "distro": "rhel-9-x86",
      "image_owner": "309956199498",
      "image_arch": "x86_64",
      "image_name": "RHEL-9.?.?_HVM-*",
      "instance_type": "t2.micro"
    },
    {
      "distro": "rhel-9-arm",
      "image_owner": "309956199498",
      "image_arch": "arm64",
      "image_name": "RHEL-9.?.?_HVM-*",
      "instance_type": "t4g.micro"
    }
  ]
}
```

### Example 3: Custom Application Matrix

```json
{
  "molecule": [
    {
      "distro": "app-server-1",
      "image_owner": "123456789012",
      "image_arch": "x86_64",
      "image_name": "my-app-base-*",
      "instance_type": "t3.small"
    }
  ]
}
```
