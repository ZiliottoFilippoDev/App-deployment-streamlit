import streamlit as st
import PIL
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
import plotly.express as px

@st.cache
def reshape(img_array):
    image = img_array
    row = image.shape[0]
    col = image.shape[1]
    num = row*col
    r = image[:,:,0].reshape((1,num)).flatten()
    g = image[:,:,1].reshape((1,num)).flatten()
    b = image[:,:,2].reshape((1,num)).flatten()
    d = {'r':r, 'g': g, 'b':b}
    matrix = pd.DataFrame(d).to_numpy()
    return matrix

@st.cache
def color_palette(matrix, n=5):
    kmeans = KMeans(n_clusters=n, random_state=0).fit(matrix)

    centers = kmeans.cluster_centers_
    centers = np.around(centers,0).astype(int)
    centers.sort(axis=0)
    centers = centers.reshape(1,centers.shape[0],3)
    centers = np.concatenate((centers, centers), axis=0)
    return centers

def plot(centers):
    img_rgb = np.array(centers, dtype=np.uint8)
    fig = px.imshow(img_rgb, aspect='equal')

    fig.update_yaxes(automargin=True)
    fig.update_layout(coloraxis_showscale=False)
    fig.update_yaxes(visible=False, showticklabels=False)
    fig.update_xaxes(visible=False, showticklabels=False)
    fig.update_layout(hovermode=False)
    return st.plotly_chart(fig)

img_orig = 'film.jpg'   
image = PIL.Image.open(img_orig)
img_array = np.array(image)


img_file_buffer = st.file_uploader('Upload an image', type=['png','jpg','jpeg'])

col1, col2, col3 = st.beta_columns([2,4,2])
if img_file_buffer is not None:
    img_orig = img_file_buffer
    image = PIL.Image.open(img_orig)
    img_array = np.array(image)
    with col2:
        st.write("Image Uploaded Successfully!")


col1, col2, col3 = st.beta_columns([2,4,2])
with col1:
    st.image(img_orig,'Demo Image...',width=500 )
with col3:
    pal = st.radio('Select the n° of color palettes',
                      (5,6,7,8,9,10,20))
if pal: n=pal
else: n=5
matrix = reshape(img_array)
centers = color_palette(matrix, n)

col1, col2, col3 = st.beta_columns([2,4,2])
with col1:
    plot(centers)


