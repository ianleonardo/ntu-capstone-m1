# Workforce Intelligence Portal

> A comprehensive data analytics platform for analyzing Singapore's job market trends and aligning educational curriculum with real-time industry demand.

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://ntu-m1-capstone.theluwak.com/)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-latest-red.svg)](https://streamlit.io/)

Built as part of the **NTU SCTP M1 Capstone Project**, this interactive dashboard empowers educators, career counselors, and workforce planners to make data-driven decisions by providing deep insights into market demand, salary trends, and skill requirements.

## 🎯 Overview

The Workforce Intelligence Portal transforms raw job market data into actionable insights through five comprehensive analytical modules:

### **1. Executive Summary**
Get a high-level overview of the job market with key metrics including:
- Total job vacancies and postings
- Aggregate view counts
- Top performing sectors breakdown
- Market health indicators

### **2. Market Demand Analysis**
Understand hiring patterns across Singapore:
- Geographic visualization of bulk hiring activities
- Top job titles segmented by industry sector
- Demand hotspots and emerging roles

### **3. Salary & Value Intelligence**
Make informed compensation decisions:
- Experience vs. compensation matrix analysis
- Interactive salary heatmaps by sector
- Role-specific salary distributions
- Competitive positioning insights

### **4. Market Momentum Tracking**
Monitor temporal trends and predict future demand:
- Historical vacancy trend analysis
- Seasonal hiring pattern identification
- Sector growth leaderboards
- Year-over-year comparisons

### **5. Curriculum Deep-Dive**
Bridge the gap between education and industry:
- Sector-specific job exploration
- Skills gap analysis with curriculum mapping
- In-demand skillset identification
- Educational alignment recommendations

## 🚀 Live Demo

Experience the portal in action: **[https://ntu-m1-capstone.theluwak.com/](https://ntu-m1-capstone.theluwak.com/)**

## 📁 Project Structure

```
ntu-capstone-m1/
├── app.py                      # Main Streamlit application
├── preprocess_data.py          # Data cleansing and transformation pipeline
├── extract_skills.py           # Skills extraction utilities
├── refactor_data.py            # Data restructuring scripts
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container configuration
├── data/
│   ├── SGJobData.csv.xz        # Raw job market data (compressed)
│   ├── SGJobData_opt.csv.xz    # Optimized pre-processed data
│   └── skillset.csv            # Curriculum and skills reference data
└── presentation/               # Project documentation and presentations
```

## 🔄 Data Pipeline

The application uses a multi-stage data processing pipeline:

```
┌─────────────────┐
│  Raw Data       │  SGJobData.csv.xz
│  (Compressed)   │  
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Preprocessing  │  • Job title standardization
│                 │  • Salary normalization
│                 │  • Date parsing & validation
│                 │  • Type categorization
│                 │  • Column optimization
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Optimized Data │  SGJobData_opt.csv.xz
│  (Ready-to-use) │  (Smaller, faster loading)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Streamlit App  │  • Category explosion
│                 │  • Real-time aggregations
│                 │  • Interactive visualizations
└─────────────────┘
```

### Pipeline Steps

1. **Raw Data Ingestion**: Load compressed job market data
2. **Data Cleansing**: Apply standardization and validation rules
3. **Optimization**: Reduce file size and select relevant columns
4. **Runtime Processing**: Explode categories and render dashboards

## 📋 Prerequisites

- Python 3.9 or higher
- pip package manager
- 4GB+ RAM recommended for data processing

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ntu-capstone-m1.git
cd ntu-capstone-m1
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 💻 Usage

### First-Time Setup or After Data Updates

Generate the pre-processed optimized dataset:

```bash
python preprocess_data.py
```

This will create `SGJobData_opt.csv.xz` in the `data/` directory.

### Launch the Dashboard

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

### Additional Scripts

Extract and analyze skills data:

```bash
python extract_skills.py
```

Refactor and restructure data:

```bash
python refactor_data.py
```

## 🐳 Docker Deployment

The project includes a Dockerfile for containerized deployment to platforms like Google Cloud Run, AWS ECS, or Azure Container Instances.

### Build the Docker Image

```bash
docker build -t workforce-portal .
```

### Run the Container Locally

```bash
docker run -p 8501:8501 workforce-portal
```

### Deploy to Google Cloud Run

```bash
gcloud run deploy workforce-portal \
  --source . \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated
```

## 📊 Data Sources

- **Job Market Data**: Singapore job postings aggregated from multiple sources
- **Skills Reference**: Curated curriculum and industry skills mapping
- **Geographic Data**: Singapore regions and postal codes for location analysis

## 🔧 Configuration

Key configurations can be modified in `app.py`:

- Page layout and theme settings
- Data file paths
- Visualization parameters
- Filtering options

## 🤝 Contributing

This is an academic capstone project. For questions or collaboration inquiries, please contact the project team.

## 📄 License

This project was developed as part of the NTU SCTP M1 Capstone program. Please contact the project team regarding usage and distribution rights.

## 📧 Contact

For questions, feedback, or support, please reach out to the NTU SCTP M1 Capstone team.

---

**Developed with ❤️ for NTU SCTP M1 Capstone Project**
