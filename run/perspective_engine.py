import os
import subprocess
import sys
import shutil
from .utils import prepare_input_folder

class PerspectiveEngine:
    def __init__(self, workspace_root):
        self.workspace_root = workspace_root
        self.worldstereo_path = os.path.join(workspace_root, "WorldStereo")
        
    def run(self, world_name, input_image):
        print(f"[*] Starting Perspective(2.0) Mode for '{world_name}'...")
        
        # 1. 전처리 및 폴더 준비
        input_dir, scene_dir = prepare_input_folder(world_name, input_image)
        output_dir = os.path.join(scene_dir, "stage3_expansion")
        os.makedirs(output_dir, exist_ok=True)
        
        # 2. WorldStereo 실행 (멀티뷰 생성)
        print(f"[*] Running WorldStereo for multi-view generation...")
        try:
            # WorldStereo 폴더로 이동하여 실행 (의존성 문제 방지)
            cmd_ws = [
                sys.executable, "run_camera_control.py",
                "--model_type", "worldstereo-camera",
                "--input_path", input_dir,
                "--output_path", output_dir
            ]
            subprocess.run(cmd_ws, cwd=self.worldstereo_path, check=True)
        except Exception as e:
            print(f"[!] WorldStereo failed: {e}")
            return False

        # 3. WorldMirror 데이터 위치 확인
        # WorldStereo는 결과를 output_path/input/world_mirror_data/... 에 저장하는 경향이 있음
        # 실제 경로를 탐색하여 확인 필요
        wm_data_root = os.path.join(output_dir, "input", "world_mirror_data", "worldstereo-camera")
        if not os.path.exists(wm_data_root):
            # 대안 경로 확인 (scene_name이 포함될 수 있음)
            wm_data_root = os.path.join(output_dir, world_name, "world_mirror_data", "worldstereo-camera")
            
        print(f"[*] WorldMirror data generated at: {wm_data_root}")

        # 4. WorldMirror 2.0 실행 (3D 재구성)
        print(f"[*] Running WorldMirror 2.0 for 3DGS reconstruction...")
        recon_output = os.path.join(scene_dir, "stage4_recon")
        try:
            cmd_wm = [
                sys.executable, "-m", "hyworld2.worldrecon.pipeline",
                "--input_path", os.path.join(wm_data_root, "images"),
                "--prior_cam_path", os.path.join(wm_data_root, "cameras.json"),
                "--strict_output_path", recon_output,
                "--target_size", "832",
                "--enable_bf16",
                "--no_interactive"
            ]
            subprocess.run(cmd_wm, cwd=self.workspace_root, check=True)
        except Exception as e:
            print(f"[!] WorldMirror 2.0 failed: {e}")
            return False

        print(f"[+] Perspective 3D World generation completed: {recon_output}")
        return True
