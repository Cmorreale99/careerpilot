# BoardGameGeek — Async Data Pipeline & Relational Marketplace Model

## Overview

For the BoardGameGeek project, I contributed to a full-stack web application that allowed users to browse board games, manage collections, and purchase games through a simulated marketplace.

My work focused on the data ingestion layer, relational preprocessing logic, backend account-funding functionality, and React checkout workflow. I built an asynchronous Python pipeline to collect and standardize external BoardGameGeek marketplace data, integrated pricing data with metadata and ratings, generated recursive relationship mappings for board game reimplementations, implemented an AWS Lambda backend function for account funds, and developed the frontend checkout flow.

The result was an end-to-end contribution across data engineering and application workflow:

**External API data → async ingestion → preprocessing → relational datasets → backend account updates → React checkout workflow**

---

## System Overview

<img width="750" height="500" alt="architecture" src="../assets/images/bgg_pipeline_architecture.png" />

*Built an asynchronous ingestion and preprocessing pipeline for BoardGameGeek marketplace data, integrated external datasets into relational outputs, and connected backend transaction logic to a React checkout workflow.*

---

## Technical Problem

The application needed structured board game data to support browsing, marketplace behavior, collection management, and simulated purchasing. However, the required data came from heterogeneous sources with inconsistent formats and external API constraints.

The core data challenges included:

* Marketplace pricing data had to be collected from external endpoints
* API requests needed to respect rate limits and recover from transient failures
* Pricing, ratings, and metadata datasets used different formats and schema conventions
* Merged datasets required cleaning, normalization, and validation before database ingestion
* Ranking fields became inconsistent after dataset integration and needed reindexing
* Board game relationships such as reimplementations could not be accurately represented with a simple boolean field
* Frontend checkout behavior needed to remain consistent with backend account and transaction state

The problem was not only collecting data. The challenge was building a pipeline that could reliably ingest constrained external data, standardize it for relational storage, and connect it to application workflows.

---

## Environment & Constraints

* **Data Source:** BoardGameGeek marketplace, ratings, and metadata data
* **Ingestion:** Python asynchronous API requests using `aiohttp`
* **Data Scope:** Approximately 150 board games
* **Pipeline Type:** External API ingestion, preprocessing, enrichment, normalization, and export
* **Backend:** AWS Lambda for account-funding updates
* **Frontend:** React checkout workflow
* **State Management:** Browser local storage for cart persistence
* **Database Target:** Relational database ingestion
* **Primary Constraints:** API rate limits, heterogeneous source schemas, missing values, inconsistent ranking fields, recursive game relationships, and synchronization between frontend cart state and backend account data

---

## My Role

* Built an asynchronous Python ingestion pipeline using `aiohttp`
* Collected live marketplace pricing data for approximately 150 board games
* Implemented rate-limit handling, retry logic, and progress tracking for reliable ingestion
* Integrated pricing data with board game metadata and ratings datasets
* Cleaned, normalized, and validated records before relational database ingestion
* Reindexed ranking fields after dataset merges to preserve consistent ranking behavior
* Updated preprocessing logic to support recursive relationships between board games
* Generated parent-child relationship mappings for game reimplementations
* Implemented an AWS Lambda backend function for recording user account funds
* Developed the React checkout page for cart management, balance validation, and transaction submission
* Connected frontend checkout behavior to backend APIs and persisted cart state through local storage

---

## Asynchronous Data Ingestion

A key component of the project was a three-stage asynchronous data processing pipeline for collecting and standardizing BoardGameGeek data.

The ingestion layer was implemented in Python using the `aiohttp` asynchronous HTTP client. This allowed the pipeline to issue concurrent requests to external endpoints instead of processing requests sequentially.

The ingestion workflow collected live marketplace pricing data for approximately 150 board games. Because the upstream endpoints enforced request limits, the pipeline included several mechanisms to maintain reliability:

* Asynchronous request handling for concurrent network calls
* Rate-limit handling to remain within external API constraints
* Retry logic to recover from transient failures
* Progress tracking to monitor ingestion completion

The asynchronous design improved ingestion throughput compared to synchronous request processing while preserving control over external API behavior.

The output of this stage was a marketplace pricing dataset ready for enrichment and integration with additional board game data.

---

## Data Enrichment & Dataset Integration

After pricing data was collected, the pipeline integrated marketplace data with existing board game metadata and ratings datasets.

These datasets originated from different sources and formats, so they had to be standardized before merging. I implemented transformation workflows that handled:

* Missing or incomplete values
* Column-name standardization
* Data type alignment
* Schema consistency checks
* Record validation before merge operations

This preprocessing made it possible to combine pricing, ratings, and metadata into a unified structured dataset.

The resulting dataset contained enriched board game records that could be loaded into the application’s relational database and used by downstream marketplace and browsing workflows.

---

## Data Cleaning, Normalization & Ranking Reindexing

After dataset integration, the pipeline performed additional normalization steps to ensure the data could be stored and queried reliably.

These steps included:

* Renaming columns to maintain consistent schema conventions
* Resolving null or malformed values
* Validating record completeness after merging
* Standardizing schema fields across the dataset
* Exporting cleaned datasets for relational database ingestion

One important transformation involved the `game_rank` column.

After merging multiple datasets, ranking values were no longer sequential. I recalculated and reindexed the ranking column to produce a consistent sequential ranking across all entries. This ensured that ranking-based queries and displays behaved predictably once the dataset was integrated into the application database.

---

## Recursive Data Modeling for Game Reimplementations

During development, the team identified a limitation in the original representation of game relationships.

The initial schema used a simple boolean attribute to indicate whether a game was related to another version. This was insufficient for real BoardGameGeek data, where games can have multiple editions, reimplementations, expansions, and parent-child relationships.

To support a more accurate relational structure, the schema was updated to represent recursive relationships between games using a dedicated reimplementations table.

Supporting this schema required changes to the preprocessing pipeline. I implemented logic to:

* Parse nested lists of related games from the source dataset
* Extract parent-child relationships between games
* Generate mapping datasets linking parent game IDs to child game IDs
* Validate that each relationship referenced valid game records
* Export relationship mappings for relational database ingestion

In this structure:

* A parent game ID represents the canonical or source version of a game
* Child game IDs represent alternate versions, reimplementations, or related editions

This improved the database model by replacing a shallow boolean flag with a relational mapping that better reflected the structure of real board game data.

---

## AWS Lambda Backend Function for Account Funds

In addition to the data engineering work, I implemented backend functionality for recording user account funds.

This component was implemented as an AWS Lambda serverless function. The Lambda function allowed the system to update user balances without requiring a dedicated application server.

The function handled requests from the frontend when users added funds to their accounts. Its responsibilities included:

* Receiving account-funding requests from the application
* Validating request payloads
* Updating account balances in the relational database
* Returning updated balance information to the frontend

The platform used a simulated currency system where users could add funds and use those funds to purchase board games. The Lambda function served as the backend mechanism for persisting account balance updates.

---

## React Checkout Workflow

I also developed the React-based checkout page, which provided the user interface for managing cart contents and initiating simulated purchase transactions.

This component connected frontend cart behavior with backend transaction APIs.

The checkout workflow supported:

* Loading cart contents from browser local storage
* Handling multi-item carts
* Handling single-item checkout initiated directly from a game page
* Normalizing stored item data into checkout state
* Adjusting item quantities
* Removing items from the cart
* Reviewing updated order totals
* Validating account balance before transaction submission
* Submitting transaction payloads to backend APIs
* Updating local storage after successful purchase
* Refreshing user balance from the backend after transaction completion

This made the checkout page more than a static interface. It coordinated client-side state, persistent browser storage, backend account state, and transaction submission behavior.

---

## Cart State Management & Balance Validation

The checkout page initialized cart state from browser local storage so cart data persisted across navigation and reloads.

The component reconciled two cart sources:

* A multi-item cart containing several games
* A single-item cart created when users initiated checkout directly from a game page

After initialization, users could update quantities, remove items, and review totals. Each cart update was synchronized back to local storage.

Before allowing a purchase, the interface calculated the total order value and compared it against the user’s available account balance. If the order exceeded the available balance, the interface displayed an insufficient funds warning and prevented transaction submission.

This validation ensured that basic purchasing rules were enforced before the frontend communicated with backend transaction APIs.

---

## Transaction Submission Flow

The checkout page supported both single-item checkout and bulk checkout of all cart items.

When a purchase was initiated, the checkout logic constructed a transaction payload containing selected game IDs and quantities. This payload was submitted to the application’s backend transaction API.

After a successful transaction:

* Purchased items were removed from the cart
* Local storage was updated to reflect the new cart state
* The user’s balance was refreshed from the backend
* The interface reflected the updated checkout state

This workflow kept the relational database as the authoritative source of account balance data while maintaining responsive frontend interactions.

---

## Engineering Challenges

The project involved several practical engineering constraints.

### API Rate Limits

External marketplace endpoints enforced request limits. The ingestion pipeline needed asynchronous request management, pacing, and retries to avoid failed or blocked requests.

### Heterogeneous Source Data

Marketplace prices, ratings, and metadata came from different formats and sources. Integrating them required careful schema alignment, missing-value handling, and validation.

### Ranking Consistency

After merging datasets, ranking fields became inconsistent. Reindexing was required to preserve predictable ordering and ranking behavior.

### Recursive Relationships

Board game reimplementations and related editions could not be represented accurately with a simple boolean field. This required a recursive relationship model and corresponding preprocessing logic.

### Frontend / Backend State Synchronization

Checkout behavior needed to coordinate local cart state, backend balance state, and transaction API responses. This required careful handling of local storage, validation, and post-transaction updates.

---

## System Architecture & Documentation

The system connected data engineering, backend services, and frontend workflows.

The architecture included:

* External BoardGameGeek marketplace, metadata, and ratings data
* Asynchronous Python ingestion using `aiohttp`
* Data enrichment and normalization workflows
* Recursive relationship mapping for reimplementations
* Relational database-ready outputs
* AWS Lambda account-funding backend logic
* React checkout interface
* Browser local storage for cart persistence
* Backend transaction APIs for simulated purchases

The project demonstrated how external data ingestion and relational modeling can support application-layer behavior. The data pipeline was not isolated from the product workflow; it provided the structured data foundation needed for browsing, marketplace behavior, and checkout functionality.

---

## Business Impact

* Improved ingestion throughput by replacing sequential request processing with asynchronous API collection
* Collected and standardized marketplace pricing data for approximately **150 board games**
* Integrated pricing, ratings, and metadata into structured datasets for relational database ingestion
* Improved data quality through cleaning, normalization, schema alignment, and validation
* Replaced a shallow relationship flag with recursive parent-child mappings for game reimplementations
* Implemented backend account-funding functionality using AWS Lambda
* Built a React checkout workflow supporting cart management, balance validation, and transaction submission
* Connected external data ingestion, backend account operations, and frontend purchasing behavior into a more coherent application workflow

---

## Technical Skills Demonstrated

* Asynchronous Python data ingestion
* `aiohttp` API collection
* Rate-limit handling
* Retry logic and progress tracking
* Data enrichment and integration
* Data cleaning and normalization
* Schema alignment across heterogeneous datasets
* Ranking reindexing
* Recursive relational modeling
* Parent-child relationship mapping
* Relational database preprocessing
* AWS Lambda backend development
* Serverless account update logic
* React frontend development
* Checkout workflow implementation
* Browser local storage state management
* Balance validation
* Transaction payload construction
* Full-stack data application integration

---

## Key Takeaway

This work followed a consistent engineering pattern:

* **Collected** external marketplace data through asynchronous API ingestion
* **Handled** endpoint constraints through rate-limit management, retries, and progress tracking
* **Integrated** pricing, ratings, and metadata into enriched structured datasets
* **Cleaned** and normalized records for relational database ingestion
* **Reindexed** ranking fields to preserve predictable query behavior
* **Modeled** recursive board game relationships using parent-child mappings
* **Implemented** backend account-funding functionality with AWS Lambda
* **Built** a React checkout workflow connecting cart state, balance validation, and transaction APIs

The result was a full-stack data platform contribution that connected external data ingestion, relational preprocessing, backend account operations, and frontend marketplace behavior.
