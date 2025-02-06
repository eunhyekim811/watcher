from flask import Flask, request, jsonify
import os
import re
from collections import defaultdict

app = Flask(__name__)

BASE_DIR = "/home/ubuntu/Couch"  # OpenStack 인스턴스 내부의 기본 경로

# 학번과 과제명에 해당하는 코드 파일명을 조회
def list_code_files(student_id, assignment_name):
    path = os.path.join(BASE_DIR, student_id, assignment_name)
    
    if not os.path.exists(path):
        return {"error": "Directory not found"}, 404

    code_files = [entry.name for entry in os.scandir(path) if entry.is_dir()]
    
    return {"path": path, "code_files": code_files}


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
                    size = os.path.getsize(snapshot.path)
                    snapshot_trends[code_file_name].append({"timestamp": timestamp, "size": size})

            # 각 코드파일별 스냅샷 데이터를 시간순으로 정렬
            snapshot_trends[code_file_name].sort(key=lambda x: x["timestamp"])


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

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return jsonify({"content": content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/graphdata", methods=["GET"])
def get_snapshot_trends_api():
    """프런트에서 시간별 코드 크기 변화를 그래프로 표시할 데이터 반환"""
    student_id = request.args.get("student_id")
    assignment_name = request.args.get("assignment_name")

    if not student_id or not assignment_name:
        return jsonify({"error": "student_id and assignment_name are required"}), 400

    return jsonify(get_snapshot_trends(student_id, assignment_name))


# 서버 실행
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
