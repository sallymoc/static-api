# Implementation Summary

This document summarizes the changes made to support product-specific data and cache invalidation.

## What Was Implemented

### 1. Cache Invalidation System
- Added `version.json` generation to build script
- Each file gets SHA-256 hash and size metadata
- Apps can compare hashes to detect changes without downloading full files
- Works across all file types (JSON, XML, etc.)

### 2. Product-Specific Structure
- Created `products/` directory for product-specific data
- General shared data remains in `data/`
- Each product can have feature-based subfolders
- Flexible organization: simple files in `/data/`, complex features in dedicated folders

### 3. Multi-Product Build System
- Updated `build_dist.py` to support `--product` argument
- Can build individual products or all at once
- Each product gets independent output directory
- All products share same version number (monorepo pattern)

## Directory Structure

```
├── data/                              # General/shared data
│   ├── smart_contracts.json
│   ├── exchanges.json
│   ├── tokens.json
│   └── address_labels.json
│
├── products/                          # Product-specific data
│   └── wallet-app/
│       ├── data/                      # Simple config files
│       │   ├── settings.json
│       │   └── config.xml
│       └── dapps/                     # Complex feature
│           ├── dapps.json
│           └── locales/
│               ├── en.json
│               └── es.json
│
└── dist/                              # Build output
    └── v1/
        ├── general/data/
        │   ├── smart_contracts.json
        │   ├── smart_contracts.min.json
        │   ├── bundle.json
        │   ├── bundle.min.json
        │   └── version.json           # With file hashes
        │
        └── wallet-app/
            ├── dapps/
            │   ├── dapps.json
            │   ├── dapps.min.json
            │   └── locales/...
            ├── bundle.json
            ├── bundle.min.json
            └── version.json            # With file hashes
```

## Build Commands

### Build Everything
```bash
python3 scripts/build_dist.py --product all --version v1.2.3
```

### Build Specific Product
```bash
# General data only
python3 scripts/build_dist.py --product general --version v1.2.3

# Wallet app only
python3 scripts/build_dist.py --product wallet-app --version v1.2.3
```

### Staging Environment
```bash
python3 scripts/build_dist.py --product all --version v1.2.3-rc.1 --environment staging
```

## version.json Format

Each product gets a `version.json` file:

```json
{
  "version": "v1.2.3",
  "environment": "production",
  "generated_at": "2025-10-16T22:00:00Z",
  "files": {
    "data/settings.json": {
      "hash": "sha256:abc123...",
      "size": 1234
    },
    "data/config.xml": {
      "hash": "sha256:def456...",
      "size": 567
    },
    "dapps/dapps.json": {
      "hash": "sha256:ghi789...",
      "size": 890
    }
  }
}
```

## Client Usage Pattern

Apps can efficiently check for updates:

```javascript
// 1. Fetch version.json (small, fast)
const versionData = await fetch('https://static.qubic.org/v1/wallet-app/version.json')
  .then(r => r.json());

// 2. Compare file hashes with cached versions
const cachedHashes = localStorage.getItem('file-hashes');

for (const [filename, metadata] of Object.entries(versionData.files)) {
  if (cachedHashes[filename] !== metadata.hash) {
    // Hash changed → download new file
    await downloadFile(filename);
  }
  // else: use cached version
}

// 3. Update cached hashes
localStorage.setItem('file-hashes', JSON.stringify(versionData.files));
```

## Key Benefits

1. **Efficient Updates**: Apps only download changed files
2. **Scalable**: Easy to add new products
3. **Flexible**: Supports any file type (JSON, XML, images, etc.)
4. **Simple Versioning**: Single version number, but granular change detection
5. **Independent Deployment**: Can deploy specific products if needed
6. **Cache-Friendly**: File hashes enable proper cache invalidation

## Deployment URLs

### Production
- General: `https://static.qubic.org/v1/general/data/`
- Wallet App: `https://static.qubic.org/v1/wallet-app/`

### Staging
- General: `https://static.qubic.org/staging/v1/general/data/`
- Wallet App: `https://static.qubic.org/staging/v1/wallet-app/`

## Version Strategy

- **Monorepo approach**: Single version number for all products
- **Same version**: All products get v1.2.3 even if only one changed
- **Hash-based invalidation**: File hashes tell what actually changed
- **Industry standard**: Matches patterns used by CDNs, npm, Bootstrap CDN, etc.

## Adding New Products

1. Create folder: `products/{product-name}/`
2. Add data files and subfolders as needed
3. Build script auto-discovers new products
4. Deploy to: `static.qubic.org/{product-name}/v1/`

## Files Modified

- `scripts/build_dist.py` - Complete rewrite with product support
- `CLAUDE.md` - Updated documentation
- `products/README.md` - Created product structure guide

## Files Created

- `products/wallet-app/data/settings.json` - Example config
- `products/wallet-app/data/config.xml` - Example XML config
- `products/wallet-app/dapps/dapps.json` - DApp list
- `products/wallet-app/dapps/locales/en.json` - English translations
- `products/wallet-app/dapps/locales/es.json` - Spanish translations

## Next Steps

1. Migrate actual data from dapps-explorer repository
2. Update CI/CD workflows to use `--product all`
3. Update client apps to use version.json for cache invalidation
4. Test staging deployment
5. Deploy to production

## Testing

All build scenarios tested successfully:
- ✅ Build general product only
- ✅ Build wallet-app product only
- ✅ Build all products together
- ✅ version.json includes all files with hashes
- ✅ XML and other non-JSON files handled correctly
- ✅ Folder structure preserved in output
