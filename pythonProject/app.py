from flask import Flask, request, jsonify, send_file, render_template
import csv
import io

app = Flask(__name__)  # templates/ 자동 인식
markers = []

@app.route("/")
def index():
    # templates/index.html 을 반환
    return render_template("index.html")

@app.route('/add_marker', methods=['POST'])
def add_marker():
    global markers
    marker_data = request.json
    markers.append(marker_data)
    return jsonify({'status': 'success'})

@app.route('/update_marker', methods=['POST'])
def update_marker():
    global markers
    marker_data = request.json
    index = marker_data['index'] - 1
    if index < 0 or index >= len(markers):
        return jsonify({'status': 'fail', 'reason': 'invalid index'}), 400
    markers[index] = marker_data
    return jsonify({'status': 'success'})

@app.route('/delete_all_markers', methods=['POST'])
def delete_all_markers():
    global markers
    markers = []
    return jsonify({'status': 'success'})

@app.route('/save_csv', methods=['POST'])
def save_csv():
    global markers

    text = io.StringIO()
    writer = csv.writer(text)

    for marker in markers:
        writer.writerow([marker['index'], marker['lat'], marker['lon'], marker['speed'], marker['stop_time']])

    # Flask send_file은 BytesIO가 더 안전함(요즘 버전 호환)
    mem = io.BytesIO(text.getvalue().encode("utf-8"))
    mem.seek(0)

    return send_file(
        mem,
        mimetype='text/csv',
        as_attachment=True,
        download_name='markers.csv'
    )

if __name__ == "__main__":
    app.run(debug=True)
