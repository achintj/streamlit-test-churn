import streamlit as st
import pandas as pd
import numpy as np
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
from datetime import datetime, timedelta
import uuid

# --- Dummy Data Generation ---
def generate_dummy_data(num_customers=100):
    """Generates a Pandas DataFrame with dummy customer data, including a complex journey."""
    products = ['Broadband Plan A', 'TV Package B', 'Mobile Plan C', 'Sports Add-on', 'Movie Bundle']
    data = {
        'CustomerID': [str(uuid.uuid4())[:8] for _ in range(num_customers)],
        'Name': [f"{first} {last}" for first, last in zip(np.random.choice(['John', 'Jane', 'Peter', 'Mary', 'David', 'Sarah'], size=num_customers), np.random.choice(['S', 'J', 'P', 'M', 'D', 'A'], size=num_customers))],
        'Age': np.random.randint(18, 70, size=num_customers),
        'Gender': np.random.choice(['Male', 'Female'], size=num_customers),
        'TenureMonths': np.random.randint(1, 72, size=num_customers),
        'Contract': np.random.choice(['Month-to-month', 'One year', 'Two year'], size=num_customers),
        'MonthlyCharges': np.random.uniform(20, 120, size=num_customers).round(2),
        'NumSupportTickets': np.random.randint(0, 5, size=num_customers),
        'LastInteractionDays': np.random.randint(0, 365, size=num_customers),
        'SignUpDate': [datetime.now() - timedelta(days=np.random.randint(30, 2000)) for _ in range(num_customers)],
        'Churn': np.random.choice([0, 1], size=num_customers, p=[0.7, 0.3])
    }
    df = pd.DataFrame(data)
    
    # Generate complex event history for each customer
    all_journey_events = []
    for index, row in df.iterrows():
        events = []
        # Purchases
        for _ in range(np.random.randint(1, 10)):
            events.append({
                'type': 'Purchase',
                'details': np.random.choice(products),
                'date': row['SignUpDate'] + timedelta(days=np.random.randint(0, row['TenureMonths'] * 30))
            })
        # Support Tickets
        for _ in range(row['NumSupportTickets']):
            events.append({
                'type': 'Support Ticket',
                'details': f"Issue #{_ + 1}",
                'date': row['SignUpDate'] + timedelta(days=np.random.randint(0, row['TenureMonths'] * 30))
            })
        # Website Logins
        for _ in range(np.random.randint(5, 50)):
             events.append({
                'type': 'Login',
                'details': 'Website Login',
                'date': row['SignUpDate'] + timedelta(days=np.random.randint(0, row['TenureMonths'] * 30))
            })
        # Email Opens
        for _ in range(np.random.randint(10, 30)):
             events.append({
                'type': 'Email Open',
                'details': 'Marketing Email',
                'date': row['SignUpDate'] + timedelta(days=np.random.randint(0, row['TenureMonths'] * 30))
            })
        
        all_journey_events.append(sorted(events, key=lambda x: x['date']))

    df['JourneyEvents'] = all_journey_events
    return df

# --- Churn Prediction (Probability Score) ---
def predict_churn_probability(df):
    """Calculates a churn probability score for each customer."""
    df['ChurnProbability'] = 0.0
    df.loc[df['TenureMonths'] < 12, 'ChurnProbability'] += 0.2
    df.loc[df['Contract'] == 'Month-to-month', 'ChurnProbability'] += 0.25
    df.loc[df['NumSupportTickets'] > 3, 'ChurnProbability'] += 0.3
    df.loc[df['LastInteractionDays'] > 180, 'ChurnProbability'] += 0.25
    df['ChurnProbability'] = df['ChurnProbability'].clip(0, 1)
    return df

# --- Company-Wide Churn Forecast ---
def generate_company_churn_forecast(df):
    """Generates a simple 12-month churn forecast for the whole company, in percentages."""
    current_churn_rate = df['ChurnProbability'].mean() * 100
    forecast = []
    
    for i in range(12):
        month_name = (datetime.now() + timedelta(days=i*30)).strftime('%Y-%m')
        # Fluctuate around the current rate, with a slight upward trend
        forecast_rate = current_churn_rate + (i * 0.05) + np.random.uniform(-0.5, 0.5)
        forecast.append({
            'Month': month_name, 
            'Forecasted Churn Rate (%)': max(0, forecast_rate)
        })
        
    return pd.DataFrame(forecast).set_index('Month')

# --- Recommendations ---
def get_churn_recommendations(customer_data):
    """Generates recommendations to prevent churn for a specific customer."""
    recommendations = []
    if customer_data['ChurnProbability'] > 0.6:
        recommendations.append("🔥 **High-Risk Customer:** Prioritize immediate intervention.")
    if customer_data['NumSupportTickets'] > 2:
        recommendations.append("📞 **Proactive Support Call:** Reach out to resolve outstanding issues and offer dedicated support.")
    if customer_data['Contract'] == 'Month-to-month' and customer_data['TenureMonths'] > 6:
        recommendations.append("💰 **Offer Discount for Annual Plan:** Send a targeted email with a 15% discount to upgrade to a yearly contract.")
    if customer_data['LastInteractionDays'] > 90:
        recommendations.append("📧 **Re-engagement Email Campaign:** Add to a campaign showcasing new features or offering a special promotion.")
    if not recommendations:
        recommendations.append("✅ **Low Churn Risk:** Monitor customer and ensure continued satisfaction.")
    return recommendations

# --- UI Components ---
def create_customer_card(customer_series):
    """Creates a single HTML card for a customer with a portrait avatar and improved hover effect."""
    avatar_url = f"https://i.pravatar.cc/80?u={customer_series['CustomerID']}"
    card_html = f"""
    <div class="customer-card">
        <div class="card-main-content">
            <img src="{avatar_url}" alt="avatar" onerror="this.onerror=null;this.src='https://placehold.co/80x80/E8F0FE/4285F4?text=??';">
            <div class="card-info">
                <h4>{customer_series['Name']}</h4>
                <p>ID: {customer_series['CustomerID']}</p>
                <div class="churn-prob" style="color: #EA4335;">Risk: {customer_series['ChurnProbability']:.0%}</div>
            </div>
        </div>
        <div class="card-details">
            <p><strong>Age:</strong> {customer_series['Age']}</p>
            <p><strong>Tenure:</strong> {customer_series['TenureMonths']} months</p>
            <p><strong>Contract:</strong> {customer_series['Contract']}</p>
        </div>
    </div>
    """
    return card_html

# --- Customer Journey Visualization ---
def create_customer_journey_graph(customer_id, df):
    """Creates a visually appealing, hub-and-spoke network graph of the customer's journey."""
    customer_data = df[df['CustomerID'] == customer_id].iloc[0]
    events = pd.DataFrame(customer_data['JourneyEvents'])
    
    net = Network(height='800px', width='100%', bgcolor='#F8F9FA', font_color='#333333', notebook=True, directed=False)
    
    colors = {
        'Customer': '#4285F4', # Google Blue
        'Hub': '#FBBC05',      # Google Yellow
        'Purchase': '#34A853', # Google Green
        'Support': '#EA4335',  # Google Red
        'Engagement': '#70757a',# Google Grey
        'Churn': '#000000'
    }

    net.add_node(customer_id, label=f"Customer\n{customer_id}", color=colors['Customer'], size=30)

    purchases = events[events['type'] == 'Purchase']
    if not purchases.empty:
        hub_id = f"hub_purchase_{customer_id}"
        net.add_node(hub_id, label='Purchases', color=colors['Hub'], size=20)
        net.add_edge(customer_id, hub_id, value=len(purchases))
        for item, group in purchases.groupby('details'):
            item_id = f"item_{item}"
            count = len(group)
            net.add_node(item_id, label=item, title=f"Purchased {count} time(s)", color=colors['Purchase'], size=15)
            net.add_edge(hub_id, item_id, value=count)

    support_tickets = events[events['type'] == 'Support Ticket']
    if not support_tickets.empty:
        hub_id = f"hub_support_{customer_id}"
        net.add_node(hub_id, label='Support', title=f"{len(support_tickets)} tickets", color=colors['Support'], size=20)
        net.add_edge(customer_id, hub_id, value=len(support_tickets))

    logins, emails = events[events['type'] == 'Login'], events[events['type'] == 'Email Open']
    if not (logins.empty and emails.empty):
        hub_id = f"hub_engagement_{customer_id}"
        title = f"{len(logins)} Logins\n{len(emails)} Emails Opened"
        net.add_node(hub_id, label='Engagement', title=title, color=colors['Engagement'], size=20)
        net.add_edge(customer_id, hub_id, value=len(logins) + len(emails))

    if customer_data['ChurnProbability'] > 0.5:
        label = f"Churn Risk\n{customer_data['ChurnProbability']:.0%}"
        net.add_node('ChurnNode', label=label, title=label, color=colors['Churn'], size=25, shape='star')
        net.add_edge(customer_id, 'ChurnNode', value=customer_data['ChurnProbability']*10)

    net.set_options("""
    var options = { "physics": { "barnesHut": { "gravitationalConstant": -8000, "centralGravity": 0.3, "springLength": 95, "springConstant": 0.04, "damping": 0.09, "avoidOverlap": 0.1 }, "maxVelocity": 50, "minVelocity": 0.1, "solver": "barnesHut", "stabilization": { "enabled": true, "iterations": 1000, "fit": true } }, "interaction":{ "dragNodes":true, "dragView": true, "hideEdgesOnDrag": false, "hideNodesOnDrag": false } }
    """)
    return net.generate_html()

# --- Streamlit App ---
st.set_page_config(layout="wide", page_title="Churn Prediction Dashboard")

# --- Custom CSS for Cards and Layout ---
st.markdown("""
<style>
    /* Main App background */
    .stApp {
        background-color: #F8F9FA;
    }
    /* Main Title */
    h1 {
        color: #202124;
        font-weight: 700;
    }
    /* Subheaders */
    h2 {
        color: #202124;
        border-bottom: 2px solid #E8EAED;
        padding-bottom: 0.3rem;
    }
    /* Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #DADCE0;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    /* Customer Card Grid */
    .customer-card-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 1rem;
    }
    /* Individual Customer Card */
    .customer-card {
        position: relative;
        height: 100px;
        padding: 1rem;
        border-radius: 12px;
        background-color: #FFFFFF;
        border: 1px solid #DADCE0;
        transition: all 0.3s ease;
        overflow: hidden;
        cursor: pointer;
    }
    .customer-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 6px rgba(32,33,36,0.1);
        border-color: #9AA0A6;
    }
    .card-main-content {
        display: flex;
        align-items: center;
        height: 100%;
        transition: opacity 0.3s ease;
    }
    .customer-card:hover .card-main-content {
        opacity: 0;
    }
    .customer-card img {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        margin-right: 1rem;
        border: 2px solid #E8EAED;
    }
    .card-info h4 {
        margin: 0;
        font-size: 1.1em;
        font-weight: 600;
        white-space: nowrap;
        color: #202124;
    }
    .card-info p {
        margin: 0;
        font-size: 0.8em;
        color: #5F6368;
    }
    .churn-prob {
        font-weight: 700;
        margin-top: 4px;
    }
    .card-details {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 1rem;
        box-sizing: border-box;
        opacity: 0;
        transform: translateY(10px);
        transition: all 0.3s ease;
        pointer-events: none;
    }
    .customer-card:hover .card-details {
        opacity: 1;
        transform: translateY(0);
    }
    .card-details p {
        margin: 2px 0;
        font-size: 0.9em;
        color: #3C4043;
    }
</style>
""", unsafe_allow_html=True)

st.title("Customer Churn Prediction Dashboard")

# --- Generate Data and Forecast only once ---
if 'df' not in st.session_state:
    st.session_state.df = generate_dummy_data()
    st.session_state.df = predict_churn_probability(st.session_state.df)
    st.session_state.company_forecast_df = generate_company_churn_forecast(st.session_state.df)

df = st.session_state.df
company_forecast_df = st.session_state.company_forecast_df

# --- Main Layout ---
col1, col2 = st.columns((1, 2))

with col1:
    st.header("Churn Insights")
    
    # Key Metrics
    m1, m2 = st.columns(2)
    overall_churn_rate = df[df['Churn'] == 1].shape[0] / df.shape[0]
    at_risk_count = df[df['ChurnProbability'] > 0.5].shape[0]
    m1.metric(label="Overall Churn Rate", value=f"{overall_churn_rate:.1%}")
    m2.metric(label="Customers At Risk", value=at_risk_count)

    # Company Forecast
    st.subheader("Company-Wide Churn Forecast")
    st.line_chart(company_forecast_df)

    # Top 10 Churning Customers
    st.subheader("Top 10 At-Risk Customers")
    top_churners = df.sort_values(by='ChurnProbability', ascending=False).head(10)
    
    st.markdown('<div class="customer-card-grid">', unsafe_allow_html=True)
    for index, customer in top_churners.iterrows():
        st.markdown(create_customer_card(customer), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    

with col2:
    st.header("Customer Journey Explorer")
    
    customer_id = st.selectbox("Select a Customer:", df['CustomerID'])
    
    if customer_id:
        customer_data = df[df['CustomerID'] == customer_id].iloc[0]
        
        # Recommendations
        st.subheader("Recommendations to Prevent Churn")
        recommendations = get_churn_recommendations(customer_data)
        for rec in recommendations:
            st.markdown(f"- {rec}")
            
        # Journey Graph
        st.subheader("Interactive Journey Graph")
        html = create_customer_journey_graph(customer_id, df)
        components.html(html, height=800, scrolling=True)
