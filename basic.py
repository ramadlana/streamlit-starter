import streamlit as st
import pandas as pd
import numpy as np

st.write(
    "we can use st.write or just using magic write like using triple quote like this")

st.markdown("""
# Data Frame
Here is using data frame
""")
df = pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40],
    'third column': [1, 2, 3, 4]
})

st.dataframe(df)

"""
# Dataframe styler
to highlight and other customization
"""
dataframe = pd.DataFrame(
    np.random.randn(10, 20),
    columns=('col %d' % i for i in range(20)))

st.dataframe(dataframe.style.highlight_max(axis=0))

"""
# Draw Line Chart
for more API charting libraries we can check here
https://docs.streamlit.io/develop/api-reference#chart-elements
"""
chart_data = pd.DataFrame(
    np.random.randn(30, 4),
    columns=['a', 'b', 'c', 'd'])

"""
## Line Chart
scroll mouse to zoom in and zoom out
"""
st.line_chart(chart_data)
"""
## Scatter
"""
st.scatter_chart(chart_data)

"""
Slider, with the value directly stored to x as variable, COOL!
"""
x = st.slider('x')  # 👈 this is a widget
st.write(x, 'squared is', x * x)


"""
## Session state as variable
"""
st.text_input("Your name", key="name")

# You can access the value at any point with:
yourname = st.session_state.name

st.write("Your name is", yourname, "good morning")

nama_lengkap = st.text_input("Full Name")
st.write("hello ", nama_lengkap)
