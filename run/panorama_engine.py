import os
import subprocess
import sys
import shutil
import json
from .utils import resize_image, save_json

class PanoramaEngine:
    def __init__(self, workspace_root):
        self.workspace_root = workspace_root
        self.hw1_path = os.path.join(workspace_root, "HunyuanWorld-1.0")
        self.worldstereo_path = os.path.join(workspace_root, "WorldStereo")
        
    def run(self, world_name, input_image):
        print(f"[*] Starting Panorama(1.0) Mode for '{world_name}'...")
        
        scene_dir = os.path.join("outputs", world_name)
        stage1_dir = os.path.join(scene_dir, "stage1_pano")
        os.makedirs(stage1_dir, exist_ok=True)
        
        # 1. HunyuanWorld 1.0 - Panorama Generation
        print(f"[*] Generating 360 panorama using HunyuanWorld 1.0...")
        try:
            # demo_panogen.py의 실제 인자 반영
            cmd_pano = [
                sys.executable, "demo_panogen.py",
                "--image_path", os.path.abspath(input_image),
                "--output_path", os.path.abspath(stage1_dir),
                "--prompt", "a high quality 360 degree panorama",
                "--seed", "42"
            ]
            subprocess.run(cmd_pano, cwd=self.hw1_path, check=True)
        except Exception as e:
            print(f"[!] Panorama generation failed: {e}")
            return False

        # 2. 결과물 확인
        pano_img_path = os.path.join(stage1_dir, "panorama.png")
        if not os.path.exists(pano_img_path):
            print(f"[!] Generated panorama not found at {pano_img_path}")
            return False

        # 3. WorldStereo 2.0 입력을 위해 panorama_input 폴더 준비
        pano_input_dir = os.path.join(scene_dir, "panorama_input")
        os.makedirs(pano_input_dir, exist_ok=True)
        
        # panorama.png 복사
        shutil.copy(pano_img_path, os.path.join(pano_input_dir, "panorama.png"))
        
        # start_frame.png (초기 시점용, 원본 이미지 리사이즈해서 사용)
        resize_image(input_image, os.path.join(pano_input_dir, "start_frame.png"), 832, 480)
        
        # meta_info.json
        save_json({"scene_type": "panorama"}, os.path.join(pano_input_dir, "meta_info.json"))
        
        # 4. WorldStereo 2.0 - Multi-trajectory 실행 (Panorama 모드)
        print(f"[*] Running WorldStereo 2.0 (Panorama Mode)...")
        stage3_output = os.path.join(scene_dir, "stage3_expansion")
        try:
            cmd_ws = [
                sys.executable, "run_multi_traj.py",
                "--model_type", "worldstereo-memory",
                "--task_type", "panorama",
                "--input_path", os.path.abspath(pano_input_dir),
                "--output_path", os.path.abspath(stage3_output)
            ]
            subprocess.run(cmd_ws, cwd=self.worldstereo_path, check=True)
        except Exception as e:
            print(f"[!] WorldStereo 2.0 (Panorama) failed: {e}")
            return False

        # 5. WorldMirror 2.0 - 3D Reconstruction
        # WorldStereo 출력물 위치 (run_multi_traj.py는 panorama_input 폴더명 하위에 저장함)
        wm_data_root = os.path.join(stage3_output, "panorama_input", "world_mirror_data", "worldstereo-memory")
        print(f"[*] WorldMirror data generated at: {wm_data_root}")

        print(f"[*] Running WorldMirror 2.0 for Final 3DGS reconstruction...")
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
            print(f"[!] WorldMirror 2.0 (Panorama) failed: {e}")
            return False

        print(f"[+] Panorama 3D World generation completed: {recon_output}")
        return True
