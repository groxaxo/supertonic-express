
import sys
import os
import onnxruntime as ort

def inspect_model(model_path):
    print(f"Inspecting {model_path}...")
    try:
        sess = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
        print("Inputs:")
        for i in sess.get_inputs():
            print(f"  - {i.name}: {i.type}, {i.shape}")
        print("Outputs:")
        for o in sess.get_outputs():
            print(f"  - {o.name}: {o.type}, {o.shape}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    assets_dir = os.path.abspath("assets/onnx")
    inspect_model(os.path.join(assets_dir, "text_encoder.onnx"))
    inspect_model(os.path.join(assets_dir, "latent_denoiser.onnx"))
    inspect_model(os.path.join(assets_dir, "voice_decoder.onnx"))
