# Products Directory

This directory contains product-specific data and assets that are deployed separately from the general shared data.

## Structure

```
products/
└── {product-name}/
    ├── data/              # Simple, flat configuration files
    │   ├── *.json        # JSON configs (auto-minified during build)
    │   ├── *.xml         # XML configs (copied as-is)
    │   └── ...
    └── {feature-name}/    # Complex features with multiple related files
        ├── *.json
        └── subfolder/
            └── ...
```

## Current Products

### wallet-app
Mobile wallet application data including:
- `/data/` - App settings and configuration files
- `/dapps/` - DApp explorer data and localization files

## Adding a New Product

1. Create a folder: `products/{product-name}/`
2. Add your data files (JSON, XML, or any format)
3. Organize complex features into subfolders
4. Build with: `python3 scripts/build_dist.py --product {product-name} --version v1.0.0`

## Build & Deployment

Build a specific product:
```bash
python3 scripts/build_dist.py --product wallet-app --version v1.2.3
```

Build all products:
```bash
python3 scripts/build_dist.py --product all --version v1.2.3
```

Each product is deployed to:
- Production: `static.qubic.org/{product-name}/v1/`
- Staging: `static.qubic.org/{product-name}/staging/v1/`

## Guidelines

**Use `/data/` for:**
- Single configuration files
- Simple data that doesn't need subfolders
- Standalone resources

**Create feature folders for:**
- Multiple related files (e.g., data + translations)
- Features with their own structure
- Logical units that should be grouped together

## Version Tracking

Each product gets its own `version.json` with:
- Same version number across all products (monorepo versioning)
- Individual file hashes for cache invalidation
- File sizes for all resources

Example: `dist/wallet-app/v1/version.json`
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
    }
  }
}
```
