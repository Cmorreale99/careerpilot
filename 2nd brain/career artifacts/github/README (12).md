# Embue — Secure IoT Data Architecture & Decentralized Integrity Layer

## Overview

Architected a secure data infrastructure prototype for IoT telemetry, separating encryption, storage, verification, and access control into a modular system design.

Built an end-to-end encrypted workflow using **GnuPG, IPFS, and Filecoin** to support tamper-evident storage, verifiable retrieval, and controlled decryption of sensor data.

**Impact: designed a scalable integrity layer for IoT data workflows where trust, auditability, and modularity are core system requirements.**

---

## Key Contributions

- Architected a **secure IoT data pipeline** separating encryption, decentralized storage, verification, and access control  
- Implemented **end-to-end encryption** using GnuPG before data entered the storage layer  
- Stored encrypted telemetry using **IPFS**, enabling content-addressed retrieval and tamper-evident data references  
- Integrated **Filecoin-based verification** to support persistence guarantees and data integrity checks  
- Evaluated decentralized storage options including **Filecoin, Storj, Skynet, IPFS, and Web3.Storage**  
- Designed a hybrid architecture using **IPFS for off-chain storage** and **Filecoin for verification/persistence**  
- Validated retrieval and controlled decryption workflows across decentralized storage infrastructure  
- Documented system tradeoffs around scalability, integrity, performance, cost, and operational complexity  

---

## Business Impact

- Created a secure architecture for IoT telemetry workflows requiring **verifiable data integrity**  
- Reduced reliance on centralized storage assumptions by using **content-addressed data references**  
- Improved auditability by making stored data tamper-evident and independently retrievable  
- Separated system responsibilities into modular layers, improving maintainability and extensibility  
- Demonstrated how decentralized infrastructure can support secure data pipelines beyond blockchain-native use cases  

---

## Tech Stack

- **Encryption:** GnuPG  
- **Storage:** IPFS, Web3.Storage  
- **Verification/Persistence:** Filecoin  
- **Architecture:** Hybrid on-chain/off-chain design  
- **Focus Areas:** Secure data architecture, decentralized storage, IoT telemetry, data integrity, access control  

---

## Paper

📄 [Co-Authored Paper](../research/decentralized-iot-architecture.pdf.pdf)

---

## Deep Dive

➡️ [Read Full Technical Writeup](./technical-writeup.md)

---

## Navigation

⬅️ [Back to Portfolio Home](../README.md)
