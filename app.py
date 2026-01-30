import pycountry
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title='Dashboard Salaries',
    page_icon='📊',
    layout='wide'
)

df = pd.read_csv("dados_salariais.csv")

# Filters
st.sidebar.title("Filters")

# Year Filter
available_years = sorted(df['work_year'].unique())
selected_year = st.sidebar.multiselect("Year", available_years, default=available_years)

# Experience Level Filter
experience_levels = df['experience_level'].unique()
selected_experience = st.sidebar.multiselect("Experience Level", experience_levels, default=experience_levels)

# Employment Type Filter
employment_types = df['employment_type'].unique()
selected_employment = st.sidebar.multiselect("Employment Type", employment_types, default=employment_types)

# Company Size Filter
company_sizes = df['company_size'].unique()
selected_company_size = st.sidebar.multiselect("Company Size", company_sizes, default=company_sizes)

df_filtered = df[
    (df['experience_level'].isin(selected_experience)) &
    (df['work_year'].isin(selected_year)) &
    (df['employment_type'].isin(selected_employment)) &
    (df['company_size'].isin(selected_company_size))
    ]

# Principal Content
st.title("Dashboard Salaries")
st.markdown("Created by Caio Cardoso and Guilherme Estrela.")

st.subheader("Key Metrics")

if not df_filtered.empty:
    avg_salary = df_filtered['salary_in_usd'].mean()
    min_salary = df_filtered['salary_in_usd'].min()
    max_salary = df_filtered['salary_in_usd'].max()
    total_registrations = df_filtered.shape[0]
    more_frequently_type = df_filtered['employment_type'].mode()[0]
else:
    avg_salary, min_salary, max_salary, total_registrations, more_frequently_type = 0, 0, 0, 0, "N/A"

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Average Salary", f"${avg_salary:,.2f}")
col2.metric("Minimum Salary", f"${min_salary:,.2f}")
col3.metric("Maximum Salary", f"${max_salary:,.2f}")
col4.metric("Total Registrations", total_registrations)
col5.metric("Most Frequent Employment Type", more_frequently_type)

st.markdown("---")

# Visual Analysis with Plotly

st.subheader("Graphics")

col_graph1, col_graph2 = st.columns(2)

with col_graph1:
    if not df_filtered.empty:
        top_employment_types = df_filtered.groupby('employment_type')['salary_in_usd'].mean().sort_values(ascending=True).reset_index()
        employment_type_graph = px.bar(
            top_employment_types,
            x="salary_in_usd",
            y="employment_type",
            orientation='h',
            title="Top 10 Employment Type by Average Salary",
            labels={"employment_type": "Employment Type", "salary_in_usd": "Average Salary"}
            )
        employment_type_graph.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(employment_type_graph, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")

with col_graph2:
    if not df_filtered.empty:
        hist_graph = px.histogram(
            df_filtered,
            x="salary_in_usd",
            nbins=30,
            title="Annual Salary Distribution",
            labels={"salary_in_usd": "Salary (USD)", 'count': ''}
            )
        hist_graph.update_layout(title_x=0.1)
        st.plotly_chart(hist_graph, use_container_width=True)
        
col_graph3, col_graph4 = st.columns(2)

with col_graph3:
    if not df_filtered.empty:
        remote_work_counts = df_filtered['remote_ratio'].value_counts().reset_index()
        remote_work_counts.columns = ['work_type', 'quantity']
        remote_work_graph = px.pie(
            remote_work_counts,
            names='work_type',
            values='quantity',
            title='Proportion of Remote Work Types',
            hole=0.5
        )
        remote_work_graph.update_traces(textinfo='percent+label')
        remote_work_graph.update_layout(title_x=0.1)
        st.plotly_chart(remote_work_graph, use_container_width=True)
        
def iso2_to_iso3(code):
    try:
        return pycountry.countries.get(alpha_2=code).alpha_3
    except:
        return None
        
df_filtered['residence_iso3'] = df_filtered['employee_residence'].apply(iso2_to_iso3)

df_ds = df_filtered[df_filtered['job_title'] == 'Data Scientist']
avg_salary_by_country = df_ds.groupby('residence_iso3')['salary_in_usd'].mean().reset_index()

with col_graph4:
    if not df_filtered.empty:
        countries_graph = px.choropleth(avg_salary_by_country,
            locations='residence_iso3',
            color='salary_in_usd',
            color_continuous_scale='rdylgn',
            title='Average Data Scientist Salary by Country',
            labels={'salary_in_usd': 'Average Salary (USD)', 'employee_residence': 'Country'})
        countries_graph.update_layout(title_x=0.1)
        st.plotly_chart(countries_graph, use_container_width=True)