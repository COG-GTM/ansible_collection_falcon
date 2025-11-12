# Molecule Scenario Parameterization

This document describes how Molecule scenarios are parameterized using environment variables for reusable CI/CD workflows.

## Overview

Molecule scenarios in this collection are designed to be fully parameterized through environment variables, allowing the same scenario configuration to be used across different platforms, regions, and test configurations without modification.

## Environment Variables

### Required Variables

#### MOLECULE_VPC_SUBNET_ID

**Description**: VPC subnet ID for EC2 instance provisioning.

**Format**: `subnet-xxxxxxxxxxxxxxxxx`

**Usage**: Determines which VPC subnet instances are launched in. Must have:
- Internet gateway access (for package downloads)
- Sufficient IP address space
- Appropriate security group rules

**Example**:
```bash
export MOLECULE_VPC_SUBNET_ID="subnet-0123456789abcdef0"
```

**In Workflows**:
```yaml
env:
  MOLECULE_VPC_SUBNET_ID: ${{ secrets.MOLECULE_VPC_SUBNET_ID }}
```

### Platform Configuration Variables

#### MOLECULE_INSTANCE_NAME

**Description**: Name for the EC2 instance created by Molecule.

**Format**: String (alphanumeric with hyphens)

**Default**: `default-{scenario-name}` (e.g., `default-falcon-install`)

**Usage**: Used to identify instances in AWS console and prevent naming conflicts in parallel test runs.

**Example**:
```bash
export MOLECULE_INSTANCE_NAME="ubuntu-2004-falcon-install"
```

**In Workflows**:
```yaml
env:
  MOLECULE_INSTANCE_NAME: ${{ matrix.molecule.distro }}-${{ matrix.collection_role }}
```

**Best Practice**: Include distribution and scenario name for easy identification.

#### MOLECULE_IMAGE_OWNER

**Description**: AWS account ID that owns the AMI.

**Format**: 12-digit AWS account ID

**Default**: `099720109477` (Canonical/Ubuntu)

**Usage**: Filters AMI search to specific publisher. Ensures you get official images.

**Common Values**:
- `099720109477` - Canonical (Ubuntu)
- `137112412989` - Amazon (Amazon Linux)
- `013907871322` - SUSE
- `679593333241` - AlmaLinux
- `309956199498` - Red Hat (RHEL)
- `801119661308` - Amazon (Windows Server)

**Example**:
```bash
export MOLECULE_IMAGE_OWNER="099720109477"
```

**In Workflows**:
```yaml
env:
  MOLECULE_IMAGE_OWNER: ${{ matrix.molecule.image_owner }}
```

#### MOLECULE_IMAGE_ARCH

**Description**: CPU architecture for the AMI.

**Format**: `x86_64` or `arm64`

**Default**: `x86_64`

**Usage**: Filters AMI search by architecture. Must match instance type architecture.

**Example**:
```bash
export MOLECULE_IMAGE_ARCH="x86_64"
```

**In Workflows**:
```yaml
env:
  MOLECULE_IMAGE_ARCH: ${{ matrix.molecule.image_arch }}
```

**Architecture Compatibility**:
- **x86_64**: t2, t3, t3a, m5, c5, r5, etc.
- **arm64**: t4g, m6g, c6g, r6g, etc.

#### MOLECULE_IMAGE_NAME

**Description**: AMI name pattern with wildcards.

**Format**: String with wildcards (`*`, `?`)

**Default**: `ubuntu/images/hvm-ssd/ubuntu-focal-20.04*`

**Usage**: Filters AMI search by name pattern. Wildcards ensure latest version is selected.

**Examples**:
```bash
# Ubuntu 22.04
export MOLECULE_IMAGE_NAME="ubuntu/images/hvm-ssd/ubuntu-jammy-22.04*"

# Amazon Linux 2023
export MOLECULE_IMAGE_NAME="al2023-ami-2023*"

# RHEL 9
export MOLECULE_IMAGE_NAME="RHEL-9.?.?_HVM-*"

# Windows Server 2022
export MOLECULE_IMAGE_NAME="Windows_Server-2022-English-Full-Base-*"
```

**In Workflows**:
```yaml
env:
  MOLECULE_IMAGE_NAME: '${{ matrix.molecule.image_name }}'
```

**Note**: Quote the value in YAML to preserve wildcards.

#### MOLECULE_INSTANCE_TYPE

**Description**: EC2 instance type.

**Format**: Instance type identifier (e.g., `t2.micro`, `t3a.medium`)

**Default**: `t2.micro`

**Usage**: Determines instance size, CPU, memory, and cost. Must be compatible with architecture.

**Common Values**:
- **Linux (x86_64)**: `t2.micro`, `t2.small`, `t3.micro`
- **Linux (arm64)**: `t4g.micro`, `t4g.small`
- **Windows**: `t3a.medium`, `t3a.large` (requires more resources)

**Example**:
```bash
export MOLECULE_INSTANCE_TYPE="t2.micro"
```

**In Workflows**:
```yaml
env:
  MOLECULE_INSTANCE_TYPE: ${{ matrix.molecule.instance_type }}
```

**Cost Considerations**:
- `t2.micro`: ~$0.0116/hour
- `t3a.medium`: ~$0.0376/hour
- `t4g.micro`: ~$0.0084/hour (ARM, cheaper)

#### MOLECULE_REGION

**Description**: AWS region for instance provisioning.

**Format**: AWS region identifier (e.g., `us-west-2`, `eu-west-1`)

**Default**: `us-west-2`

**Usage**: Determines which AWS region instances are launched in. Must match VPC subnet region.

**Example**:
```bash
export MOLECULE_REGION="us-west-2"
```

**In Workflows**:
```yaml
env:
  MOLECULE_REGION: ${{ env.AWS_REGION }}
```

**Common Regions**:
- `us-east-1` - US East (N. Virginia)
- `us-west-2` - US West (Oregon)
- `eu-west-1` - Europe (Ireland)
- `ap-southeast-1` - Asia Pacific (Singapore)

### Optional Variables

#### MOLECULE_SECURITY_GROUP_RESTRICT_CIDR_IP

**Description**: Restrict security group ingress to specific CIDR.

**Format**: Boolean string (`"true"` or `"false"`)

**Default**: `"true"`

**Usage**: When true, restricts SSH/WinRM access to GitHub Actions runner IP.

**Example**:
```bash
export MOLECULE_SECURITY_GROUP_RESTRICT_CIDR_IP="true"
```

**Security Note**: Always use `"true"` in production to prevent unauthorized access.

#### MOLECULE_BOOT_WAIT_SECONDS

**Description**: Seconds to wait after instance boot before connecting.

**Format**: Integer

**Default**: `10`

**Usage**: Allows instance to fully initialize before Ansible connection attempts.

**Example**:
```bash
export MOLECULE_BOOT_WAIT_SECONDS="30"
```

**Adjustment Guidelines**:
- **Linux**: 10-20 seconds usually sufficient
- **Windows**: 60-120 seconds recommended (slower boot)
- **Large instances**: May need longer wait times

## Molecule Configuration File

The `molecule.yml` file uses environment variables with defaults:

```yaml
---
dependency:
  name: galaxy
driver:
  name: ec2
platforms:
  - name: "${MOLECULE_INSTANCE_NAME:-default-falcon-install}"
    image_owner: "${MOLECULE_IMAGE_OWNER:-099720109477}"
    image_filters:
      - architecture: "${MOLECULE_IMAGE_ARCH:-x86_64}"
      - name: "${MOLECULE_IMAGE_NAME:-ubuntu/images/hvm-ssd/ubuntu-focal-20.04*}"
    instance_type: "${MOLECULE_INSTANCE_TYPE:-t2.micro}"
    region: "${MOLECULE_REGION:-us-west-2}"
    vpc_subnet_id: "${MOLECULE_VPC_SUBNET_ID}"
    security_group_restrict_cidr_ip: "${MOLECULE_SECURITY_GROUP_RESTRICT_CIDR_IP:-true}"
    boot_wait_seconds: ${MOLECULE_BOOT_WAIT_SECONDS:-10}
provisioner:
  name: ansible
  config_options:
    ssh_connection:
      pipelining: true
    defaults:
      callbacks_enabled: ansible.posix.profile_tasks
  playbooks:
    create: ../shared/playbooks/create.yml
    destroy: ../shared/playbooks/destroy.yml
    verify: ../shared/playbooks/verify.yml
verifier:
  name: ansible
scenario:
  test_sequence:
    - dependency
    - syntax
    - create
    - prepare
    - converge
    - idempotence
    - side_effect
    - verify
    - destroy
```

## Variable Substitution Pattern

The pattern `${VARIABLE_NAME:-default_value}` provides:

1. **Environment Variable**: Uses `$VARIABLE_NAME` if set
2. **Default Value**: Falls back to `default_value` if not set
3. **Local Testing**: Allows running Molecule locally without setting all variables
4. **CI/CD Flexibility**: Workflows can override any value

## Collection-Specific Variables

In addition to Molecule platform variables, collection-specific variables are used:

### COLLECTION_API_CLIENT_ID

**Description**: API client ID for collection operations (e.g., CrowdStrike Falcon API).

**Usage**: Passed to Ansible playbooks for API authentication.

**Example**:
```yaml
env:
  COLLECTION_API_CLIENT_ID: ${{ secrets.FALCON_CLIENT_ID }}
```

### COLLECTION_API_CLIENT_SECRET

**Description**: API client secret for collection operations.

**Usage**: Passed to Ansible playbooks for API authentication.

**Example**:
```yaml
env:
  COLLECTION_API_CLIENT_SECRET: ${{ secrets.FALCON_CLIENT_SECRET }}
```

### COLLECTION_CID

**Description**: Customer/Client ID for collection operations.

**Usage**: Passed to Ansible playbooks for service configuration.

**Example**:
```yaml
env:
  COLLECTION_CID: ${{ secrets.FALCON_CID }}
```

### COLLECTION_PROV_TOKEN

**Description**: Provisioning token for collection operations.

**Usage**: Passed to Ansible playbooks for secure provisioning.

**Example**:
```yaml
env:
  COLLECTION_PROV_TOKEN: ${{ secrets.FALCON_PROV_TOKEN }}
```

## Creating New Scenarios

To create a new parameterized Molecule scenario:

1. **Copy an existing scenario directory**:
   ```bash
   cp -r molecule/falcon_install molecule/my_new_scenario
   ```

2. **Update the scenario name** in `molecule.yml`:
   ```yaml
   platforms:
     - name: "${MOLECULE_INSTANCE_NAME:-default-my-new-scenario}"
   ```

3. **Customize playbooks** in the scenario directory:
   - `converge.yml` - Main test playbook
   - `prepare.yml` - Pre-test setup (optional)
   - `verify.yml` - Post-test verification (or use shared)

4. **Add to workflow matrix**:
   ```yaml
   collection_role:
     - falcon_install
     - my_new_scenario
   ```

## Testing Scenarios Locally

### Prerequisites

1. AWS credentials configured
2. Python 3.11+ with dependencies installed
3. Molecule and molecule-plugins[ec2] installed

### Running a Scenario

```bash
# Set required variables
export MOLECULE_VPC_SUBNET_ID="subnet-0123456789abcdef0"
export MOLECULE_INSTANCE_NAME="local-test-ubuntu"
export MOLECULE_IMAGE_OWNER="099720109477"
export MOLECULE_IMAGE_ARCH="x86_64"
export MOLECULE_IMAGE_NAME="ubuntu/images/hvm-ssd/ubuntu-jammy-22.04*"
export MOLECULE_INSTANCE_TYPE="t2.micro"
export MOLECULE_REGION="us-west-2"

# Set collection-specific variables
export COLLECTION_API_CLIENT_ID="your-client-id"
export COLLECTION_API_CLIENT_SECRET="your-client-secret"

# Run the scenario
cd molecule/falcon_install
molecule test
```

### Testing Without Destroy

To keep the instance running for debugging:

```bash
molecule test --destroy never
```

Then manually destroy when done:

```bash
molecule destroy
```

## Troubleshooting

### Variable Not Substituted

**Symptom**: Molecule uses default value instead of environment variable.

**Cause**: Variable not exported or not set before Molecule runs.

**Solution**:
```bash
# Ensure variable is exported
export MOLECULE_INSTANCE_NAME="my-instance"

# Verify it's set
echo $MOLECULE_INSTANCE_NAME

# Run Molecule
molecule test
```

### AMI Not Found

**Symptom**: Molecule fails with "No AMI found matching criteria".

**Cause**: Image owner, architecture, or name pattern doesn't match any AMIs.

**Solution**:
```bash
# Search for AMIs
aws ec2 describe-images \
  --owners $MOLECULE_IMAGE_OWNER \
  --filters "Name=name,Values=$MOLECULE_IMAGE_NAME" \
            "Name=architecture,Values=$MOLECULE_IMAGE_ARCH" \
  --query 'Images[*].[Name,ImageId]' \
  --output table

# Adjust variables based on results
```

### Instance Type Not Available

**Symptom**: Molecule fails with "Instance type not available".

**Cause**: Instance type not supported in region or for architecture.

**Solution**:
```bash
# Check instance type availability
aws ec2 describe-instance-type-offerings \
  --location-type availability-zone \
  --filters Name=instance-type,Values=$MOLECULE_INSTANCE_TYPE \
  --region $MOLECULE_REGION

# Use alternative instance type if needed
```

### Subnet Not Found

**Symptom**: Molecule fails with "Subnet not found".

**Cause**: VPC subnet ID incorrect or not in the specified region.

**Solution**:
```bash
# Verify subnet exists
aws ec2 describe-subnets \
  --subnet-ids $MOLECULE_VPC_SUBNET_ID \
  --region $MOLECULE_REGION

# Ensure region matches subnet region
```

## Best Practices

1. **Always use environment variables**: Never hardcode values in `molecule.yml`.

2. **Provide sensible defaults**: Use defaults that work for local development.

3. **Document required variables**: Clearly indicate which variables must be set.

4. **Use descriptive instance names**: Include distribution and scenario for easy identification.

5. **Test locally before CI/CD**: Verify scenarios work locally before adding to workflows.

6. **Clean up instances**: Always run `molecule destroy` after testing.

7. **Use security group restrictions**: Always set `MOLECULE_SECURITY_GROUP_RESTRICT_CIDR_IP="true"`.

8. **Monitor costs**: Be aware of instance costs, especially for Windows and larger instances.

9. **Version control scenarios**: Commit scenario changes with descriptive messages.

10. **Share common playbooks**: Use shared playbooks (create, destroy, verify) across scenarios.

## Integration with Workflows

The reusable workflow template `molecule-integration-test-reusable.yml` automatically sets all required environment variables from the matrix configuration:

```yaml
- name: Run role tests
  uses: nick-fields/retry@v3
  env:
    MOLECULE_INSTANCE_NAME: ${{ matrix.molecule.distro }}-${{ matrix.collection_role }}
    MOLECULE_IMAGE_OWNER: ${{ matrix.molecule.image_owner }}
    MOLECULE_IMAGE_ARCH: ${{ matrix.molecule.image_arch }}
    MOLECULE_IMAGE_NAME: '${{ matrix.molecule.image_name }}'
    MOLECULE_INSTANCE_TYPE: ${{ matrix.molecule.instance_type }}
    MOLECULE_REGION: ${{ env.AWS_REGION }}
  with:
    command: molecule test -s ${{ matrix.collection_role }}
```

This ensures consistent parameterization across all test runs.
