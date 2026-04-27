# HY-World 2.0 World Generation Pipeline Plan (Multi-Mode)

이 문서는 HY-World 2.0의 단일 이미지 기반 3D 월드 생성 파이프라인 계획안입니다. 사용자의 요청에 따라 **Perspective (2.0)**와 **Panorama (1.0)** 두 가지 모드를 지원합니다.

---

## 1. 개요 (Overview)
본 프로젝트는 단일 입력 이미지(`input.png/jpg`)로부터 3D 월드(3DGS/Mesh)를 생성하는 것을 목표로 합니다. 
*   **Perspective Mode (2.0):** 최신 HY-World 2.0 및 WorldStereo 2.0 기술을 사용하여 사진 속 공간을 고화질로 입체화합니다.
*   **Panorama Mode (1.0):** HunyuanWorld 1.0 기술을 사용하여 단일 이미지를 360° 파노라마로 확장한 뒤 전방위 3D 월드를 생성합니다.

---

## 2. 모드별 상세 파이프라인 (Pipeline Details)

### 🟢 Mode A: Perspective (2.0) - [주력 모드]
*   **특징:** 네이티브 2.0 엔진을 사용하여 가장 정교하고 깨끗한 3D 복원 수행.
*   **단계:**
    1.  **Image Pre-processing:** 입력 이미지를 16:9 또는 4:3 비율로 리사이즈 (AI 모델 최적화).
    2.  **Auto Trajectory Generation:** `WorldNav` 대신 수학적 알고리즘을 사용하여 최적의 5~8개 카메라 경로(`camera.json`) 자동 생성.
    3.  **World Expansion (WorldStereo 2.0):** 단일 이미지에서 멀티뷰 비디오 생성.
    4.  **World Composition (WorldMirror 2.0):** 생성된 비디오에서 3DGS 및 Point Cloud 추출.

### 🔵 Mode B: Panorama (1.0) - [전방위 확장 모드]
*   **특징:** HunyuanWorld 1.0 코드를 활용하여 360도 전체 공간을 생성.
*   **단계:**
    1.  **Panorama Generation:** `HunyuanWorld-1.0/demo_panogen.py`를 사용하여 일반 이미지를 360° 파노라마로 변환.
    2.  **Multi-trajectory Expansion:** 파노라마의 각 방향으로 시점을 확장하여 전체 공간 데이터 확보.
    3.  **Unified 3D Recon:** 파노라마 데이터를 기반으로 전체 구형(Spherical) 3D 월드 구축.

---

## 3. 구현 계획 및 과제 (Implementation Tasks)

### 📁 디렉토리 구조
*   `run/`: 모든 실행 스크립트가 위치하는 핵심 폴더.
    *   `main.py`: 모드 선택 및 전체 흐름 제어 (API/GUI 연동용).
    *   `perspective_engine.py`: 2.0 기반 핵심 로직.
    *   `panorama_engine.py`: 1.0 기반 핵심 로직.
    *   `utils.py`: 이미지 처리 및 카메라 궤적 수학 공식 라이브러리.

### 🛠️ 핵심 구현 과제
1.  **이미지 자동 리사이즈:** 16:9/4:3 해상도를 감지하고 모델이 요구하는 해상도(예: 832px 등)로 보간법을 사용하여 리사이즈.
2.  **수학적 카메라 궤적 설계:** 전진, 좌우 훑기, 궤도 회전 등 3D 복원에 가장 유리한 카메라 행렬(W2C) 자동 계산 로직 작성.
3.  **HunyuanWorld 1.0 브릿지:** 1.0 폴더의 코드를 호출하고 결과물을 2.0 파이프라인으로 연결하는 래퍼 작성.
4.  **API 지향 설계:** GUI에서 이미지 경로와 모드 값만 넘겨주면 비동기적으로 실행될 수 있도록 클래스 구조화.

---

## 4. 실행 방식 (Expected Usage)
```bash
# Perspective 2.0 모드로 실행 (기본)
python -m run.main --input input.png --name MyRoom --mode perspective

# Panorama 1.0 모드로 실행
python -m run.main --input input.png --name MyWorld --mode panorama
```

최종 결과물은 `outputs/[WORLD_NAME]/` 폴더에 3D 자산과 렌더링 영상이 저장됩니다.
