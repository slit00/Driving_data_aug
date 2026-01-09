import json
from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import os

app = Flask(__name__)

# 좌표 데이터를 저장할 리스트
coordinates_data = []

# 데이터 파일 경로
DATA_FILE = 'markers_data.json'

def load_data():
    global coordinates_data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            coordinates_data = json.load(file)

def save_data():
    with open(DATA_FILE, 'w') as file:
        json.dump(coordinates_data, file)

@app.route('/')
def index():
    load_data()  # 서버 시작 시 데이터 로드
    return render_template('map.html')

@app.route('/get_markers', methods=['GET'])
def get_markers():
    return jsonify(coordinates_data)

@app.route('/add_marker', methods=['POST'])
def add_marker():
    data = request.json
    lat = data.get('lat')
    lon = data.get('lon')
    speed = data.get('speed', 0)
    stop_time = data.get('stop_time', 0)  # 정지시간 기본값 0

    if lat is not None and lon is not None:
        index = len(coordinates_data) + 1
        marker = {'index': index, 'latitude': lat, 'longitude': lon, 'speed': speed, 'stop_time': stop_time}
        coordinates_data.append(marker)
        save_data()  # 데이터 저장
        print(f"New marker added: Index: {index}, Latitude: {lat}, Longitude: {lon}, Speed: {speed}, Stop Time: {stop_time}")
        return jsonify({'status': 'success', 'message': 'Marker added successfully', 'index': index})
    else:
        print("Error: Invalid data received")
        return jsonify({'status': 'error', 'message': 'Invalid data received'}), 400

@app.route('/update_marker', methods=['POST'])
def update_marker():
    data = request.json
    index = data.get('index')
    lat = data.get('lat')
    lon = data.get('lon')
    speed = data.get('speed')
    stop_time = data.get('stop_time')

    if index is not None and lat is not None and lon is not None and speed is not None and stop_time is not None:
        for marker in coordinates_data:
            if marker['index'] == index:
                marker['latitude'] = lat
                marker['longitude'] = lon
                marker['speed'] = speed
                marker['stop_time'] = stop_time
                save_data()  # 데이터 저장
                print(f"Marker updated: Index: {index}, Latitude: {lat}, Longitude: {lon}, Speed: {speed}, Stop Time: {stop_time}")
                return jsonify({'status': 'success', 'message': 'Marker updated successfully'})
        return jsonify({'status': 'error', 'message': 'Marker not found'}), 404
    else:
        return jsonify({'status': 'error', 'message': 'Invalid data received'}), 400

@app.route('/delete_marker', methods=['POST'])
def delete_marker():
    data = request.json
    index = data.get('index')

    if index is not None:
        global coordinates_data
        coordinates_data = [marker for marker in coordinates_data if marker['index'] != index]
        save_data()  # 데이터 저장
        print(f"Marker deleted: Index: {index}")
        return jsonify({'status': 'success', 'message': 'Marker deleted successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid data received'}), 400

@app.route('/delete_all_markers', methods=['POST'])
def delete_all_markers():
    global coordinates_data
    coordinates_data.clear()  # 서버에서 모든 마커 데이터를 제거
    save_data()  # 데이터 저장
    print("All markers deleted.")
    return jsonify({'status': 'success', 'message': 'All markers deleted successfully'})

@app.route('/save_csv', methods=['POST'])
def save_csv():
    df = pd.DataFrame(coordinates_data)
    file_path = 'markers.csv'
    df.to_csv(file_path, index=False)
    print(f"Data saved to {file_path}")
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
