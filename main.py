import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import numpy as np
import time
import pandas 
import matplotlib.pyplot as plt
import json
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import plotly.graph_objects as go
import requests
import time
import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import plotly.graph_objs as go
import random

with open('response.json') as json_file:
    data = json.load(json_file)
map_of_game = data["islands"]

def returnShips(enemy = False):
    """if enemy False return our ships"""
    r = requests.get("https://datsblack.datsteam.dev/api/scan", headers = {"X-API-Key": "889f6a73-29fc-4364-9ed8-7640dbb7ddae"})

    list = []

    if enemy:
        for i in range(len(r.json()["scan"]["enemyShips"])): 
            try:
                x = int(r.json()["scan"]["enemyShips"][i]["x"])
                y = int(r.json()["scan"]["enemyShips"][i]["y"])
                lenght = int(r.json()["scan"]["enemyShips"][i]["size"])
                direction = r.json()["scan"]["enemyShips"][i]["direction"]

                list.append([x, y, lenght, direction])
            except:
                pass
    else:
        for i in range(len(r.json()["scan"]["myShips"])): 
            try:
                x = int(r.json()["scan"]["myShips"][i]["x"])
                y = int(r.json()["scan"]["myShips"][i]["y"])
                lenght = int(r.json()["scan"]["myShips"][i]["size"])
                direction = r.json()["scan"]["myShips"][i]["direction"]

                list.append([x, y, lenght, direction])
            except:
                pass

    return list

print(returnShips())

a = np.zeros((2000,2000), 'int')

def printing():
    a = np.zeros((2000,2000), 'int')
    my_ships = returnShips()
    enemy_ships = returnShips(True)

    count = 0
    for i in range(len(map_of_game)):
        kords = map_of_game[i]["start"]
        island = map_of_game[i]["map"]
        island_height = len(island)
        island_width = len(island[0])

        for k in range(island_height):
            for l in range(island_width):
                if kords[0]+k <2000:
                    if kords[1]+l <2000:
                        a[kords[0]+k][kords[1]+l] = 1
                        count +=1
                    else:
                        break
                else:
                    break

    def hz(enemy = False):
        """if enemy False draw our ships"""

        for i in range(len(enemy_ships if enemy else my_ships)):
            x = enemy_ships[i][0] if enemy else my_ships[i][0]
            y = enemy_ships[i][1] if enemy else my_ships[i][1]

            size = enemy_ships[i][2] if enemy else my_ships[i][2]
            facing = enemy_ships[i][3] if enemy else my_ships[i][3]

            color = 3 if enemy else 2

            a[y][x] = color

            match facing:
                case "south":
                    for k in range(size): a[y+k][x] = color

                case "north":
                    for k in range(size): a[y-k][x] = color

                case "west":
                    for k in range(size): a[y][x-k] = color

                case "east":
                    for k in range(size): a[y][x+k] = color

    hz()
    hz(True)
    return a

a = printing()
# Создаем приложение Dash
app = dash.Dash(__name__)

# Создаем массив данных для тестирования (можно заменить своими данными)
data = np.random.randint(0, 2, size=(2000, 2000))

# Создаем тепловую карту с Plotly Express
fig = px.imshow(a, color_continuous_scale='Viridis')

# Сохраняем идентификатор текущего отображения
initial_layout = None

# Настраиваем макет веб-приложения Dash
app.layout = html.Div([
    html.H1("Интерактивная карта 2000x2000 с обновлением по параметрам"),
    dcc.Graph(id='heatmap', figure=fig, style={'height': '100vh', 'width': '100vw'}),
    html.Label("Выберите параметры для обновления графика:"),
    dcc.Slider(
        id='slider-size',
        min=100,
        max=1000,
        step=100,
        marks={i: str(i) for i in range(100, 1100, 100)},
        value=1000,
        tooltip={'placement': 'bottom'},
    ),
    dcc.Slider(
        id='slider-noise',
        min=0,
        max=1,
        step=0.1,
        marks={i/10: str(i/10) for i in range(0, 11)},
        value=0.5,
        tooltip={'placement': 'bottom'},
    ),
    html.Button("Обновить график", id='update-button', n_clicks=0),
])

# Обработчик для обновления графика по параметрам и нажатию кнопки
@app.callback(
    Output('heatmap', 'figure'),
    Input('slider-size', 'value'),
    Input('slider-noise', 'value'),
    Input('update-button', 'n_clicks')
)
def update_heatmap(size, noise, n_clicks):
    # Здесь вы можете обновить данные для графика с учетом параметров size и noise
    
    updated_data = printing()

    updated_fig = px.imshow(updated_data, color_continuous_scale='Viridis')

    return updated_fig

# Запускаем приложение
if __name__ == '__main__':
    app.run_server(debug=True)