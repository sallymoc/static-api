# URL Structure Reference

## Overview

All files are served from `static.qubic.org` with environment-based paths.

## Environment Paths

- **Production**: `/v1/` - Stable, tested releases
- **Staging**: `/staging/v1/` - Release candidates for testing
- **Dev**: `/dev/v1/` - Development builds

**Future API versions** (v2, v3, etc.) will be supported across all environments:
- Production: `/v2/`, `/v3/`
- Staging: `/staging/v2/`, `/staging/v3/`
- Dev: `/dev/v2/`, `/dev/v3/`

## URL Format

**Production:**
```
https://static.qubic.org/v1/{product}/{path-to-file}
```

**Staging/Dev:**
```
https://static.qubic.org/{environment}/v1/{product}/{path-to-file}
```

## Examples

### General Data (Shared)

**Production:**
```
https://static.qubic.org/v1/general/data/smart_contracts.json
https://static.qubic.org/v1/general/data/exchanges.json
https://static.qubic.org/v1/general/data/tokens.json
https://static.qubic.org/v1/general/data/address_labels.json
https://static.qubic.org/v1/general/data/version.json
```

**Staging:**
```
https://static.qubic.org/staging/v1/general/data/smart_contracts.json
https://static.qubic.org/staging/v1/general/data/version.json
```

**Dev:**
```
https://static.qubic.org/dev/v1/general/data/smart_contracts.json
https://static.qubic.org/dev/v1/general/data/version.json
```

### Wallet App

**Production:**
```
https://static.qubic.org/v1/wallet-app/dapps/dapps.json
https://static.qubic.org/v1/wallet-app/dapps/locales/en.json
https://static.qubic.org/v1/wallet-app/dapps/locales/es.json
https://static.qubic.org/v1/wallet-app/version.json
```

**Staging:**
```
https://static.qubic.org/staging/v1/wallet-app/dapps/dapps.json
https://static.qubic.org/staging/v1/wallet-app/dapps/locales/en.json
https://static.qubic.org/staging/v1/wallet-app/version.json
```

**Dev:**
```
https://static.qubic.org/dev/v1/wallet-app/dapps/dapps.json
https://static.qubic.org/dev/v1/wallet-app/version.json
```

## Minified Files

All JSON files have minified versions:
```
https://static.qubic.org/v1/general/data/smart_contracts.min.json
https://static.qubic.org/v1/wallet-app/dapps/dapps.min.json
```

## Bundle Files

Each product has a bundle containing all JSON merged:
```
https://static.qubic.org/v1/general/data/bundle.json
https://static.qubic.org/v1/general/data/bundle.min.json
https://static.qubic.org/v1/wallet-app/bundle.json
https://static.qubic.org/v1/wallet-app/bundle.min.json
```

## Version Tracking

Check for updates with version.json:
```javascript
// Production
const prod = await fetch('https://static.qubic.org/v1/wallet-app/version.json')
  .then(r => r.json());

// Staging (for testing)
const staging = await fetch('https://static.qubic.org/staging/v1/wallet-app/version.json')
  .then(r => r.json());

// Compare file hashes
if (prod.files['dapps/dapps.json'].hash !== cachedHash) {
  // Download updated file
  await fetch('https://static.qubic.org/v1/wallet-app/dapps/dapps.json');
}
```

## Build Output Structure

```
dist/
├── v1/                          # Production
│   ├── general/data/
│   │   ├── *.json
│   │   └── version.json
│   └── wallet-app/
│       ├── dapps/
│       └── version.json
├── staging/                     # Staging
│   └── v1/
│       ├── general/data/
│       └── wallet-app/
└── dev/                         # Development
    └── v1/
        ├── general/data/
        └── wallet-app/
```

## FTP Deployment

Deploy `dist/` contents directly to domain root:

```bash
# Production
dist/v1/*          → ftp://static.qubic.org/v1/*

# Staging
dist/staging/v1/*  → ftp://static.qubic.org/staging/v1/*

# Dev
dist/dev/v1/*      → ftp://static.qubic.org/dev/v1/*
```

## Build Commands

```bash
# Production
python3 scripts/build_dist.py --product all --version v1.2.3 --environment production

# Staging
python3 scripts/build_dist.py --product all --version v1.2.3-rc.1 --environment staging

# Dev
python3 scripts/build_dist.py --product all --version v1.2.3-dev --environment dev
```

## Benefits

1. **No subdomains needed** - All environments on same domain
2. **Clear separation** - `/v1/` vs `/staging/` vs `/dev/`
3. **Easy testing** - Swap `/v1/` with `/staging/` in URLs
4. **Simple DNS** - Only need `static.qubic.org`
5. **CDN friendly** - Can set different cache rules per path
