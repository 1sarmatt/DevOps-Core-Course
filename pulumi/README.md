# Pulumi AWS Infrastructure - Lab 4

This project deploys the same AWS infrastructure as the Terraform version using Pulumi with Python.

## Prerequisites

- Pulumi CLI installed
- Python 3.7+
- AWS credentials (temporary credentials with session token)

## Setup

1. Install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Configure AWS credentials:
```bash
source setup-aws.sh
```

Or set environment variables manually:
```bash
export AWS_REGION="us-east-1"
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_SESSION_TOKEN="your-session-token"
```

3. Login to Pulumi (local backend):
```bash
pulumi login --local
```

Or use Pulumi Cloud:
```bash
pulumi login
```

## Deployment

1. Preview changes:
```bash
pulumi preview
```

2. Deploy infrastructure:
```bash
pulumi up
```

3. View outputs:
```bash
pulumi stack output
```

## Infrastructure

The following resources are created:

- VPC (10.0.0.0/16)
- Internet Gateway
- Subnet (10.0.1.0/24)
- Route Table
- Security Group (SSH, HTTP, App port 5000)
- Key Pair
- EC2 Instance (Ubuntu 22.04, t2.micro)

## Testing

After deployment, connect via SSH:
```bash
ssh -i ../terraform/labsuser.pem ubuntu@$(pulumi stack output vm_public_ip)
```

## Cleanup

To destroy all resources:
```bash
pulumi destroy
```

## Comparison with Terraform

### Similarities:
- Same infrastructure resources
- Same AWS provider
- Declarative approach

### Differences:
- **Language**: Python vs HCL
- **State**: Pulumi Cloud/local vs terraform.tfstate file
- **Syntax**: More programmatic (Python) vs configuration (HCL)
- **Outputs**: `pulumi stack output` vs `terraform output`

## Configuration

You can customize the deployment by setting config values:

```bash
pulumi config set vm_name "my-custom-vm"
pulumi config set ssh_public_key_path "/path/to/key.pub"
```
