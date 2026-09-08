# 🌴 Timor-Leste Tourism Data Mining & Near-Real-Time Recommendation System

A full-stack web application for tourism data mining, analytics, sentiment analysis, K-Means clustering, and tourism destination recommendation for Timor-Leste.

This project was developed as a Capstone Project for the **Mining and Exploring** course at **Dili Institute of Technology (DIT)**, Computer Science Program, 2026.

---

## 📋 Project Overview

Tourism is an important sector for Timor-Leste. However, tourism information available online is distributed across different destinations, ratings, reviews, locations, categories, and other attributes.

This project develops a tourism intelligence system that collects tourism data from online sources, stores and preprocesses the data, performs Exploratory Data Analysis (EDA), applies data mining techniques, analyzes tourist reviews, groups tourism destinations using K-Means clustering, and provides destination recommendations based on user preferences.

The system also supports **near-real-time data collection using a 5-minute polling interval**, allowing tourism data to be periodically updated while the application is running.

---

## 🎓 Capstone Project Information

| Information | Details |
|---|---|
| Institution | Dili Institute of Technology (DIT) |
| Program | Computer Science |
| Course | Mining and Exploring |
| Year | 2026 |
| Project Topic | Data Mining no Rekomendasaun Turizmu Timor-Leste |
| Case Study | Tourism Destinations and Tourist Reviews in Timor-Leste |
| Main Techniques | Clustering, Recommendation, Sentiment Analysis |

---

# 🎯 Problem Statement

Tourism information in Timor-Leste contains useful information such as destination ratings, tourist reviews, location, categories, popularity, and other destination characteristics.

However, this information is not always easy to analyze systematically.

The main problems addressed by this project are:

1. Tourism data is distributed across online sources.
2. Tourism destinations have different levels of popularity and review activity.
3. Tourist reviews contain useful opinions that need to be analyzed.
4. It can be difficult for tourists to identify destinations that match their preferences.
5. Tourism data needs to be visualized in a clear and interactive way.

Therefore, this project develops a tourism data mining system that can collect, analyze, cluster, and recommend tourism destinations in Timor-Leste.

---

# 🎯 Objectives

## General Objective

To develop a tourism data mining and recommendation system that analyzes tourism destinations and tourist reviews in Timor-Leste using online data, data preprocessing, EDA, K-Means clustering, sentiment analysis, and recommendation techniques.

## Specific Objectives

1. Collect tourism destination and review data from online sources.
2. Store tourism data in a structured database.
3. Clean and preprocess tourism destination and review data.
4. Perform Exploratory Data Analysis (EDA).
5. Extract useful features from tourism data.
6. Apply K-Means clustering to group tourism destinations.
7. Analyze tourist review sentiment.
8. Develop a content-based recommendation system.
9. Evaluate clustering results using the Silhouette Score.
10. Develop an interactive tourism dashboard.
11. Support periodic tourism data updates using a 5-minute polling interval.
12. Provide interpretable tourism insights for users.

---

# 🌐 Data Source

The system is designed to collect tourism information from online tourism-related sources using an online data collection service.

## Primary Data Source

- Apify
- Google Places-related tourism/location data

## Data Collection Method

The system uses an online data collection service to obtain tourism destination information and tourist review data.

The collected data is validated and stored in the project database before preprocessing and analysis.

## Collection Information

| Item | Details |
|---|---|
| Primary Source | Apify |
| Data Type | Tourism destinations and tourist reviews |
| Related Data Source | Google Places-related tourism/location data |
| Collection Method | Periodic data collection |
| Update Interval | Every 5 minutes |
| Collection Date | **[FILL IN COLLECTION DATE]** |
| Collection Time | **[FILL IN COLLECTION TIME]** |
| Source URL / API | **[FILL IN SOURCE URL OR API DOCUMENTATION]** |

> Note: The system uses the term **near-real-time** according to the DIT Capstone Manual because the data collection process uses periodic polling rather than continuous real-time streaming.

---

# 📦 Dataset

The current project dataset contains tourism destination information and tourist review information.

## Dataset Statistics

| Dataset / Metric | Value |
|---|---:|
| Tourism Destinations | 569 |
| Stored Tourist Reviews | 3,190 |
| Destination Review Count | 42,470 |
| K-Means Clusters | 4 |
| Clustering Features | 6 |

### Destination Data

Main destination attributes include:

- Destination name
- Address
- City
- Municipality
- Category
- Description
- Latitude
- Longitude
- Rating
- Review count
- Popularity score
- Price level
- Image count
- Place ID
- Source information

### Review Data

Main review attributes include:

- Destination name
- Place ID
- Rating
- Review text
- Original review text
- Translated review text
- Review date
- Reviewer name
- Reviewer photo
- Source
- Raw data

---

# 🏗️ System Architecture

The system follows the following data processing architecture:

```text
Online Tourism Data Source
          ↓
Data Collection
          ↓
Raw Tourism Data
          ↓
Data Validation
          ↓
Database Storage
          ↓
Data Preprocessing
          ↓
Feature Engineering
          ↓
Exploratory Data Analysis
          ↓
K-Means Clustering
          ↓
Sentiment Analysis
          ↓
Recommendation System
          ↓
Tourism Dashboard