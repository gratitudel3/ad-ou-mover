# Active Directory OU Mover

CLI tool for moving Active Directory objects between Organizational Units(OU) using LDAP (modifyDN), supporting password and Kerberos authentication.

---

## Features

- Move users and other directory objects between OUs
- LDAP modifyDN support
- Password-based authentication
- Kerberos authentication (`-k --no-pass`)
- Lightweight and dependency minimal
- Simple CLI interface

---
## Requirements

- Python 3.9+
- LDAP connectivity to Domain Controller
- Valid Active Directory credentials or Kerberos ticket

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/active-directory-ou-mover.git
cd active-directory-ou-mover
```

## Usage

### Password Authentication

```bash
python3 ou_mover.py \
  --dc-ip 10.10.10.10 \
  --domain lab.local \
  --user john.doe \
  --password 'Password123!' \
  move \
  --user-dn "CN=John Doe,OU=Junior DevOps,DC=lab,DC=local" \
  --target-ou "OU=Senior DevOps,DC=lab,DC=local"
```

---

### Kerberos Authentication

```bash
export KRB5CCNAME=john.doe.ccache

python3 ou_mover.py \
  --dc-host dc.lab.local \
  --domain lab.local \
  --user john.doe \
  -k --no-pass \
  move \
  --user-dn "CN=John Doe,OU=Junior DevOps,DC=lab,DC=local" \
  --target-ou "OU=Senior DevOps,DC=lab,DC=local"
```

---

## Required Permissions
To move an object between Organizational Units, the authenticated user must have appropriate permissions in Active Directory.

Common permissions that allow this operation include:
- `GenericAll` (on both source and destination OUs)
- `GenericWrite` (on the object or OUs)
- `WriteProperty` (on the object)
- `Create Child` permission on the destination OU (to add the object)

In delegated environments, permissions are often granted at the OU level.
Insufficient permissions may result in LDAP operation failures even if authentication succeeds.

## Arguments

| Argument | Description |
|----------|-------------|
| `--dc-ip` | Domain Controller IP |
| `--dc-host` | Domain Controller hostname/FQDN |
| `--domain` | Active Directory domain |
| `--user` | Username |
| `--password` | Password authentication |
| `-k` | Enable Kerberos authentication |
| `--no-pass` | Use Kerberos ticket cache only |

---

## Commands

### move

Move an object between Organizational Units.

| Argument | Description |
|----------|-------------|
| `--user-dn` | Distinguished Name of target object |
| `--target-ou` | Destination OU |
| `--new-cn` | Optional CN rename during move |

---

## Example Output

```text
[*] LDAP auth via password
[+] Moved user 'John Doe'
[+] From: CN=John Doe,OU=Junior DevOps,DC=lab,DC=local
[+] To:   OU=Senior DevOps,DC=lab,DC=local
```

---

## Notes

- Kerberos authentication requires a valid ticket in `KRB5CCNAME`
- Ensure DNS and `/etc/krb5.conf` are configured properly for Kerberos
- LDAP signing or hardened environments may require LDAPS support

---

## Disclaimer

This tool is intended for authorized environments, security research, and lab usage only.
