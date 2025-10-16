# Quick Start Guide

## Build Commands

### Build everything (recommended)
```bash
python3 scripts/build_dist.py --product all --version v1.2.3
```

### Build specific product
```bash
# General data
python3 scripts/build_dist.py --product general --version v1.2.3

# Wallet app
python3 scripts/build_dist.py --product wallet-app --version v1.2.3
```

### Build for staging
```bash
python3 scripts/build_dist.py --product all --version v1.2.3-rc.1 --environment staging
```

## Directory Layout

```
data/                           # Shared data (all apps)
products/wallet-app/            # Wallet-specific data
├── data/                       # Simple configs (JSON, XML)
└── dapps/                      # Complex features (with subfolders)
```

## Adding Data Files

### Simple files → use /data/
```bash
products/wallet-app/data/settings.json
products/wallet-app/data/config.xml
```

### Complex features → create feature folder
```bash
products/wallet-app/dapps/dapps.json
products/wallet-app/dapps/locales/en.json
products/wallet-app/dapps/locales/es.json
```

## Version Checking

Apps should fetch `version.json` to check for updates:

```javascript
const response = await fetch('https://static.qubic.org/v1/wallet-app/version.json');
const { version, files } = await response.json();

// Compare file hashes to detect changes
if (cachedHash !== files['dapps/dapps.json'].hash) {
  // Download updated file
}
```

## URLs

### Production
- General: `https://static.qubic.org/v1/general/data/`
- Wallet: `https://static.qubic.org/v1/wallet-app/`

### Staging
- General: `https://static.qubic.org/staging/v1/general/data/`
- Wallet: `https://static.qubic.org/staging/v1/wallet-app/`

## Output Structure

```
dist/
└── v1/
    ├── general/data/
    │   ├── smart_contracts.json
    │   ├── smart_contracts.min.json
    │   ├── bundle.json
    │   └── version.json            # ← Cache invalidation
    └── wallet-app/
        ├── dapps/
        │   ├── dapps.json
        │   └── locales/...
        ├── bundle.json
        └── version.json              # ← Cache invalidation
```

## Key Points

1. **All products get same version number** (e.g., v1.2.3)
2. **File hashes detect actual changes** (cache invalidation)
3. **JSON files auto-minified** (.min.json created)
4. **Non-JSON files copied as-is** (XML, images, etc.)
5. **Industry standard pattern** (monorepo + hash-based caching)

## See Also

- [CLAUDE.md](CLAUDE.md) - Complete documentation
- [products/README.md](products/README.md) - Product structure guide
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Technical details
