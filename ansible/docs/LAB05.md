# Lab 5: Ansible Fundamentals

## Overview

Successfully implemented Infrastructure as Code using Ansible with role-based architecture for automated server provisioning and application deployment.

**Completed Tasks:**
- ✅ Ansible setup and role-based project structure
- ✅ System provisioning with idempotent roles (common, docker)
- ✅ Application deployment with Ansible Vault
- ✅ Secure credential management
- ✅ Automated Docker container deployment

---

## 1. Architecture Overview

### Ansible Version
```
ansible [core 2.20.2]
python version = 3.14.3
```

### Target VM
- **OS:** Ubuntu 22.04.5 LTS (Jammy Jellyfish)
- **IP:** 13.222.159.43
- **Cloud:** AWS EC2 (t2.micro)
- **Access:** SSH with key-based authentication

### Project Structure

```
ansible/
├── inventory/
│   └── hosts.ini              # Static inventory with VM details
├── roles/
│   ├── common/                # System packages and configuration
│   │   ├── tasks/main.yml
│   │   └── defaults/main.yml
│   ├── docker/                # Docker installation and setup
│   │   ├── tasks/main.yml
│   │   ├── handlers/main.yml
│   │   └── defaults/main.yml
│   └── app_deploy/            # Application deployment
│       ├── tasks/main.yml
│       ├── handlers/main.yml
│       └── defaults/main.yml
├── playbooks/
│   ├── site.yml               # Complete setup (all roles)
│   ├── provision.yml          # System provisioning only
│   └── deploy.yml             # Application deployment only
├── group_vars/
│   └── all.yml               # Encrypted variables (Ansible Vault)
├── ansible.cfg               # Ansible configuration
└── docs/
    └── LAB05.md              # This documentation
```

### Why Roles?

**Benefits of role-based architecture:**
1. **Reusability** - Use same role across multiple projects
2. **Organization** - Clear structure, easy to navigate
3. **Maintainability** - Changes in one place
4. **Modularity** - Mix and match roles as needed
5. **Testing** - Test roles independently
6. **Sharing** - Share roles via Ansible Galaxy

---

## 2. Roles Documentation

### 2.1 Common Role

**Purpose:** Basic system setup that every server needs.

**Tasks:**
- Update apt cache
- Install essential packages (python3-pip, curl, git, vim, htop, etc.)
- Set system timezone

**Variables (defaults/main.yml):**
```yaml
common_packages:
  - python3-pip
  - curl
  - git
  - vim
  - htop
  - net-tools
  - software-properties-common
  - apt-transport-https
  - ca-certificates
  - gnupg
  - lsb-release

timezone: "UTC"
```

**Handlers:** None

**Dependencies:** None

---

### 2.2 Docker Role

**Purpose:** Install and configure Docker CE on Ubuntu.

**Tasks:**
1. Remove old Docker versions
2. Add Docker GPG key
3. Add Docker repository
4. Update apt cache
5. Install Docker packages (docker-ce, docker-ce-cli, containerd.io)
6. Ensure Docker service is running and enabled
7. Add user to docker group
8. Install python3-docker for Ansible docker modules

**Variables (defaults/main.yml):**
```yaml
docker_user: ubuntu
docker_packages:
  - docker-ce
  - docker-ce-cli
  - containerd.io
  - docker-buildx-plugin
  - docker-compose-plugin
```

**Handlers (handlers/main.yml):**
```yaml
- name: restart docker
  service:
    name: docker
    state: restarted
```

**Dependencies:** None (but typically runs after common role)

**Idempotency:** All tasks are idempotent - safe to run multiple times.

---

### 2.3 App Deploy Role

**Purpose:** Deploy containerized Python application from Docker Hub.

**Tasks:**
1. Log in to Docker Hub (using vaulted credentials)
2. Pull Docker image
3. Stop existing container (if running)
4. Remove old container (if exists)
5. Run new container with proper configuration
6. Wait for application port to be available
7. Verify health endpoint

**Variables (defaults/main.yml):**
```yaml
app_restart_policy: unless-stopped
app_env_vars: {}
health_check_path: /health
health_check_timeout: 30
```

**Variables from Vault (group_vars/all.yml):**
```yaml
dockerhub_username: 1sarmatt
dockerhub_password: [ENCRYPTED]
app_name: devops-info-service
docker_image: "{{ dockerhub_username }}/{{ app_name }}"
docker_image_tag: latest
app_port: 5000
app_container_name: devops-app
```

**Handlers (handlers/main.yml):**
```yaml
- name: restart application
  community.docker.docker_container:
    name: "{{ app_container_name }}"
    state: started
    restart: yes
```

**Dependencies:** Requires docker role to be run first.

---

## 3. Idempotency Demonstration

### First Run (provision.yml)

```bash
$ ansible-playbook playbooks/provision.yml
```

**Output:**
```
PLAY RECAP *********************************************************************
lab-vm                     : ok=13   changed=10   unreachable=0    failed=0
```

**Analysis:**
- 13 tasks executed
- 10 tasks showed "changed" status (yellow)
- System was modified: packages installed, Docker configured, services started

**What changed:**
- apt cache updated
- Common packages installed
- Timezone set
- Docker GPG key added
- Docker repository added
- Docker packages installed
- Docker service started and enabled
- User added to docker group
- python3-docker installed
- Docker service restarted (handler)

---

### Second Run (provision.yml)

```bash
$ ansible-playbook playbooks/provision.yml
```

**Output:**
```
PLAY RECAP *********************************************************************
lab-vm                     : ok=12   changed=0   unreachable=0    failed=0
```

**Analysis:**
- 12 tasks executed
- 0 tasks showed "changed" status - all green (ok)
- No modifications made - system already in desired state

**Why nothing changed:**
- apt cache still valid (cache_valid_time: 3600)
- Packages already installed (state: present)
- Timezone already set
- Docker GPG key already present
- Docker repository already configured
- Docker packages already installed
- Docker service already running
- User already in docker group
- python3-docker already installed
- No handler triggered (no changes to notify)

---

### What Makes Tasks Idempotent?

**1. Stateful Modules:**
- `apt: state=present` - Only installs if not present
- `service: state=started` - Only starts if not running
- `user: groups=docker` - Only adds if not in group

**2. Conditional Execution:**
- `cache_valid_time: 3600` - Only updates if cache older than 1 hour
- `ignore_errors: yes` - Handles cases where resource doesn't exist

**3. Declarative Approach:**
- Describe desired state, not steps
- Ansible determines what changes are needed
- Same playbook run = same result

---

## 4. Ansible Vault Usage

### Why Ansible Vault?

**Security Requirements:**
- Docker Hub credentials must not be committed to Git
- Passwords should be encrypted at rest
- Secrets should be decrypted only during execution

### Vault Implementation

**Created encrypted file:**
```bash
ansible-vault create group_vars/all.yml
```

**Vault password management:**
- Password stored in `.vault_pass` file (gitignored)
- Configured in `ansible.cfg`:
  ```ini
  vault_password_file = .vault_pass
  ```

**Encrypted content (group_vars/all.yml):**
```
$ANSIBLE_VAULT;1.1;AES256
[ENCRYPTED DATA]
```

**Decrypted content structure:**
```yaml
---
# Docker Hub credentials
dockerhub_username: 1sarmatt
dockerhub_password: [REDACTED]

# Application configuration
app_name: devops-info-service
docker_image: "{{ dockerhub_username }}/{{ app_name }}"
docker_image_tag: latest
app_port: 5000
app_container_name: devops-app
```

### Vault Operations

**View encrypted file:**
```bash
ansible-vault view group_vars/all.yml
```

**Edit encrypted file:**
```bash
ansible-vault edit group_vars/all.yml
```

**Verify variables loaded:**
```bash
ansible all -m debug -a "var=dockerhub_username"
```

### Security Best Practices

1. ✅ Vault password file in `.gitignore`
2. ✅ Encrypted file safe to commit
3. ✅ `no_log: true` for sensitive tasks (prevents logging credentials)
4. ✅ Vault password never in code or logs

---

## 5. Deployment Verification

### Deployment Execution

```bash
$ ansible-playbook playbooks/deploy.yml
```

**Output:**
```
PLAY [Deploy application] ******************************************************

TASK [Gathering Facts] *********************************************************
ok: [lab-vm]

TASK [app_deploy : Log in to Docker Hub] ***************************************
ok: [lab-vm]

TASK [app_deploy : Pull Docker image] ******************************************
ok: [lab-vm]

TASK [app_deploy : Stop existing container (if running)] ***********************
changed: [lab-vm]

TASK [app_deploy : Remove old container (if exists)] ***************************
changed: [lab-vm]

TASK [app_deploy : Run application container] **********************************
changed: [lab-vm]

TASK [app_deploy : Wait for application port to be available] ******************
ok: [lab-vm]

TASK [app_deploy : Verify application health endpoint] *************************
ok: [lab-vm]

RUNNING HANDLER [app_deploy : restart application] *****************************
changed: [lab-vm]

PLAY RECAP *********************************************************************
lab-vm                     : ok=9    changed=4    unreachable=0    failed=0
```

---

### Container Status

```bash
$ ansible webservers -a "docker ps"
```

**Output:**
```
CONTAINER ID   IMAGE                                 COMMAND           CREATED         STATUS         PORTS                    NAMES
702c04852ffe   1sarmatt/devops-info-service:latest   "python app.py"   2 minutes ago   Up 2 minutes   0.0.0.0:5000->5000/tcp   devops-app
```

---

### Health Check Verification

**Main endpoint (/):**
```bash
$ curl http://13.222.159.43:5000/
```

**Response:**
```json
{
  "service": {
    "name": "devops-info-service",
    "version": "1.0.0",
    "description": "DevOps course info service",
    "framework": "Flask"
  },
  "system": {
    "hostname": "702c04852ffe",
    "platform": "Linux",
    "architecture": "x86_64",
    "python_version": "3.13.12"
  },
  "runtime": {
    "uptime_seconds": 43,
    "current_time": "2026-02-23T18:33:59.689769+00:00"
  }
}
```

**Health endpoint (/health):**
```bash
$ curl http://13.222.159.43:5000/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-23T18:34:20.074537+00:00",
  "uptime_seconds": 64
}
```

---

### Handler Execution

**Handler triggered:** `restart application`

**When:** After container is created/updated

**Action:** Restarts the container to ensure latest configuration

---

## 6. Key Decisions

### Why use roles instead of plain playbooks?

Roles provide modular, reusable infrastructure code. Instead of one large playbook with all tasks, we have:
- Separate concerns (system setup vs Docker vs app deployment)
- Reusable components across projects
- Clear organization and maintainability
- Independent testing of each role

### How do roles improve reusability?

Each role is self-contained with its own tasks, handlers, and defaults. The `docker` role can be used in any project that needs Docker, without modification. Variables in `defaults/` can be overridden per-project.

### What makes a task idempotent?

Using stateful modules that check current state before making changes. For example, `apt: state=present` only installs if package is missing. Running the same task twice produces the same result without errors.

### How do handlers improve efficiency?

Handlers only run when notified by a task that made changes. For example, Docker service only restarts if configuration changed, not on every playbook run. This saves time and reduces unnecessary service disruptions.

### Why is Ansible Vault necessary?

Credentials must never be committed to Git in plaintext. Vault encrypts sensitive data while allowing it to be version controlled. Only users with the vault password can decrypt and use the credentials.

---

## 7. Challenges and Solutions

### Challenge 1: Ansible Vault variables not loading

**Problem:** Variables from `group_vars/all.yml` were undefined in roles when playbooks were in `playbooks/` subdirectory.

**Solution:** Added `vars_files: - ../group_vars/all.yml` to playbooks to explicitly load encrypted variables.

### Challenge 2: Docker image not found

**Problem:** Initial image name `devops-info-service-python` didn't exist on Docker Hub.

**Solution:** Updated vault to use correct image name `devops-info-service` that was already pushed to Docker Hub.

### Challenge 3: Container stop/remove tasks failing

**Problem:** `docker_container` module required `image` parameter even for stop/remove operations.

**Solution:** Added `image` parameter to stop task, kept `ignore_errors: yes` for graceful handling of non-existent containers.

---

## Conclusion

Successfully implemented Ansible automation for:
- ✅ System provisioning with idempotent roles
- ✅ Docker installation and configuration
- ✅ Secure credential management with Vault
- ✅ Automated application deployment
- ✅ Health check verification

**Key Learnings:**
- Role-based architecture provides clean, maintainable code
- Idempotency ensures safe, repeatable automation
- Ansible Vault secures sensitive data
- Handlers optimize service management
- Declarative approach simplifies infrastructure management

**Infrastructure is now:**
- Fully automated (no manual steps)
- Version controlled (except secrets)
- Repeatable (same result every time)
- Documented (this file)

---

## Useful Commands

### Ansible

```bash
# Test connectivity
ansible all -m ping

# Run ad-hoc command
ansible webservers -a "docker ps"

# Check variables
ansible all -m debug -a "var=dockerhub_username"

# Run playbooks
ansible-playbook playbooks/provision.yml
ansible-playbook playbooks/deploy.yml
ansible-playbook playbooks/site.yml

# Vault operations
ansible-vault create group_vars/all.yml
ansible-vault edit group_vars/all.yml
ansible-vault view group_vars/all.yml
```

### Verification

```bash
# Check application
curl http://13.222.159.43:5000/
curl http://13.222.159.43:5000/health

# Check container
ansible webservers -a "docker ps"
ansible webservers -a "docker logs devops-app"
```

---

**Completion Date:** February 23, 2026  
**Author:** Sarmat Lutfullin  
**Status:** Completed ✅
