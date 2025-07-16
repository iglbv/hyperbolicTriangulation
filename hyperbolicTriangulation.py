from flask import Flask, render_template, request, jsonify
import math
import numpy as np

app = Flask(__name__)

def hyperbolic_distance(u, v):
    """Вычисление гиперболического расстояния между точками в модели Пуанкаре"""
    numerator = 2 * ((u[0]-v[0])**2 + (u[1]-v[1])**2)
    denominator = (1 - (u[0]**2 + u[1]**2)) * (1 - (v[0]**2 + v[1]**2))
    return math.acosh(1 + numerator / denominator)

def hyperbolic_triangulation(points):
    """Триангуляция в гиперболическом пространстве без использования центра"""
    if len(points) < 3:
        return []
    
    # Сортируем точки по углу для правильного порядка
    sorted_indices = sorted(range(len(points)), 
                          key=lambda i: math.atan2(points[i][1], points[i][0]))
    
    # Создаем треугольники между последовательными точками
    triangles = []
    for i in range(1, len(sorted_indices)-1):
        triangles.append([
            sorted_indices[0],
            sorted_indices[i],
            sorted_indices[i+1]
        ])
    
    return triangles

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/triangulate', methods=['POST'])
def triangulate():
    try:
        data = request.json
        points = data['points']
        
        # Преобразуем точки в координаты модели Пуанкаре
        poincare_points = []
        for p in points:
            x = (p['x'] - 250) / 200
            y = (250 - p['y']) / 200
            poincare_points.append((x, y))
        
        # Выполняем триангуляцию
        triangles_indices = hyperbolic_triangulation(poincare_points)
        
        # Вычисляем матрицу расстояний
        distances = []
        for i in range(len(poincare_points)):
            row = []
            for j in range(len(poincare_points)):
                if i == j:
                    row.append(0.0)
                else:
                    row.append(hyperbolic_distance(poincare_points[i], poincare_points[j]))
            distances.append(row)
        
        return jsonify({
            'success': True,
            'triangles': triangles_indices,
            'distances': distances
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)