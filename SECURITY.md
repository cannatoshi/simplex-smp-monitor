# Security Policy

## Reporting a Vulnerability

**⚠️ Please do NOT report security vulnerabilities through public GitHub issues, discussions, or pull requests.**

### Preferred Method: GitHub Private Vulnerability Reporting

1. Go to the [Security tab](https://github.com/cannatoshi/simplex-smp-monitor/security)
2. Click **"Report a vulnerability"**
3. Fill out the form with details about the vulnerability

This is the fastest and most secure way to report issues.

### Alternative: Email

📧 **security@cannatoshi.com** *(Coming Q2 2026)*

Until email is available, please use GitHub Private Vulnerability Reporting exclusively.

---

## What to Include in Your Report

To help us understand and fix the issue quickly, please include:

- **Type of vulnerability** (e.g., SQL injection, XSS, authentication bypass)
- **Affected component** (e.g., API endpoint, Docker container, frontend)
- **Step-by-step reproduction** instructions
- **Proof of concept** (if available)
- **Impact assessment** (what could an attacker do?)
- **Your suggested fix** (if any)

---

## Response Timeline

| Phase | Timeframe |
|-------|-----------|
| Initial acknowledgment | Within 48 hours |
| Issue confirmation | Within 5 business days |
| Fix development | Based on severity |
| Public disclosure | After fix is released |

---

## Severity Classification

| Severity | Description | Response |
|----------|-------------|----------|
| **🔴 CRITICAL** | Remote code execution, authentication bypass, data breach | Immediate hotfix release |
| **🟠 HIGH** | Privilege escalation, significant data exposure | Priority fix in next release |
| **🟡 MEDIUM** | Limited impact, requires specific conditions | Scheduled fix |
| **🟢 LOW** | Minor issues, unlikely to be exploited | May be addressed in future updates |

---

## Disclosure Policy

We follow a **coordinated disclosure** approach:

1. **Day 0:** We receive your report and begin investigation
2. **Day 1-5:** We confirm the vulnerability and assess severity
3. **Day 6-30:** We develop and test a fix
4. **Day 31+:** We release the fix and publish a security advisory
5. **Day 45+:** Full details may be published (with your credit, if desired)

For **critical vulnerabilities**, we may accelerate this timeline.

---

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x (current) | ✅ Yes |
| < 0.1.0 | ❌ No |

---

## Safe Harbor

We consider security research conducted consistent with this policy to be:

- **Authorized** concerning any applicable anti-hacking laws
- **Authorized** concerning any relevant anti-circumvention laws
- **Exempt** from restrictions in our Terms of Service that would interfere with conducting security research

We will not pursue legal action against researchers who:

- Act in good faith
- Avoid privacy violations, data destruction, and service disruption
- Report vulnerabilities through the channels described above
- Allow reasonable time for fixes before public disclosure

---

## Recognition

We appreciate the security research community and will:

- Acknowledge your contribution in our security advisories (unless you prefer anonymity)
- Add you to our [Security Hall of Fame](#security-hall-of-fame) (coming soon)
- Provide a letter of acknowledgment upon request

---

## Security Hall of Fame

*No vulnerabilities reported yet. Be the first!*

---

## Questions?

For non-security questions, please use:
- 💬 [GitHub Discussions](https://github.com/cannatoshi/simplex-smp-monitor/discussions)
- 📖 [Documentation](https://github.com/cannatoshi/simplex-smp-monitor#readme)
- 🌐 [cannatoshi.com](https://cannatoshi.com) *(Coming Q2 2026)*

---

## Related Documents

- [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) - Community guidelines
- [LICENSE](LICENSE) - AGPL-3.0 License

---

*This security policy was last updated on January 1, 2026.*