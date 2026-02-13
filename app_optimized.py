import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
import json
import re
import os

# ==========================================
# 1. CONFIGURATION & STYLING
# ==========================================
st.set_page_config(page_title="SG Job Market Dashboard for Curriculum Design", layout="wide", page_icon="📊")

# Custom CSS with FORCED COLORS for visibility and Formatting
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #2c3e50 !important; 
    }
    .metric-label {
        font-size: 14px;
        color: #6c757d !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .insight-box {
        background-color: #e3f2fd;
        border-left: 5px solid #2196f3;
        padding: 15px;
        border-radius: 4px;
        margin-top: 10px;
        margin-bottom: 20px;
        height: 100%; 
    }
    .insight-text {
        color: #000000 !important;
        font-size: 16px;
        line-height: 1.5;
    }
    .finding-title {
        font-weight: bold;
        color: #0d47a1 !important;
        margin-bottom: 5px;
        font-size: 18px;
    }
    li {
        color: #000000 !important;
        margin-bottom: 5px;
    }
    b {
        font-weight: 700;
        color: #000;
    }
    [data-testid="stSelectbox"] label, [data-testid="stSelectbox"] p {
        color: #1e293b !important;
    }
    [data-testid="stSelectbox"] div[data-baseweb="select"] {
        background-color: #ffffff !important;
        color: #1e293b !important;
    }
    [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #1e293b !important;
    }
    [data-baseweb="popover"] li, [data-baseweb="popover"] [role="option"] {
        background-color: #ffffff !important;
        color: #1e293b !important;
    }
    [data-baseweb="popover"] li:hover, [data-baseweb="popover"] [role="option"]:hover {
        background-color: #f1f5f9 !important;
        color: #0f172a !important;
    }
    option {
        background-color: #ffffff !important;
        color: #1e293b !important;
    }
</style>
""", unsafe_allow_html=True)

class Config:
    DATA_FILE = 'data/cleaned-sgjobdata.parquet'
    SKILL_FILE = 'data/skills_optimized.parquet'  # Optimized: 1.08MB (was 15.55MB)
    CACHE_TTL = 3600

def _remove_outliers(df, col):
    """IQR-based outlier clipping."""
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return np.where(df[col] > upper_bound, upper_bound,
                    np.where(df[col] < lower_bound, lower_bound, df[col]))


# ==========================================
# 2. OPTIMIZED DATA PROCESSING ENGINE
# ==========================================
class DataProcessor:
    @staticmethod
    def _parse_categories(cat_str):
        try:
            if isinstance(cat_str, str):
                return json.loads(cat_str.replace("'", '"'))
            return []
        except Exception:
            return []

    @staticmethod
    def _extract_category(val):
        if isinstance(val, dict):
            return val.get('category', val.get('name', str(val)))
        return str(val)

    @st.cache_data(ttl=Config.CACHE_TTL, show_spinner="Loading data...")
    def load_and_clean_data():
        """Load and perform basic cleaning - DEFER category explosion"""
        if not os.path.exists(Config.DATA_FILE):
            st.error(f"🚨 Data file not found.")
            st.stop()

        df = pd.read_parquet(Config.DATA_FILE)
        
        # Align column names
        rename_map = {}
        if 'title' in df.columns and 'jobtitle_cleaned' not in df.columns:
            rename_map['title'] = 'jobtitle_cleaned'
        if 'positionlevels' in df.columns and 'positionLevels' not in df.columns:
            rename_map['positionlevels'] = 'positionLevels'
        if rename_map:
            df = df.rename(columns=rename_map)
        
        # Use cleaned salary column
        if 'average_salary_cleaned' in df.columns:
            df['average_salary'] = df['average_salary_cleaned']
        
        # Date handling
        if 'posting_date' in df.columns:
            df['posting_date'] = pd.to_datetime(df['posting_date'])
        else:
            df['posting_date'] = pd.Timestamp('2023-06-01')
        
        df['month_year'] = df['posting_date'].dt.to_period('M').dt.to_timestamp()
        
        # Handle missing values
        df['num_vacancies'] = df['num_vacancies'].fillna(1)
        df['num_applications'] = df['num_applications'].fillna(0)
        df['min_exp'] = df['min_exp'].fillna(0)
        
        # Outlier handling for min_exp
        if 'min_exp' in df.columns and not df.empty:
            df['min_exp'] = _remove_outliers(df, 'min_exp')
        df['min_exp'] = np.clip(df['min_exp'], 0, 15)
        
        # Create experience segments
        def categorize_exp(years):
            if years == 0: return '1. Fresh / Entry (0 yrs)'
            elif years <= 2: return '2. Junior (1-2 yrs)'
            elif years <= 5: return '3. Mid-Level (3-5 yrs)'
            elif years <= 8: return '4. Senior (6-8 yrs)'
            else: return '5. Lead / Expert (9+ yrs)'
        
        df['exp_segment'] = df['min_exp'].apply(categorize_exp)
        
        # Fix view column
        view_col = 'num_views'
        if view_col not in df.columns:
            df[view_col] = 0
        else:
            df[view_col] = pd.to_numeric(df[view_col], errors='coerce').fillna(0)
        
        return df

    def explode_categories(df):
        """Separate function to explode categories - call only when needed"""
        df = df.copy()
        df['parsed_categories'] = df['categories'].apply(DataProcessor._parse_categories)
        df = df.explode('parsed_categories')
        df['category'] = df['parsed_categories'].apply(DataProcessor._extract_category)
        return df

    @st.cache_data(ttl=Config.CACHE_TTL, show_spinner="Loading skills data...")
    def load_skills_data():
        """Load pre-aggregated skills data (optimized for fast loading)"""
        try:
            if os.path.exists(Config.SKILL_FILE):
                # Load pre-aggregated data (much smaller and faster)
                df = pd.read_parquet(Config.SKILL_FILE)
                # Data already contains: skill, category, month_year, job_count
                return df
            else:
                st.info("ℹ️ Skills data file not found. Skills chart will be unavailable.")
                return pd.DataFrame()
        except Exception as e:
            st.error(f"❌ Error loading skills data: {str(e)}")
            st.info("💡 Continuing without skills analysis.")
            return pd.DataFrame()


# ==========================================
# 3. CACHED AGGREGATION FUNCTIONS
# ==========================================

def calculate_executive_metrics(df):
    """Pre-compute all Executive Summary metrics - CACHED"""
    metrics = {
        'total_vacancies': df['num_vacancies'].sum(),
        'total_posts': len(df),
        'total_views': df['num_views'].sum(),
        'top_sector_vacancy': df.groupby('category')['num_vacancies'].sum().idxmax(),
        'top_sector_posts': df['category'].value_counts().idxmax(),
        'top_sector_views': df.groupby('category')['num_views'].sum().idxmax(),
    }
    return metrics

def get_top_sectors_data(df, metric='num_vacancies', limit=10):
    """Get top sectors by metric - CACHED"""
    df_filtered = df[df['category'] != 'Others']
    
    if metric == 'num_views':
        data = df_filtered.groupby('category')[metric].sum().sort_values(ascending=False).head(limit)
    elif metric == 'count':
        data = df_filtered['category'].value_counts().head(limit)
    else:  # num_vacancies
        data = df_filtered.groupby('category')[metric].sum().sort_values(ascending=False).head(limit)
    
    return data.reset_index(name='Value')

def filter_by_sector(df, sector):
    """Filter dataframes by sector"""
    if sector == 'All':
        return df
    return df[df['category'] == sector].copy()

def get_demand_velocity(df):
    """Calculate demand velocity with bulk factor"""
    velocity_df = df[df['category'] != 'Others']
    top_10_sectors = velocity_df.groupby('category')['num_vacancies'].sum().nlargest(10).index
    velocity_df = velocity_df[velocity_df['category'].isin(top_10_sectors)]
    
    # Aggregate by month and category
    agg_df = velocity_df.groupby(['month_year', 'category']).agg({
        'num_applications': 'sum',
        'num_vacancies': 'sum'
    }).reset_index()
    
    # Calculate bulk factor (applications / vacancies)
    agg_df['bulk_factor'] = agg_df.apply(
        lambda x: x['num_applications'] / x['num_vacancies'] if x['num_vacancies'] > 0 else 0,
        axis=1
    )
    
    return agg_df

def get_bulk_hiring_data(df):
    """Calculate bulk hiring heatmap with bulk factor - CACHED"""
    bulk_df = df[df['category'] != 'Others']
    top_sectors_bulk = bulk_df.groupby('category')['num_vacancies'].sum().nlargest(12).index
    bulk_filtered = bulk_df[bulk_df['category'].isin(top_sectors_bulk)]
    
    # Create pivot tables for both applications and vacancies
    applications_pivot = bulk_filtered.pivot_table(
        index='category', columns='month_year', values='num_applications', aggfunc='sum'
    ).fillna(0)
    
    vacancies_pivot = bulk_filtered.pivot_table(
        index='category', columns='month_year', values='num_vacancies', aggfunc='sum'
    ).fillna(0)
    
    # Calculate bulk factor (applications / vacancies)
    # Replace division by zero with 0
    bulk_factor_pivot = applications_pivot / vacancies_pivot.replace(0, 1)
    bulk_factor_pivot = bulk_factor_pivot.fillna(0)
    
    return bulk_factor_pivot

def get_experience_metrics(df, sector='All'):
    """Calculate experience-related metrics - CACHED"""
    if sector != 'All':
        df = df[df['category'] == sector]
    
    # Seniority pay scale
    pay_scale = df.groupby('exp_segment').apply(
        lambda g: (g['average_salary'] * g['num_vacancies']).sum() / g['num_vacancies'].sum()
    ).reset_index(name='avg_salary')
    
    # Experience gate
    gate_df = df.groupby('exp_segment')['num_vacancies'].sum().reset_index()
    
    return pay_scale, gate_df

def get_education_metrics(df):
    """Calculate education gap metrics - CACHED"""
    metrics = df.groupby('category').agg({
        'num_vacancies': 'sum',
        'num_applications': 'sum',
        'min_exp': 'mean',
        'job_id': 'count'
    }).reset_index()
    
    metrics['opp_score'] = metrics['num_vacancies'] / (metrics['min_exp'] + 1)
    metrics['comp_index'] = metrics.apply(
        lambda x: x['num_applications'] / x['num_vacancies'] if x['num_vacancies'] > 0 else 0,
        axis=1
    )
    return metrics


# ==========================================
# 4. MAIN APP
# ==========================================
def main():
    # Load base data (without explosion)
    df_raw = DataProcessor.load_and_clean_data()
    
    # Explode categories (cached)
    with st.spinner("Processing categories..."):
        df = DataProcessor.explode_categories(df_raw)
    
    # Verify Data Integrity
    if df.empty:
        st.error("No valid data found after cleaning. Please check your CSV format.")
        st.stop()

    # Date Period
    if 'posting_date' in df.columns:
        min_d = df['posting_date'].min().strftime('%d %b %Y')
        max_d = df['posting_date'].max().strftime('%d %b %Y')
        period_str = f"{min_d} - {max_d}"
    else:
        period_str = "Date Unavailable"

    st.title("🎓 SG Job Market Dashboard for Curriculum Design")
    st.markdown("Aligning Curriculum with Real-Time Market Structure")
    st.write(f"**Data Period:** {period_str}")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Executive Summary", 
        "🏭 Sectoral Demand & Momentum", 
        "🛠️ Skill & Experience", 
        "🎓 Education Gap & Opportunity"
    ])

    # --- TAB 1: EXECUTIVE ---
    with tab1:
        st.subheader("High-Level Market Snapshot")
        
        # Use cached metrics
        metrics = calculate_executive_metrics(df)
        
        # Use Streamlit native metrics (faster than custom HTML)
        kpi1, kpi2, kpi3 = st.columns(3)
        
        with kpi1:
            st.metric(
                label="👥 Total Vacancies",
                value=f"{metrics['total_vacancies']:,.0f}",
                help=f"Top sector: {metrics['top_sector_vacancy']}"
            )
            st.caption(f"🏆 **Top:** {metrics['top_sector_vacancy']}")

        with kpi2:
            st.metric(
                label="📝 Total Job Posts",
                value=f"{metrics['total_posts']:,.0f}",
                help=f"Top sector: {metrics['top_sector_posts']}"
            )
            st.caption(f"🏆 **Top:** {metrics['top_sector_posts']}")

        with kpi3:
            st.metric(
                label="👁️ Total Job Views",
                value=f"{metrics['total_views']:,.0f}",
                help=f"Top sector: {metrics['top_sector_views']}"
            )
            st.caption(f"🏆 **Top:** {metrics['top_sector_views']}")

        st.divider()

        # Top 10 Sectors Chart with Altair (faster for simple bar charts)
        c_head, c_opt = st.columns([3, 1])
        with c_head:
            st.markdown("#### 📊 Top 10 Sectors Breakdown")
        with c_opt:
            chart_metric = st.selectbox(
                "View By:", 
                ["Vacancies", "Job Posts", "Job Views"],
                index=0
            )

        # Get cached data based on selection
        if chart_metric == "Vacancies":
            chart_data = get_top_sectors_data(df, 'num_vacancies', 10)
            x_label = 'Total Vacancies'
            bar_color = '#2E86C1'
        elif chart_metric == "Job Posts":
            chart_data = get_top_sectors_data(df, 'count', 10)
            x_label = 'Number of Posts'
            bar_color = '#28B463'
        else:
            chart_data = get_top_sectors_data(df, 'num_views', 10)
            x_label = 'Total Views'
            bar_color = '#E67E22'

        # Use Altair for better performance on simple charts
        altair_chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('Value:Q', title=x_label),
            y=alt.Y('category:N', sort='-x', title='Sector'),
            color=alt.value(bar_color),
            tooltip=['category', alt.Tooltip('Value:Q', format=',.0f')]
        ).properties(
            height=500,
            title=f"Top 10 Sectors by {chart_metric}"
        )
        st.altair_chart(altair_chart, use_container_width=True)

    # --- TAB 2: SECTORAL DEMAND & MOMENTUM ---
    with tab2:
        st.subheader("🏭 Sectoral Demand & Momentum")
        st.markdown("Objective: Identify \"What\" to teach by tracking the velocity of industry needs.")
        
        # Demand Velocity (cached)
        st.markdown("#### 📈 Demand Velocity (Bulk Factor)")
        st.caption("Bulk Factor = Applications ÷ Vacancies. Higher values indicate stronger competition.")
        
        velocity_df = get_demand_velocity(df)
        
        if len(velocity_df) > 1:
            fig_vel = px.line(velocity_df, x='month_year', y='bulk_factor', color='category',
                              markers=True, line_shape='spline',
                              title="Top 10 Sectors: Bulk Factor Trend Over Time",
                              labels={'month_year': 'Posting Date', 'bulk_factor': 'Bulk Factor (Apps/Vacancies)', 'category': 'Sector'})
            st.plotly_chart(fig_vel, use_container_width=True, key="demand_velocity_chart")
        else:
            st.warning("Not enough data points for time-series velocity.")

        # 4. Bulk Hiring Map (cached)
        st.markdown("#### 🗺️ Bulk Hiring Map")
        st.caption("Competition intensity by sector and time. Darker = higher bulk factor (more applications per vacancy).")
        
        bulk_pivot = get_bulk_hiring_data(df)
        fig_bulk = px.imshow(
            bulk_pivot, aspect='auto', color_continuous_scale='YlOrRd',
            labels=dict(x='Month', y='Sector', color='Bulk Factor')
        )
        st.plotly_chart(fig_bulk, use_container_width=True, key="bulk_hiring_map")

        # 5. Skills in High Demand
        st.markdown("#### High Demand Skills")
        st.caption("Top 10 skills by unique job postings over time.")
        
        # Load pre-aggregated skills data (optimized: 1.08MB, 14x faster)
        try:
            with st.spinner("Loading optimized skills data..."):
                skills_df = DataProcessor.load_skills_data()
        except Exception as e:
            st.error(f"Failed to load skills data: {str(e)}")
            skills_df = pd.DataFrame()
        
        if not skills_df.empty:
            # Data already contains: skill, category, month_year, job_count (pre-aggregated)
            available_months = sorted(skills_df['month_year'].unique())
            
            # Create formatted month labels (e.g., "Nov 2023")
            month_labels = {}
            for month in available_months:
                # Convert "2022-10" to "Oct 2022"
                date_obj = pd.to_datetime(month)
                month_labels[month] = date_obj.strftime('%b %Y')
            
            if len(available_months) > 0:
                st.markdown("### 📈 Skill Demand Timeline - Top 10 Most Popular Skills")
                
                skills_sectors = ['All'] + sorted(skills_df['category'].dropna().unique().tolist())
                col_skills_filter, col_skills_space = st.columns([1, 3])
                with col_skills_filter:
                    st.markdown("**Filter by Sector**")
                with col_skills_space:
                    selected_skills_sector = st.selectbox("", skills_sectors, key="skills_sector_filter", label_visibility="collapsed")
                
                # Filter by sector
                skills_filtered = skills_df.copy()
                if selected_skills_sector != 'All':
                    skills_filtered = skills_filtered[skills_filtered['category'] == selected_skills_sector]
                
                # Find top 10 skills overall (sum of job_count across all months)
                top_skills = skills_filtered.groupby('skill')['job_count'].sum().nlargest(10).index.tolist()
                
                if top_skills:
                    # Filter timeline data for top 10 skills
                    timeline_df = skills_filtered[skills_filtered['skill'].isin(top_skills)].copy()
                    
                    # Group by skill and month (sum job_count across categories if needed)
                    timeline_df = timeline_df.groupby(['skill', 'month_year'])['job_count'].sum().reset_index()
                    
                    # Convert month to formatted labels
                    timeline_df['month_label'] = timeline_df['month_year'].map(month_labels)
                    
                    # Create line chart
                    fig = px.line(
                        timeline_df,
                        x='month_label',
                        y='job_count',
                        color='skill',
                        markers=True,
                        title=f'Skill Demand Timeline - Top 10 Most Popular Skills' if selected_skills_sector == 'All' else f'Top 10 Skills in {selected_skills_sector}',
                        labels={
                            'month_label': 'Month-Year Period',
                            'job_count': 'Number of Unique Job Postings',
                            'skill': 'Skill'
                        }
                    )
                    
                    fig.update_layout(
                        height=600,
                        hovermode='x unified',
                        legend=dict(
                            title='Skills',
                            orientation='v',
                            yanchor='top',
                            y=1,
                            xanchor='left',
                            x=1.02
                        )
                    )
                    
                    fig.update_traces(line=dict(width=2.5))
                    
                    st.plotly_chart(fig, use_container_width=True, key="skills_demand_chart")
                else:
                    st.info(f"No skills data available for {selected_skills_sector}")
            else:
                st.info("No date information available in skills data.")
        else:
            st.info("Skills data file not found or empty.")

    # --- TAB 3: SKILL & EXPERIENCE ---
    with tab3:
        st.subheader("🛠️ Skill & Experience Analysis")
        st.markdown("Objective: Align the \"Level\" of training with market reality to ensure graduate ROI.")
        
        # Add sector filter at top
        exp_comp_sectors = ['All'] + sorted(df['category'].unique().tolist())
        selected_exp_sector = st.selectbox("Filter by Sector:", exp_comp_sectors, key="tab3_sector_filter")
        
        # Get cached metrics
        pay_scale, gate_df = get_experience_metrics(df, selected_exp_sector)
        
        c3a, c3b = st.columns(2)
        
        with c3a:
            st.markdown("#### Seniority Pay-Scale")
            st.caption("Average salary by experience level")
            pay_scale = pay_scale.sort_values('exp_segment')
            
            # Use Altair for simpler, faster rendering
            pay_chart = alt.Chart(pay_scale).mark_bar().encode(
                x=alt.X('exp_segment:N', title='Experience Level', axis=alt.Axis(labelAngle=-45)),
                y=alt.Y('avg_salary:Q', title='Avg Salary (SGD)'),
                color=alt.Color('avg_salary:Q', scale=alt.Scale(scheme='blues'), legend=None),
                tooltip=['exp_segment', alt.Tooltip('avg_salary:Q', format=',.0f')]
            ).properties(height=400, title="Salary by Seniority")
            st.altair_chart(pay_chart, use_container_width=True)
        
        with c3b:
            st.markdown("#### The \"Experience Gate\"")
            st.caption("Vacancies accessible at each tier")
            gate_df = gate_df.sort_values('exp_segment')
            
            gate_chart = alt.Chart(gate_df).mark_bar().encode(
                x=alt.X('exp_segment:N', title='Experience Level', axis=alt.Axis(labelAngle=-45)),
                y=alt.Y('num_vacancies:Q', title='Vacancies'),
                color=alt.Color('num_vacancies:Q', scale=alt.Scale(scheme='viridis'), legend=None),
                tooltip=['exp_segment', alt.Tooltip('num_vacancies:Q', format=',.0f')]
            ).properties(height=400, title="Market Access by Experience")
            st.altair_chart(gate_chart, use_container_width=True)

    # --- TAB 4: EDUCATION GAP & OPPORTUNITY ---
    with tab4:
        st.subheader("🎓 Educational Gap & Opportunity")
        st.markdown("Objective: Identify \"Blue Ocean\" opportunities where job matching rates are highest.")
        
        # Use cached education metrics
        p2_metrics = get_education_metrics(df)

        # Supply vs Demand Treemap (Keep Plotly for complex visualization)
        st.markdown("#### Supply vs Demand")
        st.caption("Treemap: Rectangle size = Vacancies (demand), Color = Applications (supply).")
        supply_demand = p2_metrics[p2_metrics['category'] != 'Others'].copy()
        supply_demand = supply_demand.sort_values('num_vacancies', ascending=False).head(20)
        
        fig_supply_demand = px.treemap(
            supply_demand, path=[px.Constant("All Sectors"), 'category'],
            values='num_vacancies', color='num_applications',
            color_continuous_scale='RdYlGn_r',
            labels={'num_vacancies': 'Vacancies (Size)', 'num_applications': 'Applications (Color)'},
            title='Supply vs Demand Treemap',
            hover_data=['num_vacancies', 'num_applications']
        )
        st.plotly_chart(fig_supply_demand, use_container_width=True, key="supply_demand_treemap")

        # Hidden Demand (Keep Plotly for scatter with quadrants) - BY JOB TITLE
        st.markdown("#### The \"Hidden Demand\"")
        st.caption("Quadrant analysis by job title: High vacancies + Low applications = Hidden opportunities.")
        
        # Create metrics by job title instead of category
        title_metrics = df.groupby('jobtitle_cleaned').agg({
            'num_vacancies': 'sum',
            'num_applications': 'sum',
            'min_exp': 'mean',
            'job_id': 'count'
        }).reset_index()
        
        title_metrics['opp_score'] = title_metrics['num_vacancies'] / (title_metrics['min_exp'] + 1)
        title_metrics['comp_index'] = title_metrics.apply(
            lambda x: x['num_applications'] / x['num_vacancies'] if x['num_vacancies'] > 0 else 0,
            axis=1
        )
        
        hidden_demand = title_metrics.copy()
        
        if len(hidden_demand) > 0:
            # Sample to show top 50 job titles by vacancy count
            if len(hidden_demand) > 50:
                hidden_demand = hidden_demand.nlargest(50, 'num_vacancies')
            
            median_vac = hidden_demand['num_vacancies'].median()
            median_app = hidden_demand['num_applications'].median()
            
            def assign_quadrant(row):
                if row['num_vacancies'] >= median_vac and row['num_applications'] < median_app:
                    return 'Hidden Opportunity'
                elif row['num_vacancies'] >= median_vac and row['num_applications'] >= median_app:
                    return 'Competitive Market'
                elif row['num_vacancies'] < median_vac and row['num_applications'] < median_app:
                    return 'Niche Market'
                else:
                    return 'Oversupplied'
            
            hidden_demand['quadrant'] = hidden_demand.apply(assign_quadrant, axis=1)
            hidden_demand['title_text'] = hidden_demand.apply(
                lambda row: '' if row['quadrant'] == 'Niche Market' else row['jobtitle_cleaned'], axis=1
            )
            
            fig_hidden = px.scatter(
                hidden_demand, x='num_vacancies', y='num_applications',
                size='num_vacancies', color='quadrant',
                hover_name='jobtitle_cleaned', text='title_text',
                labels={'num_vacancies': 'Vacancies', 'num_applications': 'Applications'},
                title='Hidden Demand Quadrant Analysis (by Job Title)',
                color_discrete_map={
                    'Hidden Opportunity': '#28B463',
                    'Competitive Market': '#E67E22',
                    'Niche Market': '#95A5A6',
                    'Oversupplied': '#E74C3C'
                }
            )
            fig_hidden.update_traces(textposition='top center', textfont_size=8)
            fig_hidden.add_hline(y=median_app, line_dash="dash", line_color="gray", 
                               annotation_text=f"Median Apps: {median_app:.0f}")
            fig_hidden.add_vline(x=median_vac, line_dash="dash", line_color="gray",
                               annotation_text=f"Median Vacancies: {median_vac:.0f}")
            fig_hidden.update_layout(height=600)
            st.plotly_chart(fig_hidden, use_container_width=True, key="hidden_demand_chart")


if __name__ == "__main__":
    main()
