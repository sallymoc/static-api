# Qubic Static

This repository provides static data related to Qubic.

It makes available information that is not directly accessible through the blockchain APIs, including:

- **Smart contracts** — names, indexes, procedures, GitHub source links, and addresses  
- **Exchanges** — known trading platforms and their Qubic addresses  
- **Tokens** — Additional tokens information  
- **Address labels** — Relevant Qubic addresses  
- **Images** *(planned)* — Logos and icons (e.g., network logos, token logos) for use in explorers, wallets, dashboards, and analysis tools  

👉 **https://static.qubic.org/general/data/v1**

### Available files (`general/data/v1/`)

- [smart_contracts.json](https://static.qubic.org/general/data/v1/smart_contracts.json)  
- [smart_contracts.min.json](https://static.qubic.org/general/data/v1/smart_contracts.min.json)  

- [exchanges.json](https://static.qubic.org/general/data/v1/exchanges.json)  
- [exchanges.min.json](https://static.qubic.org/general/data/v1/exchanges.min.json)  

- [tokens.json](https://static.qubic.org/general/data/v1/tokens.json)  
- [tokens.min.json](https://static.qubic.org/general/data/v1/tokens.min.json)  

- [address_labels.json](https://static.qubic.org/general/data/v1/address_labels.json)  
- [address_labels.min.json](https://static.qubic.org/general/data/v1/address_labels.min.json)  

- [bundle.json](https://static.qubic.org/general/data/v1/bundle.json)  
- [bundle.min.json](https://static.qubic.org/general/data/v1/bundle.min.json)  

### Folder structure

- `general/` — Shared resources that can be used across different types of products.  
  - `data/` — Current JSON data files.  
  - `images/` *(planned, does not exist yet)* — Will contain visual resources such as logos and icons.  

In the future, additional top-level folders may be added for product-specific resources if needed.  

### Purpose
The goal is to provide a single, reliable source of structured JSON data and, in the future, images for developers, explorers, wallets, dashboards, and analysis tools.

### How to Contribute

Updates are welcome:

- **Exchanges, tokens, address labels** — Open a Pull Request with the new values or entries.  
- **Smart contracts** — Data is mainly auto-generated from the core source. If you notice something that needs correction, open an Issue instead of a PR.  