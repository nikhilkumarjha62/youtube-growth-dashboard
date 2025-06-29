import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("📺 YouTube Channel Growth Dashboard")

# Load data
@st.cache_data
def load_data():
    channels = pd.read_csv("C:/Users/Lenovo/Downloads/media_dashboard_project/data/df_channels_en.tsv.gz", sep="\t")
    timeseries = pd.read_csv("C:/Users/Lenovo/Downloads/media_dashboard_project/data/df_timeseries_en.tsv.gz", sep="\t")
    return channels, timeseries

channels_df, timeseries_df = load_data()

# Preprocessing
timeseries_df['datetime'] = pd.to_datetime(timeseries_df['datetime'], errors='coerce')
growth_df = timeseries_df.groupby('channel').agg({
    'delta_views': 'mean',
    'delta_subs': 'mean'
}).reset_index()
growth_df.rename(columns={
    'delta_views': 'avg_weekly_view_growth',
    'delta_subs': 'avg_weekly_sub_growth'
}, inplace=True)

channels_df = channels_df.rename(columns={'channel_id': 'channel'})
growth_merged_df = pd.merge(channels_df, growth_df, on='channel')

# Sidebar filters
categories = sorted(growth_merged_df['category_cc'].dropna().unique())
selected_categories = st.sidebar.multiselect("Select Categories", categories, default=categories[:5])

view_min, view_max = st.sidebar.slider("View Growth Range", 
    int(growth_merged_df['avg_weekly_view_growth'].min()), 
    int(growth_merged_df['avg_weekly_view_growth'].max()), 
    (10000, 100000))

subs_min, subs_max = st.sidebar.slider("Subscriber Growth Range", 
    int(growth_merged_df['avg_weekly_sub_growth'].min()), 
    int(growth_merged_df['avg_weekly_sub_growth'].max()), 
    (1000, 10000))

min_videos = st.sidebar.slider("Minimum Video Count", 
    int(growth_merged_df['videos_cc'].min()), 
    int(growth_merged_df['videos_cc'].max()), 
    int(growth_merged_df['videos_cc'].min()))

filtered_df = growth_merged_df[
    (growth_merged_df['category_cc'].isin(selected_categories)) &
    (growth_merged_df['avg_weekly_view_growth'] >= view_min) &
    (growth_merged_df['avg_weekly_view_growth'] <= view_max) &
    (growth_merged_df['avg_weekly_sub_growth'] >= subs_min) &
    (growth_merged_df['avg_weekly_sub_growth'] <= subs_max) &
    (growth_merged_df['videos_cc'] >= min_videos)
]

# Display filtered data
st.subheader("🎯 Filtered Channels")
st.dataframe(filtered_df[['name_cc', 'category_cc', 'avg_weekly_view_growth', 'avg_weekly_sub_growth']].sort_values("avg_weekly_view_growth", ascending=False))

# Visualization 1: Top 10 Channels by View Growth
top_views = filtered_df.sort_values("avg_weekly_view_growth", ascending=False).head(10)
st.subheader("🔥 Top 10 Channels by Avg Weekly View Growth")
fig1, ax1 = plt.subplots(figsize=(12, 6))
sns.barplot(data=top_views, x="avg_weekly_view_growth", y="name_cc", palette="rocket", ax=ax1)
ax1.set_xlabel("Avg Weekly View Growth")
ax1.set_ylabel("Channel")
st.pyplot(fig1)

# Visualization 2: Scatterplot
st.subheader("📊 View vs Subscriber Growth by Category")
fig2, ax2 = plt.subplots(figsize=(12, 6))
sns.scatterplot(
    data=filtered_df,
    x="avg_weekly_view_growth",
    y="avg_weekly_sub_growth",
    hue="category_cc",
    size="videos_cc",
    sizes=(50, 500),
    alpha=0.7,
    ax=ax2
)
ax2.set_xlabel("Avg Weekly View Growth")
ax2.set_ylabel("Avg Weekly Subscriber Growth")
ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
st.pyplot(fig2)

# Visualization 3: Growth Over Time (Line Chart)
st.subheader("📈 Weekly Growth of a Selected Channel")
selected_channel = st.selectbox("Pick a channel", filtered_df['name_cc'].dropna().unique())
selected_id = filtered_df[filtered_df['name_cc'] == selected_channel]['channel'].values[0]
channel_ts = timeseries_df[timeseries_df['channel'] == selected_id]
fig3, ax3 = plt.subplots(figsize=(12, 6))
sns.lineplot(data=channel_ts, x="datetime", y="views", color="teal", label="Views", ax=ax3)
sns.lineplot(data=channel_ts, x="datetime", y="subs", color="orange", label="Subscribers", ax=ax3)
ax3.set_title(f"Weekly Views and Subs for {selected_channel}")
ax3.set_ylabel("Count")
ax3.set_xlabel("Week")
st.pyplot(fig3)

# Visualization 4: Correlation Heatmap
st.subheader("🧠 Correlation of Growth Metrics")
numeric_cols = growth_merged_df[["avg_weekly_view_growth", "avg_weekly_sub_growth", "subscribers_cc", "videos_cc"]]
corr = numeric_cols.corr()
fig4, ax4 = plt.subplots(figsize=(8, 6))
sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax4)
st.pyplot(fig4)

# Visualization 5: Category Average Growth
st.subheader("📂 Avg Weekly View Growth by Category")
cat_avg = growth_merged_df.groupby("category_cc")["avg_weekly_view_growth"].mean().sort_values()
fig5, ax5 = plt.subplots(figsize=(10, 6))
sns.barplot(x=cat_avg.values, y=cat_avg.index, palette="viridis", ax=ax5)
ax5.set_xlabel("Avg Weekly View Growth")
ax5.set_ylabel("Category")
st.pyplot(fig5)
