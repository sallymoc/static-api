# Qubic Static API

This repository provides static data and assets related to Qubic blockchain. It serves as a single, reliable source of structured data for developers, explorers, wallets, dashboards, and analysis tools.

## Data Categories

### General Data (Shared)
Available at: **https://static.qubic.org/v1/general/data/**

- **Smart contracts** — names, indexes, procedures, GitHub source links, and addresses
- **Exchanges** — known trading platforms and their Qubic addresses
- **Tokens** — additional token information
- **Address labels** — relevant Qubic addresses

### Product-Specific Data

**Wallet App**
Available at: **https://static.qubic.org/v1/wallet-app/**

- DApp explorer data with multilingual support
- Mobile wallet configuration files
- Localization files (EN, DE, ES, FR, RU, TR, ZH)

## Available Files

### General Data Files
Base URL: `https://static.qubic.org/v1/general/data/`

- **Smart Contracts**
  - [smart_contracts.json](https://static.qubic.org/v1/general/data/smart_contracts.json)
  - [smart_contracts.min.json](https://static.qubic.org/v1/general/data/smart_contracts.min.json)

- **Exchanges**
  - [exchanges.json](https://static.qubic.org/v1/general/data/exchanges.json)
  - [exchanges.min.json](https://static.qubic.org/v1/general/data/exchanges.min.json)

- **Tokens**
  - [tokens.json](https://static.qubic.org/v1/general/data/tokens.json)
  - [tokens.min.json](https://static.qubic.org/v1/general/data/tokens.min.json)

- **Address Labels**
  - [address_labels.json](https://static.qubic.org/v1/general/data/address_labels.json)
  - [address_labels.min.json](https://static.qubic.org/v1/general/data/address_labels.min.json)

- **Bundle (All files combined)**
  - [bundle.json](https://static.qubic.org/v1/general/data/bundle.json)
  - [bundle.min.json](https://static.qubic.org/v1/general/data/bundle.min.json)

- **Version Tracking**
  - [version.json](https://static.qubic.org/v1/general/data/version.json) - Contains file hashes and sizes for cache invalidation

### Wallet App Files
Base URL: `https://static.qubic.org/v1/wallet-app/`

- **DApps**
  - [dapps/dapps.json](https://static.qubic.org/v1/wallet-app/dapps/dapps.json)
  - Locales: `dapps/locales/{lang}.json` (en, de, es, fr, ru, tr, zh)  

## Environments

This repository supports three deployment environments:

- **Production**: `https://static.qubic.org/` - Stable releases (e.g., v1.2.3)
- **Staging**: `https://static.qubic.org/staging/` - Release candidates (e.g., v1.2.3-rc.1)
- **Dev**: `https://static.qubic.org/dev/` - Development testing

## Repository Structure

```
data/                              # General/shared source data
  ├── smart_contracts.json
  ├── exchanges.json
  ├── tokens.json
  └── address_labels.json

products/                          # Product-specific source data
  └── wallet-app/
      └── dapps/
          ├── dapps.json
          └── locales/

scripts/                           # Build and update utilities
  ├── build_dist.py               # Build distribution files
  └── update_smart_contracts.py   # Update SC data from GitHub

.github/workflows/                 # CI/CD automation
  ├── commitlint.yml              # Commit message validation
  ├── lint-pr.yml                 # PR title validation
  └── deploy.yml                  # Automated deployments
```

## CI/CD & Releases

This repository uses GitHub Actions with semantic-release for automated versioning and deployments.

### Commit Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New features (triggers MINOR version bump)
- `fix:` - Bug fixes (triggers PATCH version bump)
- `docs:` - Documentation changes (no version bump)
- `chore:` - Maintenance tasks (no version bump)

**Examples:**
```
feat: add proposalUrl field to smart contracts
fix: correct address calculation for contract index 166
docs: update README with new structure
```

### Deployment Workflow

1. **Dev** - Push to `dev` branch → deploys to dev environment (no versioning)
2. **Staging** - Push to `staging` branch → creates RC tag & GitHub pre-release → deploys to staging
3. **Production** - Push to `main` branch → creates version tag & GitHub release → deploys to production

### Building Locally

Build distribution files for all products:
```bash
python3 scripts/build_dist.py --product all --version v1.2.3
```

Update smart contracts from Qubic core repository:
```bash
python3 scripts/update_smart_contracts.py
```

## How to Contribute

Contributions are welcome:

- **General data** (exchanges, tokens, address labels) - Submit Pull Requests with new entries
- **Product-specific data** - Submit PRs to `products/{product-name}/` with updates
- **Smart contracts** - Data is auto-generated. Open Issues for corrections rather than PRs
- **New products** - Create folder under `products/` and submit PR

See [products/README.md](products/README.md) for detailed structure guidelines.  