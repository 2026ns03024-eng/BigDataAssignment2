# Birla Institute of Technology & Science, Pilani
## Work Integrated Learning Programmes Division

**First Semester 2026-2027**

| Field | Details |
|---|---|
| Course Title | Big Data Systems |
| Course No(s) | CC ZG522 |
| Instructor/Faculty | Dr D VENKATA SUBRAMANIAN |
| Assignment No. | 2 |
| Assignment Title | Big Data Systems Implementation & Analytics |
| Start Date | OCT 10th 2026 |
| End Date | NOV 15th 2026 |
| Total Marks | 10 |

## Assignment Overview

Modern Big Data architecture has evolved beyond monolithic batch processing. Industry enterprises actively combine operational document databases (such as MongoDB) with distributed memory compute clusters (such as Apache Spark). The primary objective of this assignment is to challenge Master's level students to evaluate and contrast database-level computational processing versus distributed compute-engine processing.

Students are given the freedom to solve complex enterprise problems using MongoDB's native Aggregation Framework, PySpark's distributed DataFrames and MLlib pipelines, or a state-of-the-art Hybrid Architecture leveraging the Mongo-Spark Connector. This forces students to understand not just 'how to write code', but 'where compute should reside' based on data locality, latency, indexing, and memory overhead.

## Six Comprehensive Industry Scenarios / Case Studies

Anyone can be selected based on the interest.

### Scenario 1: Retail & E-Commerce — Omnichannel Analytics & Dynamic Customer LTV

**Domain Context:** An omnichannel retailer tracks real-time customer purchasing behavior, cart events, returned items, and product catalog interactions across web, mobile app, and physical POS systems.

**Data Architecture:** Documents are formatted as nested BSON/JSON structures containing arrays of purchased items, category tags, session metadata, dynamic pricing, and payment tokens.

### Scenario 2: Industrial IoT Automation — Sensor Telemetry & Predictive Failure

**Domain Context:** A smart manufacturing plant streams multi-sensor telemetry (vibration, temperature, pressure, rotational speed) from 5,000 industrial CNC machines at sub-second intervals to detect anomalies and schedule predictive maintenance.

**Data Architecture:** High-velocity time-series streams consisting of machine ID, timestamp, sensor array payload, status codes, and operating environment variables.

### Scenario 3: Healthcare & Telemedicine — Remote Patient Monitoring & Readmission Risk

**Domain Context:** A regional hospital network aggregates electronic health records (EHR), Continuous Glucose Monitoring (CGM) streams, wearable physiological metrics, and unstructured clinical diagnoses to predict 30-day patient readmission risk.

**Data Architecture:** Polymorphic documents containing patient demography, historical ICD-10 diagnosis arrays, nested lab result arrays, continuous heart rate time-series, and unstructured physician notes.

### Scenario 4: Social Media Analytics — Viral Trend Detection & Sentiment Modeling

**Domain Context:** A media analytics firm monitors global social platform streams (posts, retweets, threaded nested comments, user follower graphs, and geo-location metrics) to track brand sentiment and compute real-time viral propagation rates.

**Data Architecture:** Unstructured and semi-structured documents with dynamic key-value properties, embedded media references, nested comment trees, hashtag arrays, and interaction counts.

### Scenario 5: EdTech & Online Learning — Adaptive Pathways & Dropout Risk

**Domain Context:** An international EdTech platform collects interaction logs from millions of online students, tracking video playback behavior (pauses, rewinds, speed), quiz attempt histories, forum post activity, and module completion rates.

**Data Architecture:** Hierarchical student event documents containing nested arrays of course progress, timestamped interaction logs, assessment performance matrices, and discussion board metrics.

### Scenario 6: Financial Technology (Fintech) — Real-Time Fraud & Geospatial Risk

**Domain Context:** A global payment processor monitors high-frequency transaction streams across digital wallets, credit cards, and cross-border transfers to flag fraudulent behavior and compute real-time credit risk scores.

**Data Architecture:** High-velocity transaction logs containing transaction IDs, sender/receiver account nodes, transaction amounts, merchant categories, device footprints, and geospatial coordinates.

> Public datasets from Kaggle, Government Open Data Portals, UCI Repository, Data.gov, etc., may be used. Students are encouraged to enrich the dataset through additional preprocessing wherever applicable or generate synthetic data set through GEN AI tools as appropriate.

## Dynamic Execution Track Options

For each scenario, students may choose one of three technical tracks based on their architectural interest:

- **Track A — Pure MongoDB Engine:** Implement end-to-end data processing, complex joins (`$lookup`), rolling analytics (`$setWindowFields`), graph traversals (`$graphLookup`), and dynamic bucket categorization natively within MongoDB collections.
- **Track B — Pure Apache Spark / PySpark Engine:** Load raw JSON/BSON datasets directly into PySpark DataFrames, perform distributed schema flattening, windowed aggregations, and construct MLlib Machine Learning pipelines (ALS, Random Forest, GBT, Word2Vec).
- **Track C — Hybrid Enterprise Architecture:** Utilize MongoDB as the operational time-series/document datastore, stream/read data into PySpark via the Mongo-Spark Connector for heavy model training, and persist predictions/vector embeddings back to MongoDB collections.

## Expected Learning Outcomes

By completing this assignment, students should be able to:

- Apply NoSQL/MongoDB for the scenario.
- Apply Big Data Infrastructure/two nodes cluster lab environment.
- Demonstrate ML Spark/PySpark.
- Integrate Python programs and MongoDB databases.
- Generate dashboards and analytical reports.
- Present technical findings professionally.

## Implementation Platform

Students may choose **Option A or Option B** of the following implementation platforms.

The recommended option/path is to use BITS Cluster Labs (Option A) and use the screenshots/images to add in the assignment solution.

### Option A — PRAYOGSHALA

- https://prayogshala.bits-pilani.ac.in/auth/login

CLUSTER INFRASTRUCTURE
0/3 Active
Node 1 - master Master

Node 2 - slave1 Worker

Node 3 - slave2 Worker

### Option B — Any Cloud Platform or WSL / VM Platform

- Amazon Web Services (AWS)
- Google Cloud Platform (GCP)
- MongoDB Cluster / Atlas

## Dashboard Options

Students may construct their dashboard using:

- **MongoDB Charts**
- **Python Frameworks:** Plotly, Dash, Streamlit, Seaborn, Matplotlib
- **BI Tools:** Power BI, Tableau, Apache Superset connected to MongoDB/Spark datastores

---

*Converted from the provided Assignment 2 PDF into Markdown.*
