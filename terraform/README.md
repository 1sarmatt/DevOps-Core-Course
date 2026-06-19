# Terraform Configuration for Yandex Cloud

This directory contains Terraform configuration for creating a VM in Yandex Cloud for Lab 4.

## Prerequisites

- Terraform installed (`brew install hashicorp/tap/terraform`)
- Yandex Cloud account
- Service account with `editor` role
- Authorized key file (`key.json`)
- SSH key pair

## Setup

### 1. Get Your Cloud and Folder IDs

```bash
# Using Yandex Cloud CLI
yc config list

# Or from web console:
# https://console.cloud.yandex.ru/
# Cloud ID: top right corner
# Folder ID: in folder settings
```

### 2. Create terraform.tfvars

```bash
# Copy example file
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
nano terraform.tfvars
```

Add your IDs:
```hcl
cloud_id  = "b1g..."  # Your cloud ID
folder_id = "b1g..."  # Your folder ID
```

### 3. Ensure SSH Key Exists

```bash
# Check if you have SSH key
ls ~/.ssh/id_rsa.pub

# If not, create one
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
# Press Enter for all prompts (default location, no passphrase)
```

## Usage

### Initialize Terraform

```bash
terraform init
```

### Preview Changes

```bash
terraform plan
```

### Create Infrastructure

```bash
terraform apply
```

Type `yes` when prompted.

### Get Outputs

```bash
# Show all outputs
terraform output

# Get specific output
terraform output vm_external_ip

# Get SSH command
terraform output ssh_command
```

### Connect to VM

```bash
# Use the SSH command from output
ssh ubuntu@<external_ip>
```

### Destroy Infrastructure

```bash
terraform destroy
```

Type `yes` when prompted.

## Resources Created

- **VPC Network** - Virtual private cloud
- **Subnet** - 10.128.0.0/24 in ru-central1-a
- **Security Group** - Firewall rules (SSH, HTTP, port 5000)
- **Compute Instance** - VM with Ubuntu 22.04 LTS
  - 2 vCPU (20% core fraction - free tier)
  - 1 GB RAM
  - 10 GB HDD
  - Public IP address

## Files

- `main.tf` - Main configuration (provider, resources)
- `variables.tf` - Input variables
- `outputs.tf` - Output values
- `terraform.tfvars` - Variable values (gitignored, create from example)
- `key.json` - Service account key (gitignored)

## Troubleshooting

### Error: "Error while requesting API"

Check that:
- `key.json` exists and is valid
- `cloud_id` and `folder_id` are correct
- Service account has `editor` role

### Error: "quota exceeded"

You may have reached free tier limits. Check:
- Only one VM is running
- VM uses 20% core fraction
- Using free tier region (ru-central1-a)

### Cannot SSH to VM

Check that:
- Security group allows SSH (port 22)
- Your SSH public key is in `~/.ssh/id_rsa.pub`
- VM has finished booting (wait 1-2 minutes)

## Cost Management

This configuration uses free tier resources:
- ✅ 20% vCPU (free tier)
- ✅ 1 GB RAM (free tier)
- ✅ 10 GB HDD (free tier)

**Important:**
- Run `terraform destroy` when done testing
- Consider keeping VM for Lab 5 (Ansible)
- Monitor usage in Yandex Cloud Console

## Next Steps

After creating the VM:
1. SSH into the VM to verify access
2. Document the public IP
3. Keep VM running for Lab 5 (or destroy and recreate later)
4. Move to Pulumi implementation (Task 2)
