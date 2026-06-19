"""AWS Infrastructure with Pulumi - Lab 4"""

import pulumi
import pulumi_aws as aws

# Configuration
config = pulumi.Config()
vm_name = config.get("vm_name") or "devops-lab-vm"
ssh_public_key_path = config.get("ssh_public_key_path") or "../terraform/labsuser.pub"

# Read SSH public key
with open(ssh_public_key_path, 'r') as f:
    ssh_public_key = f.read().strip()

# Create VPC
vpc = aws.ec2.Vpc("lab-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={"Name": "lab-vpc"}
)

# Create Internet Gateway
igw = aws.ec2.InternetGateway("lab-igw",
    vpc_id=vpc.id,
    tags={"Name": "lab-igw"}
)

# Create Subnet
subnet = aws.ec2.Subnet("lab-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    availability_zone="us-east-1a",
    map_public_ip_on_launch=True,
    tags={"Name": "lab-subnet"}
)

# Create Route Table
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

# Associate Route Table with Subnet
route_table_association = aws.ec2.RouteTableAssociation("lab-rta",
    subnet_id=subnet.id,
    route_table_id=route_table.id
)

# Create Security Group
security_group = aws.ec2.SecurityGroup("lab-sg",
    name="lab-security-group",
    description="Security group for Lab VM",
    vpc_id=vpc.id,
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            description="SSH",
            from_port=22,
            to_port=22,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
        ),
        aws.ec2.SecurityGroupIngressArgs(
            description="HTTP",
            from_port=80,
            to_port=80,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
        ),
        aws.ec2.SecurityGroupIngressArgs(
            description="App port",
            from_port=5000,
            to_port=5000,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            from_port=0,
            to_port=0,
            protocol="-1",
            cidr_blocks=["0.0.0.0/0"],
        )
    ],
    tags={"Name": "lab-sg"}
)

# Create Key Pair
key_pair = aws.ec2.KeyPair("lab-key",
    key_name="lab-key-pulumi",
    public_key=ssh_public_key
)

# Get latest Ubuntu AMI
ami = aws.ec2.get_ami(
    most_recent=True,
    owners=["099720109477"],  # Canonical
    filters=[
        aws.ec2.GetAmiFilterArgs(
            name="name",
            values=["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"],
        ),
        aws.ec2.GetAmiFilterArgs(
            name="virtualization-type",
            values=["hvm"],
        ),
    ]
)

# Create EC2 Instance
instance = aws.ec2.Instance("lab-vm",
    ami=ami.id,
    instance_type="t2.micro",
    subnet_id=subnet.id,
    vpc_security_group_ids=[security_group.id],
    key_name=key_pair.key_name,
    associate_public_ip_address=True,
    root_block_device=aws.ec2.InstanceRootBlockDeviceArgs(
        volume_size=10,
        volume_type="gp3",
    ),
    tags={"Name": vm_name}
)

# Export outputs
pulumi.export("vm_id", instance.id)
pulumi.export("vm_public_ip", instance.public_ip)
pulumi.export("vm_private_ip", instance.private_ip)
pulumi.export("ssh_command", pulumi.Output.concat("ssh -i ../terraform/labsuser.pem ubuntu@", instance.public_ip))
