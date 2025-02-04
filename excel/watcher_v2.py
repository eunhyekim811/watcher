import os
from openpyxl import Workbook
from datetime import datetime
from collections import defaultdict

# 최상위 디렉터리 경로 (학번 디렉터리들이 포함된 디렉터리)
root_directory = "/home/ubuntu/Couch"

def create_excel_for_assignment(assignment_name, student_snapshots):
    # 출력 디렉터리 생성
    output_dir = "/home/ubuntu/watcher/outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    output_excel = os.path.join(output_dir, f"{assignment_name}.xlsx")
    wb = Workbook()
    del wb["Sheet"]  # 기본 시트 제거

    # 각 학생별로 시트 생성
    for student_id, snapshots in student_snapshots.items():
        ws = wb.create_sheet(title=student_id)
        ws.append(["과제 코드 디렉터리 (.c)", "스냅샷 파일명", "파일 크기 (bytes)", "마지막 수정 시간", "타임스탬프"])

        # 스냅샷을 파일명 기준으로 정렬 (숫자 변환 없이)
        sorted_snapshots = sorted(snapshots, key=lambda x: x[1])
        for snapshot in sorted_snapshots:
            ws.append(snapshot)

    wb.save(output_excel)
    print(f"엑셀 파일이 생성되었습니다: {output_excel}")

# 과제별로 학생들의 스냅샷 정보를 저장할 딕셔너리
assignments_data = defaultdict(lambda: defaultdict(list))

# 학번 디렉터리 탐색
for student_dir in os.listdir(root_directory):
    student_path = os.path.join(root_directory, student_dir)
    if not os.path.isdir(student_path):
        continue

    # 과제 디렉터리 탐색
    for hw_dir in os.listdir(student_path):
        hw_path = os.path.join(student_path, hw_dir)
        if not os.path.isdir(hw_path):
            continue

        # .c 과제 코드 디렉터리 탐색
        for code_dir in os.listdir(hw_path):
            if not code_dir.endswith(".c"):
                continue
            code_path = os.path.join(hw_path, code_dir)
            if not os.path.isdir(code_path):
                continue

            # 타임스탬프 스냅샷 파일 탐색
            for snapshot_file in os.listdir(code_path):
                snapshot_path = os.path.join(code_path, snapshot_file)
                if not os.path.isfile(snapshot_path):
                    continue

                # 파일 정보 수집
                file_size = os.path.getsize(snapshot_path)
                file_mtime = datetime.fromtimestamp(os.path.getmtime(snapshot_path)).strftime('%Y-%m-%d %H:%M:%S')
                
                # 데이터 저장
                snapshot_info = [code_dir, snapshot_file, file_size, file_mtime, snapshot_file.split('.')[0]]
                assignments_data[hw_dir][student_dir].append(snapshot_info)

# 각 과제별로 엑셀 파일 생성
for assignment_name, student_snapshots in assignments_data.items():
    create_excel_for_assignment(assignment_name, student_snapshots)
