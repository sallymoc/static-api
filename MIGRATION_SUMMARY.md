# Migration Summary: dapps-explorer → static-api

## What Was Migrated

Successfully migrated all data from [qubic/dapps-explorer](https://github.com/qubic/dapps-explorer) main branch to this repository.

### Files Migrated

✅ **DApp Data**
- `dapps.json` → `products/wallet-app/dapps/dapps.json`
  - 7 dApps (Explorer, Proposals, Community Voting, QEarn, QXBoard, QXTrade, QX)
  - 2 featured top apps (Explorer, Proposals)

✅ **Localization Files**
All 7 language files migrated to `products/wallet-app/dapps/locales/`:
- ✅ `en.json` - English
- ✅ `es.json` - Spanish
- ✅ `de.json` - German
- ✅ `fr.json` - French
- ✅ `ru.json` - Russian
- ✅ `tr.json` - Turkish
- ✅ `zh.json` - Chinese

### Source Repository

- **Original**: https://github.com/qubic/dapps-explorer
- **Branch**: main
- **Date Migrated**: October 16, 2025

### New Structure

```
products/wallet-app/
└── dapps/
    ├── dapps.json              # Main DApp catalog
    └── locales/                # i18n translations
        ├── en.json
        ├── es.json
        ├── de.json
        ├── fr.json
        ├── ru.json
        ├── tr.json
        └── zh.json
```

### DApps Included

1. **Qubic Explorer** - Blockchain explorer
2. **Proposals (Quorum Voting)** - Governance proposals
3. **Community Voting** - Community polls and voting
4. **QEarn** - Staking rewards platform
5. **QXBoard** - QX exchange UI
6. **QXTrade** - QX trading interface
7. **QX** - Decentralized exchange

### Build Output

After migration, running the build generates:

```
dist/v1/wallet-app/
├── dapps/
│   ├── dapps.json              # 1.7 KB
│   ├── dapps.min.json          # Minified
│   └── locales/
│       ├── en.json             # 1.1 KB
│       ├── en.min.json
│       ├── es.json             # 1.2 KB
│       ├── es.min.json
│       ├── de.json             # 1.2 KB
│       ├── de.min.json
│       ├── fr.json             # 1.2 KB
│       ├── fr.min.json
│       ├── ru.json             # 1.5 KB
│       ├── ru.min.json
│       ├── tr.json             # 1.2 KB
│       ├── tr.min.json
│       ├── zh.json             # 1.1 KB
│       └── zh.min.json
├── bundle.json                 # All data merged
├── bundle.min.json
└── version.json                # With file hashes
```

### Deployment URLs

Once deployed, files will be accessible at:

**Production:**
- Main catalog: `https://static.qubic.org/v1/wallet-app/dapps/dapps.json`
- English: `https://static.qubic.org/v1/wallet-app/dapps/locales/en.json`
- Spanish: `https://static.qubic.org/v1/wallet-app/dapps/locales/es.json`
- etc.

**Staging:**
- Main catalog: `https://static.qubic.org/staging/v1/wallet-app/dapps/dapps.json`
- etc.

### Version Tracking

`version.json` includes hashes for all files:
```json
{
  "version": "v1.0.0",
  "environment": "production",
  "files": {
    "dapps/dapps.json": {
      "hash": "sha256:74703103...",
      "size": 1739
    },
    "dapps/locales/en.json": {
      "hash": "sha256:7aceaa30...",
      "size": 1069
    },
    ...
  }
}
```

### Next Steps

1. ✅ Files migrated from dapps-explorer
2. ✅ Build script tested and working
3. ⏳ Deploy to staging environment
4. ⏳ Update wallet app to use new URLs
5. ⏳ Deploy to production
6. ⏳ Archive or deprecate dapps-explorer repository

### Notes

- All data migrated exactly as-is from source repository
- Example config files (settings.json, config.xml) removed
- Only real DApp data remains
- Ready for deployment

### Testing

```bash
# Build wallet app
python3 scripts/build_dist.py --product wallet-app --version v1.0.0

# Build everything
python3 scripts/build_dist.py --product all --version v1.0.0

# Check output
ls -lh dist/wallet-app/v1/dapps/
cat dist/wallet-app/v1/version.json
```

## Migration Verification

- ✅ All 7 locale files present
- ✅ dapps.json contains all 7 dApps
- ✅ File structure matches original repository
- ✅ Build process completes successfully
- ✅ version.json generated with correct hashes
- ✅ Minified versions created for all JSON files
