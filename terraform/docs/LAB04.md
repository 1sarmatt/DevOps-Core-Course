# Lab 4: Infrastructure as Code (IaC)

## Objective
Learn the fundamentals of Infrastructure as Code (IaC) using Terraform and Pulumi to automate cloud infrastructure deployment.

## Tasks
1. ✅ Choose a cloud provider (AWS)
2. ✅ Deploy a virtual machine using Terraform
3. ✅ Configure network infrastructure (VPC, Security Groups)
4. ✅ Test SSH access to the VM
5. ⏳ Recreate infrastructure using Pulumi
6. ⏳ Compare experience with Terraform and Pulumi

---

## Part 1: Terraform

### 1.1 Cloud Provider Selection

**Selected Provider:** AWS (Amazon Web Services)

**Reasons for Selection:**
- AWS Academy provides temporary credentials for learning
- Extensive documentation and community support
- Free tier for EC2 t2.micro instances
- Simple integration with Terraform

**Alternatives Considered:**
- Yandex Cloud - encountered permission issues with service accounts
- Initially attempted to use Yandex Cloud but faced access limitations

### 1.2 Infrastructure Architecture

The following infrastructure was created in AWS:

```
┌─────────────────────────────────────────┐
│           AWS Region: us-east-1         │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │  VPC (10.0.0.0/16)                │  │
│  │                                   │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │ Subnet (10.0.1.0/24)        │  │  │
│  │  │                             │  │  │
│  │  │  ┌───────────────────────┐  │  │  │
│  │  │  │  EC2 Instance         │  │  │  │
│  │  │  │  - Ubuntu 22.04       │  │  │  │
│  │  │  │  - t2.micro           │  │  │  │
│  │  │  │  - Docker installed   │  │  │  │
│  │  │  └───────────────────────┘  │  │  │
│  │  │                             │  │  │
│  │  └─────────────────────────────┘  │  │
│  │                                   │  │
│  │  Security Group:                  │  │
│  │  - SSH (22)                       │  │
│  │  - HTTP (80)                      │  │
│  │  - App (5000)                     │  │
│  │                                   │  │
│  └───────────────────────────────────┘  │
│                                         │
│  Internet Gateway                       │
└─────────────────────────────────────────┘
```

### 1.3 Terraform Project Structure

```
terraform/
├── main.tf              # Main resource configuration
├── variables.tf         # Variable definitions
├── outputs.tf           # Output values
├── terraform.tfvars     # Variable values (not in Git)
├── .gitignore          # Git exclusions
├── labsuser.pem        # SSH private key (not in Git)
├── labsuser.pub        # SSH public key
└── docs/
    └── LAB04.md        # Documentation
```

### 1.4 Terraform Configuration

#### main.tf
Main resources:
- **AWS Provider** - AWS connection setup with session_token support
- **VPC** - Virtual Private Cloud (10.0.0.0/16)
- **Internet Gateway** - Internet access
- **Subnet** - Subnet (10.0.1.0/24) in us-east-1a zone
- **Route Table** - Traffic routing
- **Security Group** - Firewall rules (SSH, HTTP, App port 5000)
- **Key Pair** - SSH key for VM access
- **EC2 Instance** - Virtual machine Ubuntu 22.04, t2.micro

#### variables.tf
Variables:
- `aws_region` - AWS region (us-east-1)
- `aws_access_key` - access key (sensitive)
- `aws_secret_key` - secret key (sensitive)
- `aws_session_token` - session token for temporary credentials (sensitive)
- `vm_name` - VM name (devops-lab-vm)
- `ssh_public_key_path` - path to SSH public key

#### outputs.tf
Output values:
- `vm_public_ip` - VM public IP address
- `vm_private_ip` - VM private IP address
- `vm_id` - EC2 instance ID
- `ssh_command` - ready-to-use SSH command

### 1.5 Infrastructure Deployment

#### Step 1: SSH Key Preparation
```bash
# Extract public key from private key
ssh-keygen -y -f labsuser.pem > labsuser.pub
chmod 400 labsuser.pem
```

#### Step 2: Variable Configuration
Created `terraform.tfvars` file with AWS credentials:
```hcl
aws_region          = "us-east-1"
aws_access_key      = "ASIAXCKZLCGINX77RQXL"
aws_secret_key      = "***"
aws_session_token   = "***"
ssh_public_key_path = "./labsuser.pub"
```

#### Step 3: Terraform Initialization
```bash
terraform init
```

Result:
- Downloaded AWS provider version 5.100.0
- Created `.terraform` directory with providers
- Created `.terraform.lock.hcl` for versioning

#### Step 4: Plan Review
```bash
terraform plan
```

Plan showed creation of 8 resources:
- 1 VPC
- 1 Internet Gateway
- 1 Subnet
- 1 Route Table
- 1 Route Table Association
- 1 Security Group
- 1 Key Pair
- 1 EC2 Instance

#### Step 5: Apply Configuration
```bash
terraform apply -auto-approve
```

Result:
```
Apply complete! Resources: 8 added, 0 changed, 0 destroyed.

Outputs:
ssh_command = "ssh -i labsuser.pem ubuntu@100.53.122.197"
vm_id = "i-0a8db0dd79812f363"
vm_private_ip = "10.0.1.10"
vm_public_ip = "100.53.122.197"
```

### 1.6 Infrastructure Testing

#### SSH Connection
```bash
ssh -i labsuser.pem ubuntu@100.53.122.197
```

Result: ✅ Successful connection

#### System Check
```bash
uname -a
# Linux ip-10-0-1-10 6.8.0-1044-aws #46~22.04.1-Ubuntu SMP x86_64 GNU/Linux

cat /etc/os-release
# Ubuntu 22.04.5 LTS (Jammy Jellyfish)
```

#### Docker Installation and Testing
```bash
sudo apt update
sudo apt install -y docker.io
docker --version
# Docker version 28.2.2

sudo docker run hello-world
# Hello from Docker! ✅
```

#### Web Server Test
```bash
sudo docker run -d -p 5000:80 --name test-nginx nginx:alpine
curl http://localhost:5000
# Welcome to nginx! ✅
```

#### Browser Test
URL: `http://100.53.122.197:5000`

Result: ✅ Nginx page displays correctly (see screenshot)

![Nginx Welcome Page](screenshots/nginx-test.png)

### 1.7 Test Results

**What Works:**
- ✅ VM created and running
- ✅ SSH access configured and working
- ✅ Network configuration correct (VPC, Subnet, Internet Gateway)
- ✅ Security Group properly configured (ports 22, 80, 5000 open)
- ✅ Docker installed and working
- ✅ Containers running
- ✅ Web server accessible from internet

**System Information:**
- OS: Ubuntu 22.04.5 LTS (Jammy Jellyfish)
- Kernel: 6.8.0-1044-aws
- Architecture: x86_64
- Docker: 28.2.2
- Instance Type: t2.micro
- Public IP: 100.53.122.197
- Private IP: 10.0.1.10

### 1.8 State Management

Terraform created `terraform.tfstate` file to track infrastructure state:
- Contains information about all created resources
- Used to determine changes on next apply
- Should not be committed to Git (contains sensitive data)

### 1.9 Resource Cleanup

To delete all infrastructure:
```bash
terraform destroy -auto-approve
```

This will remove all 8 created resources and free up AWS resources.

---

## Part 2: Pulumi

### 2.1 Pulumi Installation

Installed Pulumi CLI:
```bash
brew install pulumi
# or
curl -fsSL https://get.pulumi.com | sh
```

Verified installation:
```bash
pulumi version
# v3.221.0
```

### 2.2 Project Creation

Created new Pulumi project with Python:
```bash
mkdir pulumi
cd pulumi
pulumi new aws-python
```

Project structure:
```
pulumi/
├── __main__.py          # Main infrastructure code (Python)
├── Pulumi.yaml          # Project configuration
├── Pulumi.dev.yaml      # Stack configuration
├── requirements.txt     # Python dependencies
├── venv/               # Python virtual environment
├── setup-aws.sh        # AWS credentials setup script
└── README.md           # Documentation
```

### 2.3 Infrastructure Code

Created the same infrastructure as Terraform in Python (`__main__.py`):

```python
import pulumi
import pulumi_aws as aws

# VPC
vpc = aws.ec2.Vpc("lab-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={"Name": "lab-vpc"}
)

# Internet Gateway
igw = aws.ec2.InternetGateway("lab-igw",
    vpc_id=vpc.id,
    tags={"Name": "lab-igw"}
)

# Subnet
subnet = aws.ec2.Subnet("lab-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    availability_zone="us-east-1a",
    map_public_ip_on_launch=True,
    tags={"Name": "lab-subnet"}
)

# Route Table
route_table = aws.ec2.RouteTable("lab-rt",
    vpc_id=vpc.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            gateway_id=igw.id,
        )
    ],
    tags={"Name": "lab-rt"}
)

# Security Group
security_group = aws.ec2.SecurityGroup("lab-sg",
    name="lab-security-group",
    description="Security group for Lab VM",
    vpc_id=vpc.id,
    ingress=[
        # SSH, HTTP, App port 5000
    ],
    egress=[
        # All outbound traffic
    ],
    tags={"Name": "lab-sg"}
)

# Key Pair
key_pair = aws.ec2.KeyPair("lab-key",
    key_name="lab-key-pulumi",
    public_key=ssh_public_key
)

# EC2 Instance
instance = aws.ec2.Instance("lab-vm",
    ami=ami.id,
    instance_type="t2.micro",
    subnet_id=subnet.id,
    vpc_security_group_ids=[security_group.id],
    key_name=key_pair.key_name,
    tags={"Name": vm_name}
)

# Outputs
pulumi.export("vm_public_ip", instance.public_ip)
pulumi.export("vm_private_ip", instance.private_ip)
pulumi.export("vm_id", instance.id)
pulumi.export("ssh_command", pulumi.Output.concat("ssh -i ../terraform/labsuser.pem ubuntu@", instance.public_ip))
```

### 2.4 Configuration

Set up AWS credentials:
```bash
# Created setup-aws.sh with AWS credentials
source setup-aws.sh

# Used local backend (no registration required)
pulumi login --local
```

### 2.5 Deployment

Deployed infrastructure:
```bash
pulumi up
```

Result:
```
Type                              Name            Status      
+   pulumi:pulumi:Stack               devops-lab-dev  created (48s)
+   ├─ aws:ec2:Vpc                    lab-vpc         created (15s)
+   ├─ aws:ec2:KeyPair                lab-key         created (1s)
+   ├─ aws:ec2:Subnet                 lab-subnet      created (13s)
+   ├─ aws:ec2:SecurityGroup          lab-sg          created (5s)
+   ├─ aws:ec2:InternetGateway        lab-igw         created (1s)
+   ├─ aws:ec2:RouteTable             lab-rt          created (2s)
+   ├─ aws:ec2:RouteTableAssociation  lab-rta         created (1s)
+   └─ aws:ec2:Instance               lab-vm          created (16s)

Outputs:
    ssh_command  : "ssh -i ../terraform/labsuser.pem ubuntu@98.89.37.38"
    vm_id        : "i-08ed00b6744c555fd"
    vm_private_ip: "10.0.1.159"
    vm_public_ip : "98.89.37.38"

Resources:
    + 9 created

Duration: 51s
```

### 2.6 Testing

#### SSH Connection
```bash
ssh -i ../terraform/labsuser.pem ubuntu@98.89.37.38
```

Result: ✅ Successful connection

#### System Check
```bash
uname -a
# Linux ip-10-0-1-159 6.8.0-1044-aws #46~22.04.1-Ubuntu SMP x86_64 GNU/Linux

cat /etc/os-release
# Ubuntu 22.04.5 LTS (Jammy Jellyfish)
```

#### Docker Installation and Testing
```bash
sudo apt update
sudo apt install -y docker.io
docker --version
# Docker version 28.2.2

sudo docker run hello-world
# Hello from Docker! ✅
```

#### Web Server Test
```bash
sudo docker run -d -p 5000:80 --name test-nginx nginx:alpine
curl http://localhost:5000
# Welcome to nginx! ✅
```

#### Browser Test
URL: `http://98.89.37.38:5000`

Result: ✅ Nginx page displays correctly

### 2.7 Test Results

**What Works:**
- ✅ VM created and running
- ✅ SSH access configured and working
- ✅ Network configuration correct (VPC, Subnet, Internet Gateway)
- ✅ Security Group properly configured (ports 22, 80, 5000 open)
- ✅ Docker installed and working
- ✅ Containers running
- ✅ Web server accessible from internet

**System Information:**
- OS: Ubuntu 22.04.5 LTS (Jammy Jellyfish)
- Kernel: 6.8.0-1044-aws
- Architecture: x86_64
- Docker: 28.2.2
- Instance Type: t2.micro
- Public IP: 98.89.37.38
- Private IP: 10.0.1.159

### 2.8 State Management

Pulumi uses local backend (`.pulumi/` directory):
- State stored locally in JSON format
- Can also use Pulumi Cloud for team collaboration
- Supports encryption of secrets

### 2.9 Resource Cleanup

Destroyed all infrastructure:
```bash
pulumi destroy
```

Result:
```
Resources:
    - 9 deleted

Duration: 45s
```

---

## Part 3: Terraform vs Pulumi Comparison

### 3.1 Syntax and Language

**Terraform:**
- Uses HCL (HashiCorp Configuration Language)
- Declarative configuration files
- Domain-specific language

Example:
```hcl
resource "aws_vpc" "lab_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "lab-vpc"
  }
}
```

**Pulumi:**
- Uses general-purpose programming languages (Python, TypeScript, Go, C#, Java)
- Programmatic infrastructure definition
- Full language features (loops, conditionals, functions)

Example:
```python
vpc = aws.ec2.Vpc("lab-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={"Name": "lab-vpc"}
)
```

### 3.2 State Management

**Terraform:**
- Local `terraform.tfstate` file by default
- Can use remote backends (S3, Terraform Cloud)
- State locking with DynamoDB
- Manual state file management

**Pulumi:**
- Local `.pulumi/` directory or Pulumi Cloud
- Built-in state encryption
- Automatic state management
- Stack-based organization

### 3.3 Deployment Speed

**Terraform:**
- Initial deployment: 8 resources created
- Time: ~60 seconds
- Destroy: ~60 seconds

**Pulumi:**
- Initial deployment: 9 resources created (includes stack)
- Time: 51 seconds ⚡
- Destroy: 45 seconds ⚡

### 3.4 Learning Curve

**Terraform:**
- ✅ Simple, declarative syntax
- ✅ Easy to read and understand
- ✅ Extensive documentation
- ❌ Limited to HCL features
- ❌ No native programming constructs

**Pulumi:**
- ✅ Use familiar programming languages
- ✅ Full IDE support (autocomplete, type checking)
- ✅ Reusable functions and modules
- ❌ Requires programming knowledge
- ❌ More complex for simple tasks

### 3.5 Ecosystem and Community

**Terraform:**
- ✅ Mature ecosystem (2014)
- ✅ Large community
- ✅ Extensive provider support
- ✅ Industry standard

**Pulumi:**
- ✅ Growing ecosystem (2018)
- ✅ Modern approach
- ✅ Same providers as Terraform
- ❌ Smaller community

### 3.6 Developer Experience

**Terraform:**
- Configuration files (`.tf`)
- `terraform plan` / `terraform apply`
- Variables in `.tfvars` files
- Modules for reusability

**Pulumi:**
- Code files (`.py`, `.ts`, etc.)
- `pulumi preview` / `pulumi up`
- Config via `pulumi config set`
- Native language packages for reusability

### 3.7 Testing

**Terraform:**
- `terraform validate` for syntax
- `terraform plan` for preview
- Third-party tools (Terratest, Kitchen-Terraform)

**Pulumi:**
- Native unit testing with language frameworks
- `pulumi preview` for preview
- Integration testing support
- Property-based testing

### 3.8 Use Cases

**Terraform is better for:**
- ✅ Simple, declarative infrastructure
- ✅ Teams without programming background
- ✅ Industry-standard compliance
- ✅ Multi-cloud with consistent syntax

**Pulumi is better for:**
- ✅ Complex logic and conditionals
- ✅ Developer-heavy teams
- ✅ Code reusability and abstraction
- ✅ Integration with existing codebases

### 3.9 Cost

**Both:**
- ✅ Free and open-source
- ✅ Optional paid cloud backends
- ✅ Same AWS infrastructure costs

### 3.10 Summary Table

| Feature | Terraform | Pulumi |
|---------|-----------|--------|
| Language | HCL | Python, TS, Go, C#, Java |
| Deployment Time | ~60s | ~51s ⚡ |
| Learning Curve | Easy | Medium |
| State Management | Local file | Local or Cloud |
| IDE Support | Limited | Full |
| Testing | External tools | Native |
| Community | Large | Growing |
| Maturity | High | Medium |
| Best For | Simple infra | Complex logic |

---

## Conclusions

### What Was Learned:
1. ✅ Infrastructure as Code (IaC) fundamentals
2. ✅ Working with Terraform for AWS
3. ✅ Working with Pulumi for AWS
4. ✅ Creating VPC, Subnet, Security Groups
5. ✅ Deploying EC2 instances
6. ✅ Managing SSH keys
7. ✅ Working with temporary AWS credentials (session_token)
8. ✅ Comparing two IaC approaches

### Key Takeaways:

**Terraform:**
- Excellent for declarative infrastructure
- Easy to learn and read
- Industry standard
- Great for teams with mixed technical backgrounds

**Pulumi:**
- Powerful for complex scenarios
- Leverages programming language features
- Faster deployment times
- Better for developer-centric teams

**Both:**
- Achieve the same infrastructure result
- Support AWS and multi-cloud
- Enable version control and collaboration
- Significantly better than manual cloud console management

### Problems and Solutions:
1. **Problem:** Yandex Cloud - lack of permissions for service accounts
   - **Solution:** Switched to AWS

2. **Problem:** SSH Permission denied with labsuser.pem
   - **Solution:** Extracted public key from .pem file and recreated VM

3. **Problem:** AWS requires session_token for temporary credentials
   - **Solution:** Added aws_session_token variable to Terraform and environment variable for Pulumi

4. **Problem:** Pulumi path to SSH key
   - **Solution:** Used relative path `../terraform/labsuser.pem`

### Personal Preference:
After testing both tools:
- **Terraform** is better for simple, straightforward infrastructure
- **Pulumi** is more powerful for complex scenarios with logic
- Both are excellent tools, choice depends on team and use case

### Next Steps (Optional):
1. ⏳ Try Terraform Cloud for remote state
2. ⏳ Try Pulumi Cloud for team collaboration
3. ⏳ Implement CI/CD for infrastructure deployment
4. ⏳ Add monitoring and alerting
5. ⏳ Try other cloud providers (GCP, Azure)

---

## Useful Commands

### Terraform
```bash
# Initialize
terraform init

# Validate configuration
terraform validate

# Format code
terraform fmt

# View plan
terraform plan

# Apply changes
terraform apply

# Destroy resources
terraform destroy

# Show state
terraform show

# List resources
terraform state list
```

### AWS CLI (optional)
```bash
# Check credentials
aws sts get-caller-identity

# List EC2 instances
aws ec2 describe-instances

# List VPCs
aws ec2 describe-vpcs
```

---

## References

- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [Pulumi Documentation](https://www.pulumi.com/docs/)

---

**Completion Date:** February 18, 2026  
**Author:** Sarmat Lutfullin  
**Status:** Completed ✅ (Both Terraform and Pulumi)
