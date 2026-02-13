# Workforce Intelligence Portal

> A streamlined analytics platform for analyzing Singapore's job market competition and aligning curriculum with industry demand.

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://ntu-m1-capstone.theluwak.com/)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-latest-red.svg)](https://streamlit.io/)

Built as part of the **NTU SCTP M1 Capstone Project**, this interactive dashboard provides educators, career counselors, and workforce planners with focused insights into market competition, skill demand, and opportunity identification.

## 🎯 Overview

The Workforce Intelligence Portal delivers actionable insights through four focused analytical modules:

### **📊 Executive Summary**
High-level market overview:
- Total vacancies, job posts, and views
- Top performing sectors by metric
- Interactive sector breakdown visualization

### **🏭 Sectoral Demand & Momentum**
Competition and trend analysis:
- **Demand Velocity**: Track bulk factor trends (applications ÷ vacancies) over time
- **Bulk Hiring Map**: Heatmap showing competition intensity by sector and month
- **High Demand Skills**: Animated visualization of top 10 skills over time with sector filtering

### **🛠️ Skill & Experience Analysis**
Experience and compensation insights:
- **Seniority Pay-Scale**: Average salary by experience level
- **Experience Gate**: Market accessibility by experience tier
- Sector-based filtering for targeted analysis

### **🎓 Education Gap & Opportunity**
Opportunity identification:
- **Supply vs Demand**: Treemap comparing vacancy volume vs application intensity
- **Hidden Demand**: Quadrant analysis by job title identifying low-competition opportunities
  - Green: Hidden opportunities (high vacancies, low applications)
  - Orange: Competitive markets (high demand, high competition)
  - Gray: Niche markets (low volume overall)
  - Red: Oversupplied (low vacancies, high applications)

## 🚀 Live Demo

Experience the portal in action: **[https://ntu-m1-capstone.theluwak.com/](https://ntu-m1-capstone.theluwak.com/)**

## 📁 Project Structure

```
ntu-capstone-m1/
├── app.py                                    # Main Streamlit application
├── app_optimized.py                          # Performance-optimized version
├── preprocess_data.py                        # Data cleansing pipeline
├── extract_skills.py                         # Skills extraction utilities
├── refactor_data.py                          # Data restructuring scripts
├── requirements.txt                          # Python dependencies (incl. Altair)
├── Dockerfile                                # Container configuration
├── data/
│   ├── cleaned-sgjobdata.parquet             # Main job data (Parquet format)
│   ├── cleaned-sgjobdata-category-withskills.parquet  # Skills-enriched data
│   └── skillset.csv                          # Curriculum reference data
└── presentation/                             # Project documentation
```

## 🔄 Data Pipeline & Key Metrics

### Pipeline Architecture

```
┌─────────────────┐
│  Raw Job Data   │  Singapore job postings
│                 │  
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Preprocessing  │  • Job title cleaning
│                 │  • Salary normalization
│                 │  • Date parsing
│                 │  • Category standardization
│                 │  • Skills extraction
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Parquet Files  │  Optimized columnar format
│                 │  Fast loading & querying
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Streamlit App  │  • Cached aggregations
│                 │  • Altair/Plotly charts
│                 │  • Interactive filtering
└─────────────────┘
```

### Key Metrics

- **Bulk Factor**: Applications ÷ Vacancies (competition intensity)
- **Experience Segments**: Fresh (0), Junior (1-2), Mid (3-5), Senior (6-8), Lead (9+)
- **Opportunity Quadrants**: 
  - Hidden Opportunity: High vacancies, low competition
  - Competitive: High vacancies, high competition  
  - Niche: Low vacancies, low competition
  - Oversupplied: Low vacancies, high competition

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

### Launch the Dashboard

**Standard version:**
```bash
streamlit run app.py
```

**Optimized version** (with Altair charts for better performance):
```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

### Data Processing Scripts

**Preprocess raw data:**
```bash
python preprocess_data.py
```

**Extract skills from job descriptions:**
```bash
python extract_skills.py
```

**Refactor and optimize data:**
```bash
python refactor_data.py
```

### Performance Features

- **Caching**: All expensive aggregations cached with `@st.cache_data`
- **Lazy Loading**: Skills data only loaded when Tab 2 is accessed
- **Optimized Charts**: Simple visualizations use Altair (~40KB) instead of Plotly (~3MB)
- **Filtered Caching**: Sector-based filters cache results for instant response

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

## ✨ Key Features

### Competition-Focused Analytics
- **Bulk Factor Metric**: Unique metric showing applications per vacancy
- **Trend Analysis**: Track competition changes over time by sector
- **Heatmap Visualization**: Identify competition hotspots by sector and month

### Opportunity Discovery
- **Quadrant Analysis**: Visual classification of job titles by demand vs competition
- **Hidden Gems**: Identify high-vacancy, low-competition roles
- **Job Title Granularity**: Analysis at individual role level, not just sectors

### Skill Intelligence
- **Temporal Tracking**: Animated visualization of skill demand changes
- **Sector Filtering**: Focus on specific industries
- **Monthly Granularity**: Understand seasonal skill trends

### User Experience
- **Interactive Filters**: Sector-based filtering across multiple charts
- **Responsive Design**: Clean, modern UI optimized for all screen sizes
- **Fast Performance**: Cached computations and optimized visualizations

## 📊 Data Sources

- **Job Market Data**: Singapore job postings (vacancies, applications, views, salaries)
- **Skills Data**: Extracted skills from job descriptions with temporal tracking
- **Reference Data**: Curriculum mapping and industry skillset requirements

## 🔧 Configuration

Edit `app.py` or `app_optimized.py` to customize:

```python
class Config:
    DATA_FILE = 'data/cleaned-sgjobdata.parquet'
    SKILL_FILE = 'data/cleaned-sgjobdata-category-withskills.parquet'
    CACHE_TTL = 3600  # Cache duration in seconds
```

**Adjustable parameters:**
- Cache TTL (time-to-live)
- Top N sectors for analysis (default: 10-12)
- Color schemes for visualizations
- Chart heights and layouts
- Sample sizes for large datasets

## 🛠️ Technical Stack

**Core Technologies:**
- **Streamlit**: Interactive web dashboard framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations

**Visualization Libraries:**
- **Altair**: Lightweight, declarative visualizations (simple charts)
- **Plotly**: Interactive charts for complex visualizations
  - Heatmaps, treemaps, scatter plots with quadrants
  - time-series charts

**Data Storage:**
- **Parquet**: Columnar storage format for efficient I/O
- **Compressed**: Optimized file sizes with fast decompression

**Performance Optimizations:**
- Streamlit caching decorators (`@st.cache_data`)
- Lazy loading strategies
- Efficient aggregation pipelines
- Minimal re-computation on user interactions

## 🤝 Contributing

This is an academic capstone project developed for NTU SCTP M1. For questions or collaboration inquiries, please contact the project team.

## 📄 License

This project was developed as part of the NTU SCTP M1 Capstone program. Please contact the project team regarding usage and distribution rights.

## 🙏 Acknowledgments

- **NTU SCTP Program**: For providing the opportunity and framework
- **Data Sources**: Singapore job market data providers
- **Open Source Community**: Streamlit, Plotly, Altair, and Pandas teams

## 📧 Contact

For questions, feedback, or support, please reach out to the NTU SCTP M1 Capstone team.

---

**Built for NTU SCTP M1 Capstone Project** | [Live Demo](https://ntu-m1-capstone.theluwak.com/)
