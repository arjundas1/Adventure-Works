import plotly.express as px
import streamlit as st
import pandas as pd
import sqlalchemy as sa
import urllib.parse
import warnings
warnings.filterwarnings("ignore")

# ---- PAGE STYLE ----
st.set_page_config(page_title="Sales Dashboard",
                   page_icon=":bar_chart:",
                   layout="wide")

st_style = """
           <style>
           #MainMenu {visibility: hidden;}
           footer {visibility: hidden;}
           header {visibility: hidden;}
           div.block-container {padding-top:1rem;}
           .css-ysnqb2 e1g8pov64 {margin-top: -75px;}
           </style>
           """

st.markdown(st_style, unsafe_allow_html=True)


#@st.cache_data
def db_conn():
    server = 'ARJUN'
    database = 'AdventureWorksDW2019'
    params = urllib.parse.quote_plus("DRIVER={SQL Server};"
                                     "SERVER="+server+";"
                                     "DATABASE="+database+";"
                                     "Trusted_connection=yes")

    engine = sa.create_engine("mssql+pyodbc:///?odbc_connect={}".format(params))
    qry = """
    select
        fis.SalesOrderNumber,
        year(fis.OrderDate) 'Year',
        datename(mm, fis.OrderDate) 'Month',
        fis.SalesAmount,
        fis.OrderQuantity,
        fis.TotalProductCost,
        dc.FirstName + ' ' + dc.LastName 'Customer',
        dc.Gender,
        dst.SalesTerritoryCountry,
        dpc.EnglishProductCategoryName
    from FactInternetSales fis
    left join DimSalesTerritory dst 
        on fis.SalesTerritoryKey = dst.SalesTerritoryKey
        left join DimCustomer dc
            on fis.CustomerKey = dc.CustomerKey
            left join DimProduct dp
                on fis.ProductKey = dp.ProductKey
                left join DimProductSubcategory dps
                    on dp.ProductSubcategoryKey = dps.ProductSubcategoryKey
                    left join DimProductCategory dpc
                        on dps.ProductCategoryKey = dpc.ProductCategoryKey
    """
    with engine.connect() as con:
        df = pd.read_sql(qry, con)
    return df


df = db_conn()
print(df.head())

years = df["Year"].unique().tolist()
countries = df["SalesTerritoryCountry"].unique().tolist()
genders = df["Gender"].unique().tolist()
categories = df["EnglishProductCategoryName"].unique().tolist()

st.sidebar.header("Filtering")

year = st.sidebar.multiselect(
    "Select the year",
    options=years,
    default=years)

country = st.sidebar.multiselect(
    "Select the country",
    options=countries,
    default=countries)

gender = st.sidebar.multiselect(
    "Select the customer gender",
    options=genders,
    default=genders)

category = st.sidebar.multiselect(
    "Select the product category",
    options=categories,
    default=categories)

if year:
    year_list = year
else:
    year_list = years

if country:
    country_list = country
else:
    country_list = countries

if gender:
    gender_list = gender
else:
    gender_list = genders

if category:
    category_list = category
else:
    category_list = categories

df_selection = df.query("Year == @year_list & SalesTerritoryCountry == @country_list & Gender == @gender_list & EnglishProductCategoryName == @category_list")
df_selection_country = df.query("Year == @year_list & Gender == @gender_list & EnglishProductCategoryName == @category_list")
df_selection_gender = df.query("Year == @year_list & SalesTerritoryCountry == @country_list & EnglishProductCategoryName == @category_list")
df_selection_category = df.query("Year == @year_list & SalesTerritoryCountry == @country_list & Gender == @gender_list")

st.title(":bar_chart: Sales Dashboard")
st.markdown("##")


total_sales = df_selection["SalesAmount"].count()
total_sales_amount = df_selection["SalesAmount"].sum()
average_sales = df_selection["SalesAmount"].mean()
top_category = df_selection["EnglishProductCategoryName"].mode()

left_column, middle_column1, middle_column2, right_column = st.columns(4)
with left_column:
    text1 = '<p style="font-family:sans-serif; color:White; font-size: 25px;">Total Sales: 📖 </p>'
    text2 = f'<p style="font-family:sans-serif; color:White; font-size: 20px;">{total_sales}</p>'
    st.markdown(text1, unsafe_allow_html=True)
    st.markdown(text2, unsafe_allow_html=True)
with middle_column1:
    text1 = '<p style="font-family:sans-serif; color:White; font-size: 25px;">Total Sales Amount: 💰 </p>'
    text2 = f'<p style="font-family:sans-serif; color:White; font-size: 20px;">US $ {total_sales_amount:,.2f}</p>'
    st.markdown(text1, unsafe_allow_html=True)
    st.markdown(text2, unsafe_allow_html=True)
with middle_column2:
    text1 = '<p style="font-family:sans-serif; color:White; font-size: 25px;">Average Sales Amount: 💵 </p>'
    text2 = f'<p style="font-family:sans-serif; color:White; font-size: 20px;">US $ {average_sales:,.2f}</p>'
    st.markdown(text1, unsafe_allow_html=True)
    st.markdown(text2, unsafe_allow_html=True)
with right_column:
    text1 = '<p style="font-family:sans-serif; color:White; font-size: 25px;">Top Category: 🏆 </p>'
    text2 = f'<p style="font-family:sans-serif; color:White; font-size: 20px;">{top_category[0]}</p>'
    st.markdown(text1, unsafe_allow_html=True)
    st.markdown(text2, unsafe_allow_html=True)

st.write("---")

chart1 = df_selection_country.groupby("SalesTerritoryCountry").sum()[["SalesAmount", "TotalProductCost"]]
fig_chart1 = px.bar(
    chart1,
    x=chart1.index,
    y=["SalesAmount", "TotalProductCost"],
    title="<b>TOTAL SALES AMOUNT vs TOTAL COST BY COUNTRY</b>",
    template="plotly_white",
    barmode="group",
    color_discrete_sequence=["#FFD184", "#E2AA00"],
    text_auto="$.2s"
)

fig_chart1.update_layout(
    autosize=True,
    uniformtext_minsize=12,
    uniformtext_mode='hide',
    yaxis_title=None,
    xaxis_title=None,
    yaxis={'visible':False, 'showticklabels':False},
    xaxis=dict(tickfont=dict(size=14)),
    legend=dict(orientation='h', yanchor='top', xanchor='center', x=0.5, y=-0.15, title=None, font=dict(size=15)),
    title={'x':0.5, 'xanchor':'center'}
)

fig_chart1.update_traces(textposition="outside", marker_line_color='#00172B', marker_line_width=4, opacity=1)


chart2 = df_selection.groupby("Month", as_index=False).sum()[["Month", "OrderQuantity"]]
chart2["Month"]=pd.Categorical(chart2["Month"],["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
chart2.sort_values("Month", inplace=True, ascending=False)
fig_chart2 = px.bar(
    chart2,
    x=["OrderQuantity"],
    y=chart2.Month,
    title="<b>TOTAL OF SALES BY MONTH</b>",
    template="plotly_white",
    orientation="h",
    text_auto=True,
    color_discrete_sequence=["#4472C4"]
)

fig_chart2.update_layout(
    uniformtext_minsize=12,
    uniformtext_mode='hide',
    yaxis_title=None,
    xaxis_title=None,
    xaxis={'visible':False, 'showticklabels':False},
    yaxis=dict(tickfont=dict(size=14)),
    height=900,
    showlegend=False,
    title={'x':0.5, 'xanchor':'center'}
)

fig_chart2.update_traces(textposition="inside", marker_line_color=None,
                         marker_line_width=0, opacity=1)


chart3 = df_selection_category.groupby("EnglishProductCategoryName").sum()[["OrderQuantity"]]
fig_chart3 = px.pie(
    chart3,
    values="OrderQuantity",
    title="<b>SALES BY CATEGORY</b>",
    names=chart3.index,
    color_discrete_sequence=["#4472C4", "#5B9BD5", "#A5A5A5"],
)

fig_chart3.update_layout(
    uniformtext_minsize=14,
    uniformtext_mode='hide',
    height=400,
    title={'x':0.5, 'xanchor':'center'}
)

fig_chart3.update_traces(
    hoverinfo='label+percent',
    marker=dict(line=dict(color="#00172B", width=4)))


chart4 = df_selection_gender.groupby("Gender").sum()[["OrderQuantity"]]
fig_chart4 = px.pie(
    chart4,
    values="OrderQuantity",
    title="<b>SALES BY GENDER</b>",
    hole=.45,
    names=chart4.index,
    color_discrete_sequence=["#FFD184", "#E2AA00"]
)

fig_chart4.update_layout(
    uniformtext_minsize=14,
    uniformtext_mode='hide',
    height=380,
    title={'x':0.5, 'xanchor':'center'}
)

fig_chart4.update_traces(
    insidetextfont={'color':'black'},
    hoverinfo='label+percent', textinfo='percent+label',
    marker=dict(line=dict(color="#00172B", width=4)),
    showlegend=False
)

left_column, right_column = st.columns(2)

with left_column:
    st.plotly_chart(fig_chart1, use_container_width=True)
    st.plotly_chart(fig_chart3, use_container_width=True)
    st.plotly_chart(fig_chart4, use_container_width=True)

with right_column:
    st.plotly_chart(fig_chart2, use_container_width=True)
