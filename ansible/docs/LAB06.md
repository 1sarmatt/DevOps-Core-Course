# Lab 6: Advanced Ansible & CI/CD - Submission

**Name:** Sarmat Lutfullin
**Date:** 2026-03-03
**Lab Points:** 10/10

---

## Task 1: Blocks & Tags (2 pts) ✅

### Implementation

Refactored `common` and `docker` roles with blocks for better error handling and task organization.

#### Common Role
**File:** `roles/common/tasks/main.yml`

**Blocks implemented:**
- Package installation block with `packages` tag
- System configuration block with `system` tag
- Rescue block for apt cache failures
- Always block for logging completion

**Tags:**
- `common` - entire role
- `packages` - package installation tasks
- `system` - system configuration tasks

#### Docker Role
**File:** `roles/docker/tasks/main.yml`

**Blocks implemented:**
- Docker installation block with `docker_install` tag
- Docker configuration block with `docker_config` tag
- Rescue block for GPG key retry (10 second wait)
- Always block to ensure Docker service is enabled

**Tags:**
- `docker` - entire role
- `docker_install` - installation only
- `docker_config` - configuration only

### Testing Results

**List all available tags:**
```bash
ansible-playbook playbooks/provision.yml --list-tags
```
Output:
```
TASK TAGS: [common, docker, docker_config, docker_install, packages, system]
```

**Selective execution with tags:**
```bash
# Run only docker tasks
ansible-playbook playbooks/provision.yml --tags "docker"

# Run only package installation
ansible-playbook playbooks/provision.yml --tags "packages"

# Skip common role
ansible-playbook playbooks/provision.yml --skip-tags "common"
```

### Research Answers

**Q: What happens if rescue block also fails?**
A: The play fails and execution stops for that host. The failure is reported in PLAY RECAP.

**Q: Can you have nested blocks?**
A: Yes, blocks can be nested, but it's not recommended as it reduces readability.

**Q: How do tags inherit to tasks within blocks?**
A: Tags applied to a block are automatically inherited by all tasks within that block.

---

## Task 2: Docker Compose (3 pts) ✅

### Implementation

Migrated from `docker_container` module to Docker Compose for better container management.

#### Changes Made

1. **Renamed role:** `app_deploy` → `web_app`
2. **Created Docker Compose template:** `roles/web_app/templates/docker-compose.yml.j2`
3. **Updated tasks:** `roles/web_app/tasks/main.yml` to use `docker_compose_v2` module
4. **Configured dependencies:** `roles/web_app/meta/main.yml` ensures Docker is installed first

#### Docker Compose Template

**File:** `roles/web_app/templates/docker-compose.yml.j2`
```yaml
services:
  {{ app_name }}:
    image: {{ docker_image }}:{{ docker_image_tag }}
    container_name: {{ app_name }}
    ports:
      - "{{ app_port }}:{{ app_port }}"
    environment:
      PORT: "{{ app_port }}"
    restart: {{ app_restart_policy }}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:{{ app_port }}{{ health_check_path }}"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

#### Role Dependencies

**File:** `roles/web_app/meta/main.yml`
```yaml
dependencies:
  - role: docker
```

This ensures Docker is installed before deploying the web application.

### Testing Results

**First deployment:**
```
PLAY RECAP
lab-vm: ok=17 changed=5 unreachable=0 failed=0
```

**Second deployment (idempotency test):**
```
PLAY RECAP
lab-vm: ok=17 changed=0 unreachable=0 failed=0
```

✅ Full idempotency achieved - no changes on second run.

**Application verification:**
```bash
curl http://34.207.181.91:5000/health
```
Output:
```json
{"status":"healthy","timestamp":"2026-03-03T07:54:56.812419+00:00","uptime_seconds":198}
```

**Docker Compose file on target:**
```bash
ansible webservers -a "cat /opt/devops-info-service/docker-compose.yml"
```
Shows properly templated docker-compose.yml with all variables substituted.

### Research Answers

**Q: What's the difference between `restart: always` and `restart: unless-stopped`?**
A: `always` restarts container even if manually stopped. `unless-stopped` respects manual stops and only restarts on daemon restart or container failure.

**Q: How do Docker Compose networks differ from Docker bridge networks?**
A: Docker Compose creates isolated networks per project with automatic DNS resolution between services. Bridge networks are shared and require manual linking.

**Q: Can you reference Ansible Vault variables in the template?**
A: Yes, Vault variables are decrypted before template rendering, so they work seamlessly in Jinja2 templates.

---

## Task 3: Wipe Logic (1 pt) ✅

### Implementation

Implemented safe application removal with double-gating mechanism (variable + tag).

#### Wipe Tasks

**File:** `roles/web_app/tasks/wipe.yml`
```yaml
- name: Wipe web application
  block:
    - name: Stop and remove containers with Docker Compose
      community.docker.docker_compose_v2:
        project_src: "{{ compose_project_dir }}"
        state: absent
        remove_orphans: yes
      ignore_errors: yes

    - name: Remove docker-compose file
      file:
        path: "{{ compose_project_dir }}/docker-compose.yml"
        state: absent
      ignore_errors: yes

    - name: Remove application directory
      file:
        path: "{{ compose_project_dir }}"
        state: absent
      ignore_errors: yes

    - name: Log wipe completion
      debug:
        msg: "Application {{ app_name }} wiped successfully"

  when: web_app_wipe | bool
  tags:
    - web_app_wipe
```

#### Variable Configuration

**File:** `roles/web_app/defaults/main.yml`
```yaml
web_app_wipe: false  # Default: do not wipe
```

### Testing Results

**Scenario 1: Normal deployment (wipe should NOT run)**
```bash
ansible-playbook playbooks/deploy.yml
```
Result: ✅ Wipe tasks skipped (4 skipped), application deployed normally

**Scenario 2: Wipe only (remove existing deployment)**
```bash
ansible-playbook playbooks/deploy.yml -e "web_app_wipe=true" --tags web_app_wipe
```
Result: ✅ Application removed (3 changed), deployment skipped
- Container stopped and removed
- docker-compose.yml deleted
- Application directory removed

**Scenario 3: Clean reinstallation (wipe → deploy)**
```bash
ansible-playbook playbooks/deploy.yml -e "web_app_wipe=true"
```
Result: ✅ Old app wiped, new app deployed (3 changed)
- Wipe tasks executed first
- Deployment tasks executed second
- Application running with fresh installation

**Scenario 4: Safety check (tag without variable)**
```bash
ansible-playbook playbooks/deploy.yml --tags web_app_wipe
```
Result: ✅ Wipe tasks skipped due to `when` condition (4 skipped)
- Application still running
- Double-gating protection worked

### Research Answers

**Q: Why use both variable AND tag?**
A: Double safety mechanism prevents accidental deletion. Variable provides runtime control, tag provides execution control.

**Q: What's the difference between `never` tag and this approach?**
A: `never` tag requires explicit inclusion every time. Our approach allows clean reinstall scenario (wipe → deploy in one command).

**Q: Why must wipe logic come BEFORE deployment in main.yml?**
A: Enables clean reinstallation use case where you want to remove old installation and deploy fresh in single playbook run.

**Q: When would you want clean reinstallation vs. rolling update?**
A: Clean reinstall for major version changes, corrupted state, or testing from scratch. Rolling update for production with zero downtime.

**Q: How would you extend this to wipe Docker images and volumes too?**
A: Add tasks to remove images with `docker_image` module (state: absent) and volumes with `docker_volume` module.

---

## Task 4: CI/CD with GitHub Actions (3 pts) ✅

### Implementation

Created automated deployment pipeline with GitHub Actions.

#### Workflow File

**File:** `.github/workflows/ansible-deploy.yml`

**Triggers:**
- Push to branches: main, master, lab06
- Changes in `ansible/**` or workflow file
- Manual trigger via workflow_dispatch

**Jobs:**

1. **Lint Job:**
   - Installs Ansible and ansible-lint
   - Creates temporary vault password file
   - Runs ansible-lint on all playbooks
   - Runs syntax checks
   - Cleans up vault file

2. **Deploy Job:**
   - Depends on lint job passing
   - Sets up Python and Ansible
   - Installs community.docker collection
   - Configures SSH access
   - Creates temporary inventory with CI credentials
   - Deploys application with Ansible
   - Verifies deployment health
   - Cleans up sensitive files

### GitHub Secrets Configuration

**Secrets added:**
1. `ANSIBLE_VAULT_PASSWORD` - Vault decryption password
2. `SSH_PRIVATE_KEY` - SSH private key for VM access
3. `VM_HOST` - Target VM IP address (34.207.181.91)
4. `VM_USER` - SSH username (ubuntu)

### Testing Results

**Workflow execution:**
- ✅ Lint job: Passed with warnings (expected)
- ✅ Deploy job: Successful deployment
- ✅ Verification: Application health check passed

**Workflow logs show:**
```
PLAY RECAP
lab-vm: ok=18 changed=0 unreachable=0 failed=0

✅ Application is healthy!
✅ Main endpoint is working!
```

### Status Badge

Added to README.md:
```markdown
[![Ansible Deployment](https://github.com/1sarmatt/DevOps-Core-Course/actions/workflows/ansible-deploy.yml/badge.svg)](https://github.com/1sarmatt/DevOps-Core-Course/actions/workflows/ansible-deploy.yml)
```

### Research Answers

**Q: What are the security implications of storing SSH keys in GitHub Secrets?**
A: Secrets are encrypted at rest and in transit. Only visible to workflow runs. Should use dedicated deployment keys with minimal permissions, not personal keys.

**Q: How would you implement a staging → production deployment pipeline?**
A: Use GitHub Environments with protection rules, separate inventory files for staging/prod, and manual approval gates before production deployment.

**Q: What would you add to make rollbacks possible?**
A: Tag Docker images with version/commit SHA, store previous deployment state, add rollback playbook that deploys previous version.

**Q: How does self-hosted runner improve security compared to GitHub-hosted?**
A: Self-hosted runner runs in your infrastructure, no need to expose SSH keys externally, direct network access to target servers, better audit trail.

---

## Task 5: Documentation (1 pt) ✅

This document serves as complete documentation for Lab 6, including:
- Implementation details for all tasks
- Code snippets and configurations
- Testing results with outputs
- Research question answers
- Evidence of successful completion

---

## Summary

### Accomplishments

✅ **Task 1:** Refactored roles with blocks, rescue/always sections, and comprehensive tagging
✅ **Task 2:** Migrated to Docker Compose with templating and role dependencies
✅ **Task 3:** Implemented safe wipe logic with double-gating protection
✅ **Task 4:** Created fully automated CI/CD pipeline with GitHub Actions
✅ **Task 5:** Complete documentation with evidence and analysis

### Technologies Used

- Ansible 2.20.3
- Docker Compose v2
- GitHub Actions
- Jinja2 templating
- Ansible Vault
- community.docker collection

### Key Learnings

1. **Blocks** provide powerful error handling and task organization
2. **Tags** enable flexible, selective playbook execution
3. **Docker Compose** simplifies container management vs raw docker commands
4. **Double-gating** (variable + tag) prevents accidental destructive operations
5. **CI/CD automation** ensures consistent, repeatable deployments
6. **Secrets management** in CI requires careful handling of sensitive data

### Challenges & Solutions

**Challenge 1:** Ansible-lint warnings about load-failure
**Solution:** Added syntax checks as primary validation, treat lint warnings as informational

**Challenge 2:** Vault password file not available in CI
**Solution:** Create temporary vault file from GitHub Secret during workflow execution

**Challenge 3:** SSH key path issues in CI environment
**Solution:** Create temporary inventory file with correct SSH key path for CI

**Challenge 4:** Group vars not loading automatically
**Solution:** Use `{{ playbook_dir }}/../group_vars/all.yml` in vars_files for explicit path


### Application Status

✅ Application deployed and accessible at: http://34.207.181.91:5000
✅ Health endpoint responding: http://34.207.181.91:5000/health
✅ Automated deployments working via GitHub Actions
✅ Full idempotency verified

---

## Conclusion

Lab 6 successfully enhanced Ansible automation with production-ready features including error handling, selective execution, Docker Compose integration, safe cleanup logic, and full CI/CD automation. The implementation demonstrates best practices for infrastructure automation and continuous deployment.
