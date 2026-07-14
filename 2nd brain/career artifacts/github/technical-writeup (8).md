# Wellington Management — Reverse-Engineering a $153B Investment Data Platform

## Overview

At Wellington Management, I reconstructed the application-level data architecture behind a Python-based investment decision platform supporting **$153B in insurance assets across 23 countries**, used by approximately **160 investment professionals globally**.

The platform was being migrated from a legacy Excel-driven workflow into a production decision system. The underlying Oracle environment contained approximately **250 tables**, but there was no usable application-level schema documentation explaining which tables mattered, how they joined, what cardinalities existed, or how spreadsheet-based business logic mapped to the data layer.

I partnered with the primary stakeholder/PM to understand the legacy Excel workflow, translated spreadsheet logic into database search patterns, narrowed the working scope from approximately **250 tables to 25 core datasets**, decomposed a large multi-nested SQL pipeline, diagnosed a missing upstream dependency, restored execution, and documented the relational model needed for the platform to function reliably.

---

## System Overview

<img width="750" height="500" alt="architecture" src="https://github.com/user-attachments/assets/23c612b6-2000-48d9-9e9a-f072d247d65d" />

*Reconstructed the data architecture behind a $153B investment decision platform, restored a blocked SQL pipeline, and supported an estimated ~$8.05M in annual workflow efficiency gains.*

---

## Technical Problem

The platform’s data layer originated from spreadsheet-based business logic translated into a large SQL pipeline. The query contained nested subqueries, joins, aggregations, and window functions, but it did not execute because one required upstream table dependency was unavailable.

The core issue was not simply a broken query. The system lacked an interpretable application-level data model. The team did not initially know whether the failure came from flawed SQL logic, missing source data, invalid join paths, incomplete table access, or misunderstood business rules.

The Oracle environment contained approximately **250 tables**, but there was no reliable map of:

* Which tables were relevant to the application workflow
* How Excel functions and business rules mapped to database tables and fields
* How tables linked together through valid join paths
* What cardinalities existed between entities
* Which join types were required for downstream outputs
* Which fields drove calculations, filters, aggregations, and window functions
* How source data flowed through SQL transformations into the Python application layer

As a result, the platform’s data layer was structurally opaque. Core queries could not execute reliably until the application-level architecture, dependencies, and lineage were reconstructed.

---

## Environment & Constraints

* **Database:** Oracle SQL
* **Application Layer:** Python, Pandas, ipywidgets
* **Source Workflow:** Legacy Excel-based investment workflow
* **Initial SQL Logic:** Large multi-nested query translated from Excel-based business logic
* **Primary Stakeholder:** Product manager responsible for platform workflow and business requirements
* **Users:** Approximately 160 investment professionals globally
* **Business Scope:** $153B in insurance asset workflows across 23 countries
* **Primary Constraints:** No usable application-level schema documentation, unclear lineage, unknown table relevance, broken pipeline execution, missing upstream dependency

---

## My Role

* Partnered with the primary stakeholder/PM to understand the Excel-based business workflow, calculation logic, and output requirements
* Mapped spreadsheet functions and business rules to Oracle table names, fields, joins, and transformation patterns
* Reduced the working data scope from approximately **250 tables to 25 core datasets**
* Decomposed a large nested SQL query into interpretable transformation layers
* Diagnosed and resolved a critical pipeline execution failure caused by a missing upstream table dependency
* Reconstructed the application-level relational model supporting downstream Python analytics
* Documented relevant tables, fields, joins, dependencies, transformation logic, and system architecture
* Co-engineered an analytics override framework using Python, Pandas, Oracle SQL, and ipywidgets

---

## Business-to-Data Layer Mapping

A central part of the work was translating stakeholder knowledge into a usable data architecture.

I met with the primary stakeholder/PM to understand what the legacy Excel workflow was doing: which spreadsheet functions mattered, how calculations were structured, what intermediate outputs represented, and how investment users interpreted the final results.

That business context became the key to narrowing the technical search space. Instead of treating the Oracle environment as 250 undifferentiated tables, I used the Excel workflow as a map for identifying likely data sources, relevant fields, table naming patterns, joins, and transformation dependencies.

This process involved:

* Translating spreadsheet functions into data requirements
* Mapping Excel-derived business concepts to Oracle table and field patterns
* Comparing business terminology against database object names and column names
* Identifying fields likely to drive calculations, filters, aggregations, and outputs
* Using stakeholder context to distinguish relevant tables from unrelated database objects
* Connecting business outputs back to upstream data dependencies

This business-to-data mapping reduced the working search space from approximately **250 Oracle tables** to approximately **25 core datasets** that appeared to drive the platform workflow.

---

## Application-Level Architecture Reconstruction

Using the narrowed set of core datasets, I reconstructed how the application’s data layer functioned end to end.

The work required combining stakeholder context, SQL decomposition, and database inspection. I broke down the large nested SQL pipeline into smaller transformation layers, identified implicit joins and filtering logic, traced aggregation and window-function behavior, and mapped how source data flowed into downstream Python analytics outputs.

The reconstruction focused on:

* Identifying relevant Oracle tables and fields
* Mapping primary-key and foreign-key patterns where documentation was unavailable
* Inferring cardinalities between entities based on join behavior and output requirements
* Tracing dependencies across nested subqueries, joins, aggregations, and window functions
* Connecting source datasets to SQL transformations and Python application outputs
* Documenting the relational structure needed for developers and analysts to reason about the platform

The result was a reconstructed relational map of the dependencies, joins, lineage, and transformation logic required for the investment decision platform to function.

---

## Pipeline Failure Diagnosis & Recovery

The initial SQL logic was delivered as one large, multi-nested query translated from Excel-based business logic. It included complex joins, aggregations, and window functions, but failed during execution because a required upstream table dependency was unavailable.

I diagnosed the failure by:

* Decomposing the nested SQL into interpretable transformation layers
* Tracing table dependencies across subqueries, joins, aggregations, and window functions
* Identifying the missing upstream dataset referenced by downstream logic
* Verifying the dependency gap through targeted Oracle SQL inspection queries
* Coordinating access restoration with the team

Once access was restored, the SQL pipeline executed successfully with minimal modification. This confirmed the failure originated from a missing data dependency rather than defective transformation logic.

This distinction mattered because it prevented unnecessary rewriting of valid SQL logic and redirected the recovery effort toward the actual system-level blocker: incomplete access to a required upstream dataset.

---

## Analytics Override Framework

To support investment decision-making, I co-engineered a controlled override framework that allowed users to adjust parameters without bypassing validation, traceability, or downstream calculation integrity.

* Implemented override functionality using **Python, Pandas, Oracle SQL, and ipywidgets**
* Enforced validation constraints on user inputs
* Preserved auditability of parameter modifications
* Integrated override logic into downstream calculations

This provided flexibility for investment users while maintaining the reliability and traceability of the data system.

---

## System Architecture & Documentation

To improve system clarity and maintainability, I formalized platform architecture and data flow documentation.

* Produced architecture diagrams for both legacy and production workflows
* Documented relevant tables, joins, dependencies, transformation layers, and pipeline structure
* Mapped interactions between the UI, Python application logic, SQL transformations, and Oracle data layer
* Created a shared technical reference for developers, analysts, and stakeholders working on the platform

This documentation converted implicit institutional and spreadsheet-based logic into an explicit technical model of the platform.

---

## Business Impact

* Enabled a production-bound investment decision platform supporting **$153B in insurance asset workflows across 23 countries**
* Restored a critical SQL pipeline, unblocking core application functionality
* Supported reliable usage by approximately **160 investment professionals globally**
* Helped replace spreadsheet-based workflows with a structured decision system
* Contributed to approximately **$8.05M–$8.06M in estimated annual operational efficiency gains**, calculated as:

  * 160 users × 10 hours/week × 48 weeks × approximately $105/hour

---

## Technical Skills Demonstrated

* Application-level data architecture reconstruction
* Business-to-data layer mapping
* Stakeholder requirements translation
* Oracle SQL pipeline debugging
* Complex SQL decomposition across nested subqueries, joins, aggregations, and window functions
* Data lineage analysis and dependency tracing
* Relational data modeling under incomplete documentation
* Cardinality and join-path inference
* Business-logic translation from Excel workflows into SQL/Python analytics systems
* SQL-to-Python application integration
* Production workflow documentation under ambiguity

---

## Key Takeaway

This work followed a consistent engineering pattern:

* **Elicited** business logic from the primary stakeholder/PM
* **Mapped** Excel-based workflows to the Oracle data layer
* **Reduced** the technical search space from approximately 250 tables to 25 core datasets
* **Decomposed** complex SQL translated from Excel business logic
* **Diagnosed** a missing upstream dependency blocking execution
* **Restored** critical pipeline functionality
* **Reconstructed** the application-level relational model and lineage required for reliable downstream analytics
* **Documented** the system architecture so future developers and analysts could understand the platform

The result was a transition from a non-functional, opaque data environment to a coherent, interpretable decision infrastructure capable of supporting real-world investment workflows.
```

