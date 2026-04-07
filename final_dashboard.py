from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.express as px

df = pd.read_csv("Final_data.csv")
df["Freq_bin"] = pd.cut(df["Workout_Frequency (days/week)"], bins=4)
df["Freq_bin_str"] = df["Freq_bin"].astype(str)


df["Freq_bin_str"] = pd.Categorical(
    df["Freq_bin_str"],
    categories=sorted(df["Freq_bin_str"].unique(), key=lambda x: float(x.split(",")[0].replace("(",""))),
    ordered=True
)

app = Dash()
app.title = "Fitness Dashboard"

palette_workout = px.colors.qualitative.Set2
palette_category = px.colors.qualitative.Pastel

app.layout = html.Div([

    html.H1("Fitness Dashboard", style={"textAlign": "center", "marginBottom": "30px"}),

    html.Div([

        html.Div([

            html.Div([
                html.Div([
                    html.Label("BMI Range:"),
                    dcc.RangeSlider(
                        id="bmi_slider",
                        min=df["BMI"].min(),
                        max=df["BMI"].max(),
                        value=[df["BMI"].min(), df["BMI"].max()],
                        marks={int(x): str(int(x)) for x in df["BMI"].quantile([0,0.25,0.5,0.75,1])},
                        step=0.1
                    )
                ], style={"width": "25%", "padding": "10px"}),
                html.Div([dcc.Graph(id="fig_bmi")], style={"flex": 1})
            ], style={"display": "flex", "alignItems": "flex-start", "marginBottom": "30px"}),

            html.Div([
                html.Div([
                    html.Label("Workout Frequency (days/week):"),
                    dcc.RangeSlider(
                        id="freq_slider",
                        min=df["Workout_Frequency (days/week)"].min(),
                        max=df["Workout_Frequency (days/week)"].max(),
                        value=[df["Workout_Frequency (days/week)"].min(), df["Workout_Frequency (days/week)"].max()],
                        marks={int(x): str(int(x)) for x in df["Workout_Frequency (days/week)"].unique()},
                        step=1
                    )
                ], style={"width": "25%", "padding": "10px"}),
                html.Div([dcc.Graph(id="fig_freq_box")], style={"flex": 1})
            ], style={"display": "flex", "alignItems": "flex-start", "marginBottom": "30px"}),

        ], style={"flex": 1, "display": "inline-block", "verticalAlign": "top", "marginRight": "2%"}),

        html.Div([

            html.Div([
                html.Div([
                    html.Label("Workout Type:"),
                    dcc.Dropdown(
                        id="workout_dd",
                        options=[{"label": wt, "value": wt} for wt in sorted(df["Workout_Type"].dropna().unique())],
                        value=None,
                        multi=True,
                        placeholder="All Types"
                    )
                ], style={"width": "25%", "padding": "10px"}),
                html.Div([dcc.Graph(id="fig_avg_cal")], style={"flex": 1})
            ], style={"display": "flex", "alignItems": "flex-start", "marginBottom": "30px"}),

            html.Div([
                html.Div([
                    html.Label("Calories Burned Category:"),
                    dcc.Dropdown(
                        id="burns_category_dd",
                        options=[{"label": c, "value": c} for c in ["Low","Medium","High","Very High"]],
                        value=None,
                        multi=True,
                        placeholder="All Categories"
                    )
                ], style={"width": "25%", "padding": "10px"}),
                html.Div([dcc.Graph(id="fig_violin")], style={"flex": 1})
            ], style={"display": "flex", "alignItems": "flex-start", "marginBottom": "30px"}),

        ], style={"flex": 1, "display": "inline-block", "verticalAlign": "top", "marginLeft": "2%"})

    ], style={"display": "flex", "width": "100%"}),

    html.Div([
        html.Div([
            html.Label("Gender:"),
            dcc.Dropdown(
                id="gender_dd",
                options=[{"label": g, "value": g} for g in sorted(df["Gender"].dropna().unique())],
                value=None,
                multi=True,
                placeholder="All Genders"
            )
        ], style={"width": "25%", "padding": "10px"}),
        html.Div([dcc.Graph(id="fig_gender")], style={"flex": 1})
    ], style={"display": "flex", "alignItems": "flex-start", "marginBottom": "30px"})
])


@app.callback(
    Output('fig_bmi', 'figure'),
    Input('bmi_slider', 'value')
)
def update_bmi(bmi_range):
    filtered_df = df[(df["BMI"] >= bmi_range[0]) & (df["BMI"] <= bmi_range[1])]
    return px.histogram(filtered_df, x="BMI", nbins=20, title="BMI Distribution",
                        color_discrete_sequence=[palette_category[0]])

@app.callback(
    Output('fig_avg_cal', 'figure'),
    Input('workout_dd', 'value')
)
def update_avg_cal(workout_types_selected):
    filtered_df = df.copy()
    if workout_types_selected:
        filtered_df = filtered_df[filtered_df["Workout_Type"].isin(workout_types_selected)]
    avg_calories = filtered_df.groupby("Workout_Type")["Calories_Burned"].mean().reset_index()
    return px.bar(avg_calories, x="Workout_Type", y="Calories_Burned", title="Average Calories Burned by Workout Type",
                  color="Workout_Type", color_discrete_sequence=palette_workout)

@app.callback(
    Output('fig_freq_box', 'figure'),
    Input('freq_slider', 'value')
)
def update_freq(freq_range):
    filtered_df = df[(df["Workout_Frequency (days/week)"] >= freq_range[0]) &
                     (df["Workout_Frequency (days/week)"] <= freq_range[1])]
    return px.box(filtered_df, x="Freq_bin_str", y="Calories_Burned",
                  title="Calories Burned by Workout Frequency",
                  category_orders={"Freq_bin_str": df["Freq_bin_str"].cat.categories},
                  color_discrete_sequence=[palette_category[1]])

@app.callback(
    Output('fig_violin', 'figure'),
    Input('burns_category_dd', 'value')
)
def update_violin(selected_categories):
    filtered_df = df.copy()
    if selected_categories:
        filtered_df = filtered_df[filtered_df["Burns_Calories_Bin"].isin(selected_categories)]
    return px.violin(filtered_df, x="Burns_Calories_Bin", y="BMI", box=True, points=False,
                     category_orders={"Burns_Calories_Bin": ["Low","Medium","High","Very High"]},
                     color="Burns_Calories_Bin", color_discrete_sequence=palette_category,
                     title="BMI Distribution by Calories Burned Category")

@app.callback(
    Output('fig_gender', 'figure'),
    Input('gender_dd', 'value')
)
def update_gender(selected_genders):
    filtered_df = df.copy()
    if selected_genders:
        filtered_df = filtered_df[filtered_df["Gender"].isin(selected_genders)]
    return px.box(filtered_df, x="Gender", y="Calories_Burned", color="Workout_Type",
                  title="Calories Burned by Gender & Workout Type", color_discrete_sequence=palette_workout)


if __name__ == "__main__":
    print("Dashboard running on http://127.0.0.1:8050/")
    app.run(debug=True)