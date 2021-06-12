import streamlit as st
import pandas as pd
import base64
import yfinance as yf
import fbprophet
from datetime import datetime
import plotly.graph_objs as go
#import time
import webbrowser

image='stock_image.jpg'
st.set_option('deprecation.showPyplotGlobalUse', False)

col1, col2, col3, col4, col5, col6 = st.beta_columns([3,1,3,3,1,3])
with col1:
	#text_input = st.text_input(label='Enter some text')
    git_button = st.button(label='My GitHub')

with col6:
	#text_input = st.text_input(label='Enter some text')
    email_button = st.button(label='Email Me :)')
    
if email_button:
    st.text('filippo.ziliotto1999@gmail.com')
        #st.write('filippo.ziliotto1999@gmail.com')
if git_button:
    webbrowser.open_new_tab('https://github.com/ZiliottoFilippoDev/Personal-Projects')
    

    #webbrowser.open_new_tab('https://gmail.com')
#with col2:
    #st.image('github.jpg', width=10)

col1, col2, col3 = st.beta_columns([1,6,1])

with col1:
    st.write("")

with col2:
    st.title('Stock Prediction by Pippo')
    st.image(image,'Simple, fast, interactive ...' , width=500)

with col3:
    st.write("")
st.write('')

st.sidebar.header('Personalize your analysis')

# Web scraping of S&P 500 data
#
@st.cache
def load_data():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    html = pd.read_html(url, header = 0)
    df = html[0]
    return df

def icon(icon_name):
    st.markdown(f'<i class="material-icons">{icon_name}</i>', unsafe_allow_html=True)   


def remote_css(url):
    st.markdown(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)    

def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="SP500.csv">Download CSV File</a>'
    return href

df = load_data()
df = df.sort_values('Security', ascending=True).reset_index(drop=True)

st.write('List of the  most known 500 companies:')
st.dataframe(df.style.set_properties(**{'background-color': 'black',
                           'color': 'green'}))
col1, col2, col3 = st.beta_columns([2,3,2])
with col1:
    st.write('**source:** [Wikipedia](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies).')
with col3:
    st.markdown(filedownload(df), unsafe_allow_html=True)

remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')
icon("search")
selected = st.text_input("Choose the company... (ex. Amazon)", "AMZN")


name = str(selected)


today = datetime.today()
today = datetime(today.year, today.month, today.day)


start_date = st.sidebar.date_input( 'Choose a starting date for the model' , value=datetime(2018, 1, 1), min_value=datetime(2016,1,1),max_value=today )

if df['Symbol'].str.contains(name).any():
    data = yf.download(
        tickers = name,
        period = "ytd",
        interval = "1d",
        group_by = 'ticker',
        auto_adjust = True,
        prepost = True,
        threads = True,
        proxy = None,
        start=start_date,
        end= today
    )
else: st.error('Error: Company not listed or wrong symbol')

def prediction(symbol):
    df = pd.DataFrame(data.Close)
   # global name
    #name = data[symbol].Security
    df['Date'] = df.index
    df=df.reindex(columns=['Date','Close'])
    df = df.rename(columns = {"Date":"ds","Close":"y"})
    df.reset_index(drop=True,inplace=True)
    global df0
    df0=df.copy()
    m = fbprophet.Prophet(yearly_seasonality=seasonality)
    m.fit(df)
    future = m.make_future_dataframe(periods=periods)
    predictions=m.predict(future)
    return predictions


def plotly(predictions,symbol):
    trace1 = go.Scatter(
    name = 'trend',
    mode = 'lines',
    x = list(predictions['ds']),
    y = list(predictions['yhat']),
    marker=dict(
        color='red',
        line=dict(width=1)
    ))
    upper_band = go.Scatter(
    name = 'upper bound',
    mode = 'lines',
    x = list(predictions['ds']),
    y = list(predictions['yhat_upper']),
    line= dict(color='lightblue'),
    fill = 'tonexty')
    
    lower_band = go.Scatter(
    name= 'lower bound',
    mode = 'lines',
    x = list(predictions['ds']),
    y = list(predictions['yhat_lower']),
    line= dict(color='#1705ff'))
    
    tracex = go.Scatter(
    name = 'Actual price',
    mode = 'markers',
    x = list(df0['ds']),
    y = list(df0['y']),
    marker=dict(
      color='darkred',
      line=dict(width=0.5)))
    data = [trace1, lower_band, upper_band, tracex ]

    layout = dict(
             xaxis=dict(title = 'Dates', ticklen=2, zeroline=True),
             yaxis=dict(title = 'Closing Stock Price', ticklen=2, zeroline=True), hovermode='x')

    figure=dict(data=data,layout=layout)
    return st.plotly_chart(figure)

#---------------------------
num_company=1

period = st.sidebar.selectbox(
     'Define the days period to predict',  ('3 Years','1 Year','3 Months','Tomorrow'))
keys = {'3 Years':1095,'1 Year': 365, '3 Months': 90, '1 Month':30,'Tomorrow':1}
periods = keys[period]
season = st.sidebar.selectbox(
    'Does the company have some predictable fluctuations during the year season? (default : no)'
    , ('No','Yes'))
if season == 'Yes':
    seasonality = True
else: seasonality = False



if st.button('Start Analysis'):
    symbol = name
    with st.spinner(text="We are computing the analysis..."):
        pred = prediction(name)
        plotly(pred,name)
        st.balloons()
        
