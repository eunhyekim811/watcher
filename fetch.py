from flask import Flask, request, jsonify
import os
from collections import defaultdict
from flask_cors import CORS
from datetime import datetime
import pytz

app = Flask(__name__)

BASE_DIR = "/home/ubuntu/Couch"  # OpenStack 인스턴스 내부의 기본 경로

CORS(app)

# 학번과 과제명에 해당하는 코드 파일명을 조회
def list_code_files(student_id, assignment_name):
    path = os.path.join(BASE_DIR, student_id, assignment_name)
    
    if not os.path.exists(path):
        return {"error": "Directory not found"}, 404

    code_files = [entry.name for entry in os.scandir(path) if entry.is_dir()]
    # print(code_files)
    
    return {"path": path, "code_files": code_files}

def get_snapshot_average(student_id, assignment_name):
    """각 코드 파일별 스냅샷 개수의 평균을 계산"""
    path = os.path.join(BASE_DIR, student_id, assignment_name)
    
    if not os.path.exists(path):
        return {"error": "Directory not found"}, 404
    
    snapshot_counts = []  # 각 코드 파일의 스냅샷 개수를 저장
    
    for entry in os.scandir(path):
        if entry.is_dir():  # 코드 파일 디렉터리
            code_file_name = entry.name
            snapshot_dir = os.path.join(path, code_file_name)
            
            snapshot_count = sum(1 for snapshot in os.scandir(snapshot_dir) if snapshot.is_file() and snapshot.name.isdigit())
            snapshot_counts.append(snapshot_count)
    
    if not snapshot_counts:
        return {"error": "No snapshots found"}, 404
    
    average_snapshots = round(sum(snapshot_counts) / len(snapshot_counts), 2)
    print(average_snapshots)
    return {"average_snapshots": average_snapshots}


def list_snapshots(student_id, assignment_name, code_file_name):
    """특정 코드 파일명 아래의 스냅샷 파일 목록 조회"""
    path = os.path.join(BASE_DIR, student_id, assignment_name, code_file_name)

    if not os.path.exists(path):
        return {"error": "Code file directory not found"}, 404

    snapshot_files = []
    for snapshot in os.scandir(path):
        if snapshot.is_file() and snapshot.name.isdigit():
            timestamp = snapshot.name
            size = os.path.getsize(snapshot.path)
            snapshot_files.append({"timestamp": timestamp, "size": size})

    # 스냅샷 파일을 시간순 정렬
    snapshot_files.sort(key=lambda x: x["timestamp"])

    return {"code_file": code_file_name, "snapshots": snapshot_files}


def convert_timestamp(timestamp):
    """Unix timestamp(초)를 대한민국 시간(KST, UTC+9)으로 변환"""
    utc_time = datetime.utcfromtimestamp(int(timestamp))  # UTC 시간 변환
    kst_time = utc_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Seoul'))  # KST 변환
    return kst_time.strftime('%Y-%m-%d %H:%M:%S')  # YYYY-MM-DD HH:MM:SS 형식으로 반환

def get_snapshot_trends(student_id, assignment_name):
    """최하위 모든 스냅샷 파일을 찾아 코드파일명별로 시간당 크기 변화를 반환"""
    path = os.path.join(BASE_DIR, student_id, assignment_name)

    if not os.path.exists(path):
        return {"error": "Directory not found"}, 404

    snapshot_trends = defaultdict(list)  # {코드파일명: [{"timestamp": time, "size": size}, ...]}

    for entry in os.scandir(path):
        if entry.is_dir():  # 코드파일명 디렉터리
            code_file_name = entry.name
            snapshot_dir = os.path.join(path, code_file_name)

            for snapshot in os.scandir(snapshot_dir):
                if snapshot.is_file() and snapshot.name.isdigit():
                    timestamp = snapshot.name
                    # kst_timestamp = convert_timestamp(timestamp)
                    size = os.path.getsize(snapshot.path)
                    snapshot_trends[code_file_name].append({"timestamp": timestamp, "size": size})

            # 각 코드파일별 스냅샷 데이터를 시간순으로 정렬
            snapshot_trends[code_file_name].sort(key=lambda x: x["timestamp"])
            
    # print(snapshot_trends)
    return snapshot_trends


# 과제를 선택하면 코드 파일명을 조회하는 API
@app.route("/codes", methods=["GET"])
def get_code_files():
    """과제를 선택하면 코드 파일명을 조회하는 API"""
    student_id = request.args.get("student_id")
    assignment_name = request.args.get("assignment_name")

    if not student_id or not assignment_name:
        return jsonify({"error": "student_id and assignment_name are required"}), 400

    return jsonify(list_code_files(student_id, assignment_name))

# 코드 파일명을 선택하면 스냅샷 파일 목록을 조회하는 API
@app.route("/snapshots", methods=["GET"])
def get_snapshots():
    """특정 코드 파일명을 선택하면 해당 코드 파일 아래의 스냅샷 목록 조회"""
    student_id = request.args.get("student_id")
    assignment_name = request.args.get("assignment_name")
    code_file_name = request.args.get("code_file_name")

    if not student_id or not assignment_name or not code_file_name:
        return jsonify({"error": "student_id, assignment_name, and code_file_name are required"}), 400

    return jsonify(list_snapshots(student_id, assignment_name, code_file_name))

# 파일 내용을 조회하는 API
@app.route("/content", methods=["GET"])
def get_file_content():
    """파일 내용을 조회"""
    student_id = request.args.get("student_id")
    assignment_name = request.args.get("assignment_name")
    code_file_name = request.args.get("code_file_name")
    snapshot_name = request.args.get("snapshot_name")

    if not student_id or not assignment_name or not code_file_name or not snapshot_name:
        return jsonify({"error": "Missing required parameters"}), 400

    file_path = os.path.join(BASE_DIR, student_id, assignment_name, code_file_name, snapshot_name)
    # print(file_path)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    try:
        # 이진 모드로 파일 열기
        with open(file_path, "rb") as f:
            content = f.read()

        # 바이너리 데이터를 안전한 형식으로 변환
        try:
            decoded_content = content.decode("utf-8")  # UTF-8로 해석 시도
        except UnicodeDecodeError:
            decoded_content = content.hex()  # UTF-8이 아닐 경우, 16진수(hex) 문자열로 변환

        return {"content": decoded_content}
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/graphdata", methods=["GET"])
def get_snapshot_trends_api():
    """프런트에서 시간별 코드 크기 변화를 그래프로 표시할 데이터 반환"""
    student_id = request.args.get("student_id")
    assignment_name = request.args.get("assignment_name")

    if not student_id or not assignment_name:
        return jsonify({"error": "student_id and assignment_name are required"}), 400

    return jsonify({"snapshot_trends": get_snapshot_trends(student_id, assignment_name)})

@app.route("/snapshot_avg", methods=["GET"])
def get_snapshot_avg_api():
    """각 코드 파일의 스냅샷 개수 평균을 반환하는 API"""
    student_id = request.args.get("student_id")
    assignment_name = request.args.get("assignment_name")
    
    if not student_id or not assignment_name:
        return jsonify({"error": "student_id and assignment_name are required"}), 400
    
    return jsonify(get_snapshot_average(student_id, assignment_name))

# 서버 실행
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)