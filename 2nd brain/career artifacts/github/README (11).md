# BoardGameGeek — Async Data Pipeline & Relational Marketplace Model

## Overview

I Built a data engineering pipeline for BoardGameGeek marketplace and metadata workflows, transforming heterogeneous API data into structured, queryable datasets for downstream application use.

Replaced sequential API ingestion with a rate-limit-aware asynchronous ELT pipeline, improving throughput while preserving reliability under constrained external endpoints.

**Impact: ~2× ingestion throughput across ~150 entities, with structured relational outputs supporting marketplace, ratings, and application workflows.**

---

## Key Contributions

- Built an **asynchronous Python ingestion pipeline** using `aiohttp` to collect BoardGameGeek marketplace, ratings, and metadata records  
- Replaced sequential API calls with **bounded concurrency**, improving ingestion throughput by approximately **2×**  
- Implemented **rate-limit handling**, retry logic, exponential backoff, and batch pacing to maintain reliability under API constraints  
- Cleaned, normalized, and validated heterogeneous data from multiple API sources  
- Integrated pricing, ratings, and metadata into structured datasets for downstream querying  
- Designed a **recursive relational model** to represent board game relationships such as expansions, reimplementations, and parent-child entity mappings  
- Built application-layer integrations connecting backend data workflows to frontend marketplace functionality  
- Implemented AWS Lambda logic for transactional account balance updates and checkout-related workflows  

---

## Business Impact

- Improved data ingestion speed and reliability for API-driven marketplace and ratings data  
- Converted fragmented external data sources into structured, queryable datasets  
- Supported marketplace workflows by integrating pricing, metadata, and ratings data into a coherent backend model  
- Improved data integrity through validation, normalization, and schema alignment  
- Enabled application-layer functionality by connecting backend data pipelines with frontend checkout and transactional flows  
- Demonstrated end-to-end data engineering across ingestion, transformation, modeling, backend logic, and user-facing application behavior  

---

## Tech Stack

- **Python:** `aiohttp`, async ingestion, data processing  
- **Data Engineering:** ELT, API ingestion, rate-limit handling, retries, exponential backoff  
- **Backend / Cloud:** AWS Lambda  
- **Frontend:** React, TypeScript  
- **Data Modeling:** Recursive relational modeling, entity relationships, parent-child mappings  
- **Focus Areas:** Async pipelines, API integration, data normalization, marketplace data systems, full-stack data workflows  

---

## Deep Dive

➡️ [Read Full Technical Writeup](./technical-writeup.md)

---

## Navigation

⬅️ [Back to Portfolio Home](../README.md)
