# Contributing to SimpleX SMP Monitor

First off, thank you for considering contributing to SimpleX SMP Monitor! 🎉

This document provides guidelines and information for contributors. Following these guidelines helps communicate that you respect the time of the developers managing this project.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Message Format](#commit-message-format)
- [Pull Request Process](#pull-request-process)
- [Developer Certificate of Origin (DCO)](#developer-certificate-of-origin-dco)
- [Community](#community)

---

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior via [GitHub Private Reporting](https://github.com/cannatoshi/simplex-smp-monitor/security).

---

## Getting Started

### Before You Start

1. **Check existing issues** - Your idea might already be discussed
2. **Read the documentation** - Familiarize yourself with the [README](README.md)
3. **Discuss first** - For significant changes, open an issue or discussion before coding

### Types of Contributions We Welcome

| Contribution | Description |
|--------------|-------------|
| 🐛 **Bug Reports** | Found a bug? Let us know! |
| ✨ **Feature Requests** | Have an idea? We'd love to hear it! |
| 📖 **Documentation** | Typos, clarifications, examples |
| 🌍 **Translations** | Help translate to your language |
| 🧪 **Testing** | Write tests, report test failures |
| 💻 **Code** | Bug fixes, features, refactoring |

---

## How Can I Contribute?

### Reporting Bugs

**Security vulnerabilities:** Please report privately via [GitHub Security](https://github.com/cannatoshi/simplex-smp-monitor/security). See [SECURITY.md](SECURITY.md).

**Regular bugs:** Open an issue using the **Bug Report** template:

1. Use a clear and descriptive title
2. Describe the exact steps to reproduce
3. Describe the expected vs actual behavior
4. Include screenshots if applicable
5. Include your environment details (OS, Docker version, etc.)

### Suggesting Features

Open an issue using the **Feature Request** template:

1. Use a clear and descriptive title
2. Explain the problem this feature would solve
3. Describe the solution you'd like
4. Consider alternatives you've thought about
5. Add mockups or diagrams if helpful

### Your First Code Contribution

Not sure where to start? Look for issues labeled:

- `good first issue` - Good for newcomers
- `help wanted` - We'd appreciate help
- `documentation` - No code required

---

## Development Setup

For detailed setup instructions, see [DEVELOPMENT.md](DEVELOPMENT.md).

### Quick Start

```bash
# Clone the repository
git clone https://github.com/cannatoshi/simplex-smp-monitor.git
cd simplex-smp-monitor

# Option A: Docker (recommended)
docker compose up -d

# Option B: Manual setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install && cd ..
```

### Development Ports

| Service | Development | Production |
|---------|-------------|------------|
| React (Vite) | 3001 | - |
| Django | 8000 | - |
| Nginx | - | 8080 |

---

## Coding Standards

### Python (Backend)

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints where practical
- Maximum line length: 120 characters
- Use meaningful variable names

```python
# ✅ Good
def get_server_status(server_id: int) -> dict:
    """Fetch the current status of a server."""
    pass

# ❌ Bad
def get(id):
    pass
```

### TypeScript/React (Frontend)

- Use TypeScript for all new code
- Follow React best practices (functional components, hooks)
- Use Tailwind CSS for styling
- Keep components small and focused

```typescript
// ✅ Good
interface ServerProps {
  id: string;
  name: string;
  status: 'online' | 'offline';
}

const ServerCard: React.FC<ServerProps> = ({ id, name, status }) => {
  return <div className="p-4 rounded-lg">{name}</div>;
};

// ❌ Bad
const ServerCard = (props: any) => {
  return <div style={{padding: 16}}>{props.name}</div>;
};
```

### General Guidelines

- Write self-documenting code
- Add comments for complex logic
- Keep functions small and focused
- Don't repeat yourself (DRY)
- Write tests for new features

---

## Commit Message Format

We use **Conventional Commits** with emojis for clear, consistent history.

### Format

```
<type>(<scope>): <description> <emoji>

[optional body]

[optional footer]

Signed-off-by: Your Name <your@email.com>
```

### Types

| Type | Description | Emoji |
|------|-------------|-------|
| `feat` | New feature | ✨ |
| `fix` | Bug fix | 🐛 🔧 |
| `docs` | Documentation | 📖 📝 |
| `style` | Formatting (no code change) | 💅 🎨 |
| `refactor` | Code restructuring | 🔄 ♻️ |
| `test` | Adding tests | 🧪 ✅ |
| `chore` | Maintenance tasks | 🔨 🧹 |
| `ci` | CI/CD changes | 🤖 ⚙️ |
| `perf` | Performance improvement | ⚡ 🚀 |
| `security` | Security fix | 🔒 🛡️ |

### Scopes

| Scope | Description |
|-------|-------------|
| `frontend` | React/TypeScript frontend |
| `backend` | Django backend |
| `api` | REST API |
| `docker` | Docker/Compose |
| `nginx` | Nginx configuration |
| `readme` | README.md |
| `changelog` | CHANGELOG.md |
| `i18n` | Translations |
| `security` | Security-related |
| `ci` | GitHub Actions |

### Examples

```bash
# Feature
git commit -s -m "feat(api): Add server health endpoint ✨ 🏥"

# Bug fix
git commit -s -m "fix(frontend): Resolve dark mode toggle issue 🐛 🌙"

# Documentation
git commit -s -m "docs(readme): Update installation instructions 📖 ⬆️"

# Multiple changes (use body)
git commit -s -m "feat(docker): Add multi-arch support 🐳 🏗️" -m "
- Add ARM64 build support
- Update base images to Alpine 3.19
- Add health checks for all services
"
```

---

## Pull Request Process

### Before Submitting

1. ✅ Fork the repository
2. ✅ Create a feature branch (`git checkout -b feat/amazing-feature`)
3. ✅ Make your changes
4. ✅ Run tests locally
5. ✅ Sign your commits with DCO (`git commit -s`)
6. ✅ Push to your fork
7. ✅ Open a Pull Request

### PR Requirements

- [ ] Descriptive title using conventional commit format
- [ ] Linked to relevant issue (if applicable)
- [ ] All commits signed with DCO
- [ ] Tests pass
- [ ] Documentation updated (if needed)
- [ ] No merge conflicts

### Review Process

1. **Automated checks** run (linting, tests)
2. **Maintainer review** within 1-7 days
3. **Feedback** provided if changes needed
4. **Approval** and merge

### After Merge

- Delete your feature branch
- Celebrate! 🎉

---

## Developer Certificate of Origin (DCO)

We use the [Developer Certificate of Origin (DCO)](https://developercertificate.org/) to ensure all contributions can be legally distributed.

### What is DCO?

By signing off your commits, you certify that you wrote the code or have the right to submit it under our open-source license.

### How to Sign Off

Add `-s` flag to your commits:

```bash
git commit -s -m "feat(api): Add new endpoint ✨"
```

This adds a `Signed-off-by` line:

```
feat(api): Add new endpoint ✨

Signed-off-by: Your Name <your@email.com>
```

### Configure Git (One-Time Setup)

```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

### Forgot to Sign Off?

```bash
# Amend the last commit
git commit --amend -s --no-edit

# Sign off multiple commits (interactive rebase)
git rebase -i HEAD~3  # Last 3 commits
# Change 'pick' to 'edit', then for each:
git commit --amend -s --no-edit
git rebase --continue
```

### DCO Full Text

```
Developer Certificate of Origin
Version 1.1

Copyright (C) 2004, 2006 The Linux Foundation and its contributors.

Everyone is permitted to copy and distribute verbatim copies of this
license document, but changing it is not allowed.

Developer's Certificate of Origin 1.1

By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I
    have the right to submit it under the open source license
    indicated in the file; or

(b) The contribution is based upon previous work that, to the best
    of my knowledge, is covered under an appropriate open source
    license and I have the right under that license to submit that
    work with modifications, whether created in whole or in part
    by me, under the same open source license (unless I am
    permitted to submit under a different license), as indicated
    in the file; or

(c) The contribution was provided directly to me by some other
    person who certified (a), (b) or (c) and I have not modified
    it.

(d) I understand and agree that this project and the contribution
    are public and that a record of the contribution (including all
    personal information I submit with it, including my sign-off) is
    maintained indefinitely and may be redistributed consistent with
    this project or the open source license(s) involved.
```

---

## Community

### Getting Help

- 💬 [GitHub Discussions](https://github.com/cannatoshi/simplex-smp-monitor/discussions)
- 📖 [Documentation](https://github.com/cannatoshi/simplex-smp-monitor#readme)
- 🌐 [cannatoshi.com](https://cannatoshi.com) *(Coming Q2 2026)*

### Stay Updated

- ⭐ Star the repository
- 👁️ Watch for releases
- 📰 Check [CHANGELOG.md](CHANGELOG.md)

---

## Recognition

Contributors are recognized in:

- Release notes
- README.md contributors section (coming soon)
- Security Hall of Fame (for security researchers)

---

## License

By contributing, you agree that your contributions will be licensed under the [AGPL-3.0 License](LICENSE).

---

*Thank you for contributing to SimpleX SMP Monitor!* 💜

*Privacy is not a feature, it's a right.*