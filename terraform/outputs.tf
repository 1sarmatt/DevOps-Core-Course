# Outputs

output "vm_public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.lab_vm.public_ip
}

output "vm_private_ip" {
  description = "Private IP of the EC2 instance"
  value       = aws_instance.lab_vm.private_ip
}

output "vm_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.lab_vm.id
}

output "ssh_command" {
  description = "SSH command to connect"
  value       = "ssh -i labsuser.pem ubuntu@${aws_instance.lab_vm.public_ip}"
}
