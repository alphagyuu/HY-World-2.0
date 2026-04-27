# 🌍 HY-World 2.0 Integrated Runner

이 디렉토리는 단일 이미지(`input.png/jpg`)로부터 고화질 3D 월드를 자동으로 생성하기 위한 통합 실행 엔진을 포함하고 있습니다. **Perspective (2.0)** 모드와 **Panorama (1.0)** 모드를 모두 지원하며, 복잡한 설정 없이 한 번의 실행으로 3DGS 결과물을 얻을 수 있습니다.

---

## 🚀 1. 스크립트 실행 방법 (CLI)

터미널에서 `HY-World-2.0` 루트 디렉토리로 이동한 뒤, 아래 명령어를 통해 실행합니다.

### 🟢 Perspective (2.0) 모드 [권장]
최신 HY-World 2.0 엔진을 사용하여 사진 속 공간을 가장 정교하게 입체화합니다.
```bash
python -m run.main --input [이미지_경로] --name [월드_이름] --mode perspective
```
*예시: `python -m run.main --input my_room.jpg --name Room1 --mode perspective`*

### 🔵 Panorama (1.0) 모드
HunyuanWorld 1.0을 사용하여 이미지를 360도 파노라마로 확장한 뒤 전방위 월드를 생성합니다.
```bash
python -m run.main --input [이미지_경로] --name [월드_이름] --mode panorama
```

### ⚙️ 옵션 상세
*   `--input`: 입력 이미지 경로 (png, jpg, jpeg 지원).
*   `--name`: 결과물이 저장될 폴더 이름.
*   `--mode`: 실행 모드 (`perspective` 또는 `panorama`).

---

## 📓 2. 코랩/주피터 실행 방법 (Notebook)

구글 코랩(Google Colab)이나 로컬 주피터 환경에서 시각적으로 실행하고 싶을 때 사용합니다.

1.  `run/run.ipynb` 파일을 엽니다.
2.  **Step 1 (Setup)**: 필요한 모든 3D 라이브러리와 의존성을 자동으로 설치합니다.
3.  **Step 2 (Run)**: 우측 패널에서 이미지 경로와 월드 이름을 입력하고 실행 버튼을 누릅니다.

---

## 📂 3. 결과물 구조 (Output)

실행이 완료되면 `outputs/[월드_이름]/` 디렉토리에 다음과 같이 결과가 저장됩니다.

```text
outputs/[월드_이름]/
├── input/                # 전처리(리사이즈)된 이미지 및 자동 생성된 경로
├── stage3_expansion/     # WorldStereo가 생성한 멀티뷰 비디오 데이터
└── stage4_recon/         # [최종 결과] WorldMirror 2.0이 복원한 3DGS 및 Point Cloud (.ply)
```

---

## 🛠️ 핵심 기능 설명
*   **Auto Resize**: 16:9 및 4:3 해상도를 자동으로 감지하여 AI 모델에 최적화된 크기로 변경합니다.
*   **Auto Trajectory**: `WorldNav`가 없어도 수학적으로 계산된 최적의 카메라 경로(`camera.json`)를 생성하여 3D 복원 품질을 보장합니다.
*   **API Ready**: `run/main.py` 내의 `WorldGenerator` 클래스를 임포트하여 GUI 프로그램이나 웹 서버에 즉시 통합할 수 있습니다.

---

## ⚠️ 주의사항
*   최초 실행 시 HuggingFace에서 수 GB의 모델 가중치를 자동으로 다운로드하므로 넉넉한 디스크 공간과 인터넷 연결이 필요합니다.
*   3D 복원 특성상 **NVIDIA GPU(VRAM 16GB 이상 권장)** 환경에서 가장 원활하게 작동합니다.
