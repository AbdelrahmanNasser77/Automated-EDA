import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.title("Web Application for Data Analysis")

hide_streamlit_style = """
<style>
  #MainMenu {visibility: hidden;}
  footer {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


uploaded_file = st.file_uploader("Upload a dataset", type=["csv", "xlsx" , "xls", "xlsm", "xlsb", "odf", "ods", "odt"], label_visibility="collapsed")

if uploaded_file:
    file_extension = uploaded_file.name.split(".")[-1]
    
    if file_extension == "csv":
        df = pd.read_csv(uploaded_file)
    elif file_extension in ["xlsx", "xls", "xlsx", "xlsm", "xlsb", "odf", "ods" , "odt"]:
        df = pd.read_excel(uploaded_file)

    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(exclude="number").columns.tolist()

    missing_cols = df.columns[df.isna().any()].tolist()

    if missing_cols:
        st.sidebar.header("Handling missing values")

        if "selected_col" not in st.session_state:
            st.session_state.selected_col = None
        if "handling_method" not in st.session_state:
            st.session_state.handling_method = {}
        
        mode = st.sidebar.selectbox("Choose Handling mode", 
                                    options=["--Select--", "Manual", "Auto"], 
                                    key="mode"
                                    )
        if mode == "--Select--":
            st.write(df)

        elif mode == "Manual":
            st.sidebar.header("Choose a column with missing values")
            col = st.sidebar.selectbox("Column", options=missing_cols, key="col")
            st.session_state.selected_col = col
            st.sidebar.text(
                f"Missing values: {df[col].isna().sum()}\nTotal values: {df.shape[0]}\nPercentage: {np.round(df[col].isna().sum() / df.shape[0] * 100)}%"
                )
            
            if col in num_cols:
                option = st.sidebar.selectbox(label=f"How do you want to handle \"{col}\"?", 
                                              options=["--Select--", "Drop", "Fill"], 
                                              key="option"
                                              )
                
                if option == "--Select--":
                    pass

                elif option == "Drop":
                    method = st.sidebar.radio(label="What do you want to drop?", 
                                              options=["Drop rows", f"Drop column \"{col}\""], 
                                              key="method"
                                              )
                    st.session_state.handling_method[col] = (option, method)
                
                elif option == "Fill":
                    method = st.sidebar.radio(label=f"How do you want to fill \"{col}\"?", 
                                              options=["Mean", "Median", "Mode"], 
                                              key="method"
                                              )
                    st.session_state.handling_method[col] = (option, method)

            elif col in cat_cols:
                option = st.sidebar.selectbox(label=f"How do you want to handle \"{col}\"?", 
                                              options=["--Select--", "Drop", "Fill"], 
                                              key="option"
                                              )
                
                if option == "--Select--":
                    pass
                
                elif option == "Drop":
                    method = st.sidebar.radio(label="What do you want to drop?", 
                                              options=["Drop rows", f"Drop column \"{col}\""], 
                                              key="method"
                                              )
                    st.session_state.handling_method[col] = (option, method)
                
                elif option == "Fill":
                    method = st.sidebar.radio(label=f"How do you want to fill \"{col}\"?", 
                                              options=["Mode"], 
                                              key="method"
                                              )
                    st.session_state.handling_method[col] = (option, method)

            for col, method in st.session_state.handling_method.items():
                if method[0] == "--Select--":
                    continue
                
                elif method[0] == "Drop":

                    if method[1] == "Drop rows":
                        df.dropna(subset=[col], inplace=True)
                        
                        if col in num_cols:    
                            num_cols.remove(col)
                        
                        elif col in cat_cols:
                            cat_cols.remove(col)
                        
                    elif method[1] == f"Drop column \"{col}\"":
                        df.drop(col, axis="columns", inplace=True)
                        
                        if col in num_cols:
                            num_cols.remove(col)

                        elif col in cat_cols:
                            cat_cols.remove(col)
                    
                elif method[0] == "Fill":
                    if col in num_cols:

                        if method[1] == "Mean":
                            df[col].fillna(df[col].mean(), inplace=True)

                        elif method[1] == "Median":
                            df[col].fillna(df[col].median(), inplace=True)

                        elif method[1] == "Mode":
                            df[col].fillna(df[col].mode()[0], inplace=True)
                        
                    elif col in cat_cols:                        
                        if method[1] == "Mode":
                            df[col].fillna(df[col].mode()[0], inplace=True)

                
            st.write("Updated dataframe:")
            st.write(df)


        elif mode == "Auto":
            
            st.sidebar.subheader("Filling Method")
            fill_method_num = st.sidebar.selectbox(label="Numerical columns", 
                                                   options=["--Select--", "Mean", "Median", "Mode"], 
                                                   key="fill_method_num"
                                                   )
           
            fill_method_cat = st.sidebar.selectbox(label="Categorical columns", 
                                                   options=["--Select--","Mode"], 
                                                   key="fill_method_cat"
                                                   )
            
            st.sidebar.subheader("Drop Method")
            min_percentage = st.sidebar.number_input(label="Minimum percentage of missing values to Drop", 
                                                     min_value=0,
                                                     max_value=100,
                                                     step=5, 
                                                     key="min_percentage"
                                                     )
            
            drop = st.sidebar.radio(label=f"If percentage of missing values <  {min_percentage} ", 
                                    options=["--Select--","Drop rows", "Drop columns"], 
                                    key="drop"
                                    )
            
            for col in missing_cols:
                percentage = np.round(df[col].isna().sum() / df.shape[0] * 100)
                if percentage < min_percentage:
                    
                    if drop == "--Select--":
                        pass
                    
                    elif drop == "Drop rows":
                        df.dropna(subset=[col], inplace=True)
  
                    elif drop == "Drop columns":
                        df.drop(col, axis="columns", inplace=True)
                        
                        if col in num_cols:    
                            num_cols.remove(col)
                        
                        elif col in cat_cols:
                            cat_cols.remove(col)
                            
                else:
                    if col in num_cols:

                        if fill_method_num == "--Select--":
                            pass

                        elif fill_method_num == "Mean":
                            df[col].fillna(df[col].mean(), inplace=True)

                        elif fill_method_num == "Median":
                            df[col].fillna(df[col].median(), inplace=True)

                        elif fill_method_num == "Mode":
                            df[col].fillna(df[col].mode()[0], inplace=True)

                    elif col in cat_cols:

                        if fill_method_cat == "--Select--":
                            pass

                        elif fill_method_cat == "Mode":
                            df[col].fillna(df[col].mode()[0], inplace=True)

            st.write("Updated dataframe:")
            st.write(df)

    else:
        st.write(df)

    st.sidebar.header("Data Visualisation")
    analysis_method = st.sidebar.selectbox(label= "Select Type of Analysis" , options= [ "--Select--" , "Univariate Analysis" , "Bivariate Analaysis"])

    if analysis_method == "--Select--":
        pass

    elif analysis_method == "Univariate Analysis":

        st.sidebar.header("Choose a column to visualize")

        col = st.sidebar.selectbox(label= "Select a column", options= df.columns)

        if col in num_cols:           
            graph_types = ["Histogram" , "Box Plot"]

            container = st.container()
            placeholders = [container.empty() for _ in graph_types]

            for i, graph_type in enumerate(graph_types):
                checked = st.sidebar.checkbox(graph_type)
                
                if checked:

                    if graph_type == "Histogram":
                        nbins = st.slider(label="Select number of bins" , min_value= 5 , max_value= 50 , step= 5)
                        fig = px.histogram(data_frame= df , x = col, text_auto=True , nbins=nbins )
                        fig.update_layout(bargap = 0.1)
                        fig.update_traces(textposition = "outside" , textfont_size = 15)
                    
                    elif graph_type == "Box Plot":
                        fig = px.box(data_frame= df , y = col)

                    placeholders[i].plotly_chart(fig)

        elif col in cat_cols:
            col_count = df[col].value_counts()
            percentages = df[col].value_counts(normalize = True) * 100

            method = st.sidebar.radio(label= "Choose Selection Method" , 
                                      options=["All" , "Percentage" , "Top"]
                                      )

            if method == "All":
                pass
            
            elif method == "Percentage":
                minimum_percentage = st.sidebar.number_input(label= "Enter Minimum Percentage: ", 
                                                         min_value=1 , 
                                                         max_value=100 , 
                                                         step=1,
                                                         key= "minimum_percentage"
                                                        )

                def filter_func(x): 
                    return x / col_count.sum() > minimum_percentage/100
                
                col_count = col_count[col_count.apply(filter_func)]

            elif method == "Top":
                top_selection = st.sidebar.number_input("Enter: " , min_value=1 , max_value= df.shape[0] , step=1)
                col_count = col_count.head(top_selection)


            graph_types = ["Bar Plot" , "Pie Chart"]

            container = st.container()
            placeholders = [container.empty() for _ in graph_types]
            
            for i, graph_type in enumerate(graph_types):
                checked = st.sidebar.checkbox(graph_type)
                
                if checked:

                    if graph_type == "Bar Plot":
                        fig = px.bar(
                            data_frame=col_count,
                            x=col_count.index, 
                            y="count", 
                            height=576 , 
                            width= 760 , 
                            text= "count" , 
                            color= col_count.values
                            )
                        fig.update_traces(textposition = "outside")
                        fig.update_layout(uniformtext_minsize = 10)
                    
                    elif graph_type == "Pie Chart":
                        fig = px.pie(
                            data_frame= col_count,
                            values= col_count.values,
                            names= col_count.index
                            )
                        fig.update_layout(width=760, height=520)
                        fig.update_layout({'font': {'size': 18}, })
                        fig.update_traces(textposition = 'inside' , textinfo = 'label+percent')


                    placeholders[i].plotly_chart(fig)

        
    elif analysis_method == "Bivariate Analaysis":
        
        same_size_numcols = []

        for col in num_cols :
            if df[col].size == df.shape[0]:
                same_size_numcols.append(col)

        same_size_catcols = []

        for col in cat_cols:
            if df[col].size == df.shape[0]:
                same_size_catcols.append(col)

        same_size_cols = same_size_numcols + same_size_catcols
        
        x_axis = st.sidebar.selectbox(label= "X-axis" , options= same_size_cols)     
        x_axis_count = df[x_axis].value_counts()
     
        y_axis = st.sidebar.selectbox(label= "Y-axis" ,options= df.columns)    
        y_axis_count = df[y_axis].value_counts()

        crossed = pd.crosstab(index= df[x_axis] , columns= df[y_axis])

        if x_axis in cat_cols: 

            x_axis_percentages = df[x_axis].value_counts(normalize = True) * 100

            method = st.sidebar.radio(label= f"Choose Selection Method for \"{x_axis}\" " , 
                                      options=["All" , "Percentage" , "Top"],
                                      key= "x_axis selection"
                                     )

            if method == "All":
                pass
            
            elif method == "Percentage":
                min_percentage = st.sidebar.number_input(label= "Enter Minimum Percentage: ", 
                                                         min_value=1 , 
                                                         max_value=100 , 
                                                         step=1,
                                                         key= "x_axis min percentage"
                                                        )

                def filter_func(x): 
                    return x / x_axis_count.sum() > min_percentage/100
                
                x_axis_count = x_axis_count[x_axis_count.apply(filter_func)]

            elif method == "Top":
                top_selection = st.sidebar.number_input(label= "Enter: " , 
                                                        min_value=1 , 
                                                        max_value= df.shape[0] , 
                                                        step=1,
                                                        key= "x_axis top selection"
                                                        )
                
                x_axis_count = x_axis_count.head(top_selection)

        if y_axis in cat_cols:
            y_axis_percentages = df[y_axis].value_counts(normalize = True) * 100

            method = st.sidebar.radio(label= f"Choose Selection Method for \" {y_axis}\"" , 
                                      options= ["All" , "Percentage" , "Top"],
                                      key= "y_axis selection"
                                      )

            if method == "All":
                pass
            
            elif method == "Percentage":
                min_percentage = st.sidebar.number_input(label= "Enter Minimum Percentage  : ", 
                                                         min_value=1 , 
                                                         max_value=100 , 
                                                         step=1,
                                                         key= "y_axis min percentage"
                                                        )

                def filter_func(x): 
                    return x / y_axis_count.sum() > min_percentage/100
                
                y_axis_count = y_axis_count[y_axis_count.apply(filter_func)]

            elif method == "Top":
                top_selection = st.sidebar.number_input(label= "Enter: ", 
                                                        min_value=1 , 
                                                        max_value= df.shape[0] , 
                                                        step=1,
                                                        key= "y_axis top selection"
                                                        )
                y_axis_count = y_axis_count.head(top_selection)


        df_x = df.loc[df[x_axis].isin(x_axis_count.index)]

        df_y = df.loc[df[y_axis].isin(y_axis_count.index)]

        crossed = pd.crosstab(index=df_x[x_axis], columns=df_y[y_axis])
        
        if x_axis in num_cols:
            graph_types = ["Bar Plot" , "Box Plot", "Line Chart" , "Scatter Plot"]

            container = st.container()
            placeholders = [container.empty() for _ in graph_types]

            for i, graph_type in enumerate(graph_types):
                checked = st.sidebar.checkbox(graph_type)
                
                if checked:

                    if graph_type == "Bar Plot":
                        fig = px.bar(data_frame= crossed , barmode="group", text_auto=True)
                        fig.update_traces(textposition = "outside")
                        fig.update_layout(uniformtext_minsize = 10)
                    
                    elif graph_type == "Box Plot":
                        fig = px.box(data_frame= crossed)

                    elif graph_type == "Line Chart":
                        fig = px.line(data_frame=crossed)

                    elif graph_type == "Scatter Plot":
                        fig = px.scatter(data_frame= crossed)

                    placeholders[i].plotly_chart(fig)

        elif x_axis in cat_cols:            
            bar_chart = px.bar(data_frame= crossed, barmode= "group")
            bar_chart.update_traces(textposition = "outside")
            bar_chart.update_layout(uniformtext_minsize = 10)
            st.plotly_chart(bar_chart)
        
