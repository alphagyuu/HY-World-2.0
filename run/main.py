import argparse
import os
import sys
from .perspective_engine import PerspectiveEngine
from .panorama_engine import PanoramaEngine

class WorldGenerator:
    """
    GUI/API 연동을 위한 최상위 클래스.
    """
    def __init__(self):
        # 현재 스크립트 위치 기준의 프로젝트 루트
        self.workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.perspective_engine = PerspectiveEngine(self.workspace_root)
        self.panorama_engine = PanoramaEngine(self.workspace_root)

    def generate(self, input_image, world_name, mode="perspective"):
        if not os.path.exists(input_image):
            return {"status": "error", "message": f"Input image not found: {input_image}"}

        if mode == "perspective":
            success = self.perspective_engine.run(world_name, input_image)
        elif mode == "panorama":
            success = self.panorama_engine.run(world_name, input_image)
        else:
            return {"status": "error", "message": f"Unknown mode: {mode}"}

        if success:
            output_path = os.path.join("outputs", world_name)
            return {"status": "success", "output_path": output_path}
        else:
            return {"status": "error", "message": "Generation failed. Check logs."}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HY-World 2.0 Integrated World Generator")
    parser.add_argument("--input", required=True, help="Path to input image (input.png/jpg)")
    parser.add_argument("--name", required=True, help="World name for output folder")
    parser.add_argument("--mode", choices=["perspective", "panorama"], default="perspective", 
                        help="Generation mode: perspective(2.0) or panorama(1.0)")
    
    args = parser.parse_args()
    
    generator = WorldGenerator()
    result = generator.generate(args.input, args.name, args.mode)
    
    if result["status"] == "success":
        print(f"\n[🎉] Success! Your 3D World is ready at: {result['output_path']}")
    else:
        print(f"\n[❌] Failed: {result['message']}")
        sys.exit(1)
