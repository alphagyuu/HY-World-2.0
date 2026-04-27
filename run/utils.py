import os
import cv2
import numpy as np
import json
from PIL import Image

def resize_image(input_path, output_path, target_width=None, target_height=None):
    """
    이미지를 특정 해상도나 비율에 맞춰 리사이즈합니다.
    16:9 또는 4:3 비율을 유지하며 리사이즈하는 기능을 포함합니다.
    """
    img = Image.open(input_path).convert('RGB')
    w, h = img.size
    
    # 해상도 판별 및 타겟 설정 (사용자 요청: 16:9, 4:3 지원)
    aspect_ratio = w / h
    
    if target_width and target_height:
        # 강제 지정된 경우
        pass
    elif abs(aspect_ratio - 16/9) < 0.1:
        # 16:9 근사치
        target_width = 832
        target_height = 480
    elif abs(aspect_ratio - 4/3) < 0.1:
        # 4:3 근사치
        target_width = 640
        target_height = 480
    else:
        # 기타: 긴 쪽을 832로 맞춤
        if w > h:
            target_width = 832
            target_height = int(832 / aspect_ratio)
        else:
            target_height = 832
            target_width = int(832 * aspect_ratio)

    img_resized = img.resize((target_width, target_height), Image.LANCZOS)
    img_resized.save(output_path, quality=95)
    return target_width, target_height

def generate_standard_trajectory(width, height, num_frames=8, motion_type='forward_pan'):
    """
    WorldNav 대신 수학적으로 계산된 카메라 궤적(camera.json 형식)을 생성합니다.
    motion_type: 'forward_pan', 'orbit', 'zoom'
    """
    # 기본 인트린직 (초점거리 f = width)
    focal = max(width, height)
    intrinsic = [
        [focal, 0, width / 2],
        [0, focal, height / 2],
        [0, 0, 1]
    ]
    
    motion_list = []
    
    for i in range(num_frames):
        # t: 0.0 ~ 1.0
        t = i / (num_frames - 1)
        
        # 기본 위치 (Identity)
        R = np.eye(3)
        T = np.zeros(3)
        
        if motion_type == 'forward_pan':
            # 서서히 전진하면서 약간의 좌우 회전
            T[2] = t * 0.5  # 전진 (Z축)
            T[0] = np.sin(t * np.pi) * 0.1 # 미세한 좌우 흔들림
            
            # Rotation (Y축 회전 - Yaw)
            yaw = np.sin(t * np.pi) * 0.05
            c, s = np.cos(yaw), np.sin(yaw)
            R = np.array([
                [c, 0, s],
                [0, 1, 0],
                [-s, 0, c]
            ])

        # 4x4 Extrinsic (World-to-Camera)
        extrinsic = np.eye(4)
        extrinsic[:3, :3] = R
        extrinsic[:3, 3] = T
        
        motion_list.append(extrinsic.tolist())

    camera_data = {
        "intrinsic": intrinsic,
        "extrinsic": motion_list[0], # 첫 프레임 기준
        "motion_list": motion_list
    }
    
    return camera_data

def save_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

def prepare_input_folder(world_name, input_image_path, outputs_root="outputs"):
    """
    WorldStereo 입력 형식에 맞게 폴더 구조를 생성합니다.
    """
    scene_dir = os.path.join(outputs_root, world_name)
    input_dir = os.path.join(scene_dir, "input")
    os.makedirs(input_dir, exist_ok=True)
    
    # 이미지 리사이즈 및 저장
    target_path = os.path.join(input_dir, "image.png")
    w, h = resize_image(input_image_path, target_path)
    
    # 기본 프롬프트 생성 (나중에 VLM 연동 가능)
    prompt_data = {
        "short caption": "A high-quality 3D scene.",
        "medium caption": "A cinematic view of the environment.",
        "long caption": "A detailed 3D reconstruction of the provided image, showing depth and spatial consistency."
    }
    save_json(prompt_data, os.path.join(input_dir, "prompt.json"))
    
    # 카메라 궤적 생성
    camera_data = generate_standard_trajectory(w, h)
    save_json(camera_data, os.path.join(input_dir, "camera.json"))
    
    return input_dir, scene_dir
