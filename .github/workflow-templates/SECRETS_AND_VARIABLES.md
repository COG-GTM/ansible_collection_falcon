# Required Secrets and Variables

This document describes all secrets and variables required for the reusable CI/CD workflow templates.

## Overview

The reusable workflow templates require various secrets and variables to be configured in your GitHub repository or organization settings. These are used for:

- AWS authentication and resource provisioning
- Collection-specific API authentication
- Release and publication operations
- Test infrastructure configuration

## Secret Management

### Where to Configure Secrets

Secrets can be configured at three levels:

1. **Repository Secrets**: Settings → Secrets and variables → Actions → Repository secrets
2. **Organization Secrets**: Organization settings → Secrets and variables → Actions → Organization secrets
3. **Environment Secrets**: Settings → Environments → [Environment name] → Secrets

**Recommendation**: Use organization secrets for shared infrastructure (AWS, VPC) and repository secrets for collection-specific credentials.

## Required Secrets

### AWS Infrastructure Secrets

#### AWS_OIDC_ROLE

**Description**: AWS IAM role ARN for OIDC authentication from GitHub Actions.

**Format**: `arn:aws:iam::ACCOUNT_ID:role/ROLE_NAME`

**Required For**:
- All integration testing workflows
- Molecule-based testing

**Usage**:
```yaml
secrets:
  AWS_OIDC_ROLE:
    required: true
```

**Setup Instructions**:

1. Create an IAM role in AWS with trust policy for GitHub OIDC:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
         },
         "Action": "sts:AssumeRoleWithWebIdentity",
         "Condition": {
           "StringEquals": {
             "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
           },
           "StringLike": {
             "token.actions.githubusercontent.com:sub": "repo:OWNER/REPO:*"
           }
         }
       }
     ]
   }
   ```

2. Attach policies for EC2 operations:
   - `AmazonEC2FullAccess` (or custom policy with EC2 permissions)
   - Custom policy for VPC operations if needed

3. Add the role ARN to GitHub secrets as `AWS_OIDC_ROLE`

**Required Permissions**:
- `ec2:RunInstances`
- `ec2:TerminateInstances`
- `ec2:DescribeInstances`
- `ec2:DescribeImages`
- `ec2:DescribeSecurityGroups`
- `ec2:CreateSecurityGroup`
- `ec2:DeleteSecurityGroup`
- `ec2:AuthorizeSecurityGroupIngress`
- `ec2:RevokeSecurityGroupIngress`
- `ec2:CreateTags`
- `ec2:DescribeSubnets`
- `ec2:DescribeVpcs`

**Security Notes**:
- Use least-privilege IAM policies
- Restrict role assumption to specific repositories
- Enable CloudTrail logging for audit
- Regularly rotate credentials

#### MOLECULE_VPC_SUBNET_ID

**Description**: VPC subnet ID where EC2 test instances will be launched.

**Format**: `subnet-xxxxxxxxxxxxxxxxx` (17 characters after `subnet-`)

**Required For**:
- All integration testing workflows
- Molecule-based testing

**Usage**:
```yaml
secrets:
  MOLECULE_VPC_SUBNET_ID:
    required: true
```

**Setup Instructions**:

1. Create or identify a VPC subnet with:
   - Internet gateway attached (for package downloads)
   - Sufficient IP address space (recommend /24 or larger)
   - Appropriate route tables
   - DNS resolution enabled

2. Note the subnet ID from AWS console or CLI:
   ```bash
   aws ec2 describe-subnets --filters "Name=tag:Name,Values=YOUR_SUBNET_NAME"
   ```

3. Add the subnet ID to GitHub secrets as `MOLECULE_VPC_SUBNET_ID`

**Requirements**:
- Must have internet access (via Internet Gateway or NAT Gateway)
- Must have available IP addresses
- Must be in the same region as specified in workflows (default: us-west-2)
- Security groups must allow SSH (22) and WinRM (5985, 5986) from GitHub Actions runners

**Cost Considerations**:
- No cost for the subnet itself
- Costs apply for EC2 instances launched in the subnet
- Data transfer costs may apply

### Collection-Specific Secrets

These secrets are specific to the collection being tested. For the CrowdStrike Falcon collection, these are Falcon API credentials. For other collections, substitute with appropriate credentials.

#### COLLECTION_API_CLIENT_ID

**Description**: API client ID for collection-specific operations.

**Format**: Varies by collection (typically alphanumeric string)

**Required For**:
- Integration testing workflows that interact with external APIs
- Molecule scenarios that require API authentication

**Usage**:
```yaml
secrets:
  COLLECTION_API_CLIENT_ID:
    required: false  # Optional for workflows that don't need API access
```

**Setup Instructions**:

1. Generate API credentials from your service provider
2. Add the client ID to GitHub secrets as `COLLECTION_API_CLIENT_ID`
3. Ensure the client has appropriate permissions for testing

**Example (CrowdStrike Falcon)**:
- Navigate to Falcon console → Support → API Clients and Keys
- Create a new API client with required scopes
- Copy the client ID

**Security Notes**:
- Use dedicated test credentials, not production
- Limit API client permissions to minimum required
- Rotate credentials regularly
- Monitor API usage for anomalies

#### COLLECTION_API_CLIENT_SECRET

**Description**: API client secret for collection-specific operations.

**Format**: Varies by collection (typically alphanumeric string)

**Required For**:
- Integration testing workflows that interact with external APIs
- Molecule scenarios that require API authentication

**Usage**:
```yaml
secrets:
  COLLECTION_API_CLIENT_SECRET:
    required: false  # Optional for workflows that don't need API access
```

**Setup Instructions**:

1. Generate API credentials from your service provider
2. Add the client secret to GitHub secrets as `COLLECTION_API_CLIENT_SECRET`
3. Store securely and never commit to version control

**Security Notes**:
- Treat as highly sensitive
- Never log or expose in workflow output
- Use GitHub's secret masking (automatic)
- Rotate immediately if compromised

#### COLLECTION_CID

**Description**: Customer/Client ID for collection-specific operations.

**Format**: Varies by collection

**Required For**:
- Integration testing workflows that require customer/tenant identification
- Molecule scenarios that configure services

**Usage**:
```yaml
secrets:
  COLLECTION_CID:
    required: false  # Optional for workflows that don't need CID
```

**Example (CrowdStrike Falcon)**:
- 32-character hex string with optional 2-character checksum
- Format: `XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX-XX`

#### COLLECTION_PROV_TOKEN

**Description**: Provisioning token for collection-specific operations.

**Format**: Varies by collection

**Required For**:
- Integration testing workflows that require secure provisioning
- Molecule scenarios that test provisioning workflows

**Usage**:
```yaml
secrets:
  COLLECTION_PROV_TOKEN:
    required: false  # Optional for workflows that don't need provisioning
```

**Security Notes**:
- Use test-specific provisioning tokens
- Limit token scope and validity period
- Rotate regularly

### Release and Publication Secrets

#### GALAXY_API_KEY

**Description**: Ansible Galaxy API key for publishing collections.

**Format**: Alphanumeric string

**Required For**:
- Release workflows
- Collection publication to Ansible Galaxy

**Usage**:
```yaml
secrets:
  GALAXY_API_KEY:
    required: false  # Only required if publishing to Galaxy
```

**Setup Instructions**:

1. Log in to https://galaxy.ansible.com
2. Navigate to Preferences → API Key
3. Generate or copy your API key
4. Add to GitHub secrets as `GALAXY_API_KEY`

**Security Notes**:
- Allows publishing collections under your account
- Protect carefully to prevent unauthorized publications
- Rotate if compromised

#### AUTOMATION_HUB_TOKEN

**Description**: Red Hat Automation Hub token for publishing collections.

**Format**: JWT token string

**Required For**:
- Release workflows publishing to Red Hat Automation Hub
- Enterprise collection distribution

**Usage**:
```yaml
secrets:
  AUTOMATION_HUB_TOKEN:
    required: false  # Only required if publishing to Automation Hub
```

**Setup Instructions**:

1. Log in to https://console.redhat.com
2. Navigate to Automation Hub → API token
3. Generate or copy your token
4. Add to GitHub secrets as `AUTOMATION_HUB_TOKEN`

**Requirements**:
- Red Hat partner account
- Approved namespace in Automation Hub
- Appropriate permissions for collection publication

#### GITHUB_TOKEN

**Description**: GitHub token for release operations.

**Format**: GitHub personal access token or automatic token

**Required For**:
- Release workflows
- Uploading artifacts to GitHub releases

**Usage**:
```yaml
secrets:
  GITHUB_TOKEN:
    required: false  # Often provided automatically by GitHub Actions
```

**Setup Instructions**:

GitHub Actions automatically provides a `GITHUB_TOKEN` with appropriate permissions. If you need custom permissions:

1. Generate a personal access token (Settings → Developer settings → Personal access tokens)
2. Grant `repo` scope
3. Add to GitHub secrets as `GITHUB_TOKEN`

**Note**: The automatic `GITHUB_TOKEN` is usually sufficient for release operations.

## Optional Variables

### Workflow Configuration Variables

These can be configured as repository variables (Settings → Secrets and variables → Actions → Variables) or passed as workflow inputs.

#### AWS_REGION

**Description**: AWS region for EC2 instance provisioning.

**Format**: AWS region identifier (e.g., `us-west-2`)

**Default**: `us-west-2`

**Usage**: Can be set as repository variable or workflow input.

**Common Values**:
- `us-east-1` - US East (N. Virginia)
- `us-west-2` - US West (Oregon)
- `eu-west-1` - Europe (Ireland)
- `ap-southeast-1` - Asia Pacific (Singapore)

**Note**: Must match the region of `MOLECULE_VPC_SUBNET_ID`.

## Security Best Practices

### Secret Rotation

1. **Regular Rotation**: Rotate all secrets every 90 days minimum
2. **Compromise Response**: Rotate immediately if compromise suspected
3. **Audit Logs**: Review secret usage in workflow logs regularly
4. **Access Control**: Limit who can view/modify secrets

### Secret Scope

1. **Least Privilege**: Grant minimum required permissions
2. **Environment Separation**: Use different secrets for dev/staging/prod
3. **Test Credentials**: Never use production credentials in CI/CD
4. **Time Limits**: Use time-limited tokens when possible

### Secret Protection

1. **Never Commit**: Never commit secrets to version control
2. **Mask in Logs**: GitHub automatically masks secrets in logs
3. **Secure Storage**: Use GitHub's encrypted secret storage
4. **Access Audit**: Regularly audit who has access to secrets

### Monitoring

1. **Usage Tracking**: Monitor secret usage patterns
2. **Anomaly Detection**: Alert on unusual usage
3. **Failed Attempts**: Monitor failed authentication attempts
4. **Cost Monitoring**: Track AWS costs from test infrastructure

## Troubleshooting

### Secret Not Found

**Symptom**: Workflow fails with "secret not found" or empty value.

**Solutions**:
1. Verify secret name matches exactly (case-sensitive)
2. Check secret is configured at correct level (repo/org/environment)
3. Verify workflow has access to the secret
4. Check environment protection rules if using environment secrets

### Authentication Failed

**Symptom**: Workflow fails with authentication error.

**Solutions**:
1. Verify secret value is correct (no extra spaces/newlines)
2. Check credentials haven't expired
3. Verify API client has required permissions
4. Test credentials outside workflow to confirm validity

### AWS OIDC Authentication Failed

**Symptom**: "Unable to assume role" or OIDC authentication error.

**Solutions**:
1. Verify IAM role ARN is correct
2. Check trust policy allows GitHub OIDC provider
3. Verify repository name in trust policy condition
4. Ensure role has required EC2 permissions
5. Check AWS account isn't experiencing service issues

### Subnet Not Accessible

**Symptom**: "Subnet not found" or "No available IP addresses".

**Solutions**:
1. Verify subnet ID is correct
2. Check subnet is in the correct region
3. Ensure subnet has available IP addresses
4. Verify VPC has internet gateway attached
5. Check security groups allow required ports

## Secret Configuration Checklist

Use this checklist when setting up a new repository:

- [ ] `AWS_OIDC_ROLE` configured with correct IAM role ARN
- [ ] `MOLECULE_VPC_SUBNET_ID` configured with valid subnet ID
- [ ] IAM role has required EC2 permissions
- [ ] VPC subnet has internet access
- [ ] Security groups allow SSH (22) and WinRM (5985, 5986)
- [ ] Collection-specific API credentials configured (if needed)
- [ ] `GALAXY_API_KEY` configured (if publishing to Galaxy)
- [ ] `AUTOMATION_HUB_TOKEN` configured (if publishing to Automation Hub)
- [ ] All secrets tested in a workflow run
- [ ] Secret rotation schedule established
- [ ] Access audit process established

## Example Secret Configuration

### Minimal Configuration (Testing Only)

Required for basic integration testing:

```
AWS_OIDC_ROLE=arn:aws:iam::123456789012:role/github-actions-role
MOLECULE_VPC_SUBNET_ID=subnet-0123456789abcdef0
```

### Full Configuration (Testing + Release)

Required for complete CI/CD pipeline:

```
# AWS Infrastructure
AWS_OIDC_ROLE=arn:aws:iam::123456789012:role/github-actions-role
MOLECULE_VPC_SUBNET_ID=subnet-0123456789abcdef0

# Collection API (example: CrowdStrike Falcon)
COLLECTION_API_CLIENT_ID=abc123def456
COLLECTION_API_CLIENT_SECRET=xyz789uvw012
COLLECTION_CID=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX-XX
COLLECTION_PROV_TOKEN=ABCD1234

# Release & Publication
GALAXY_API_KEY=galaxy_api_key_here
AUTOMATION_HUB_TOKEN=automation_hub_token_here
GITHUB_TOKEN=ghp_xxxxxxxxxxxx (usually automatic)
```

## Support

For issues with secret configuration:

1. Review this documentation
2. Check GitHub Actions logs for specific error messages
3. Verify secrets in repository settings
4. Test credentials manually outside workflows
5. Contact repository maintainers for assistance
