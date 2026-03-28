# Lab 4: Pulumi Implementation

## Quick Summary

Successfully deployed AWS infrastructure using Pulumi with Python.

## Deployment Results

```
Type                              Name            Status      Duration
+   pulumi:pulumi:Stack               devops-lab-dev  created     48s
+   ├─ aws:ec2:Vpc                    lab-vpc         created     15s
+   ├─ aws:ec2:KeyPair                lab-key         created     1s
+   ├─ aws:ec2:Subnet                 lab-subnet      created     13s
+   ├─ aws:ec2:SecurityGroup          lab-sg          created     5s
+   ├─ aws:ec2:InternetGateway        lab-igw         created     1s
+   ├─ aws:ec2:RouteTable             lab-rt          created     2s
+   ├─ aws:ec2:RouteTableAssociation  lab-rta         created     1s
+   └─ aws:ec2:Instance               lab-vm          created     16s

Resources: 9 created
Duration: 51 seconds
```

## VM Information

- **Public IP:** 98.89.37.38
- **Private IP:** 10.0.1.159
- **Instance ID:** i-08ed00b6744c555fd
- **OS:** Ubuntu 22.04.5 LTS
- **Docker:** 28.2.2

## Test Results

✅ SSH access working  
✅ Docker installed and running  
✅ Nginx container deployed on port 5000  
✅ Web server accessible from internet  

## Cleanup

```
Resources: 9 deleted
Duration: 45 seconds
```

## Comparison with Terraform

| Metric | Terraform | Pulumi |
|--------|-----------|--------|
| Deployment Time | ~60s | 51s ⚡ |
| Destroy Time | ~60s | 45s ⚡ |
| Language | HCL | Python |
| Resources Created | 8 | 9 (includes stack) |
| Learning Curve | Easy | Medium |
| Code Lines | ~150 | ~120 |

## Conclusion

Pulumi successfully deployed identical infrastructure to Terraform with:
- Faster deployment and destroy times
- More programmatic approach
- Better IDE support
- Same reliability and results

See full documentation in `../terraform/docs/LAB04.md`
