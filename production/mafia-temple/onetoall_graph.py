"""Private ComfyUI API graph for the approved running research pilot.

Reference and driver are generated research assets, never the original photo.
The driver itself is imperfect; output is a diagnostic, not a final film.
"""

WIDTH, HEIGHT, FRAMES, FPS = 480, 832, 49, 16

def node(kind, **inputs):
    return {"class_type": kind, "inputs": inputs}

def make_graph():
    return {
        "1": node("PrivatePilotInput", width=WIDTH, height=HEIGHT, frames=FRAMES),
        "2": node("OnnxDetectionModelLoader", vitpose_model="vitpose-l-wholebody.onnx", yolo_model="yolov10m.onnx", onnx_device="CUDAExecutionProvider"),
        "3": node("PoseDetectionOneToAllAnimation", model=["2",0], images=["1",0], ref_image=["1",1], width=WIDTH, height=HEIGHT, align_to="pose", draw_face_points="weak", draw_head="weak"),
        "4": node("PrivatePoseAudit", images=["3",0], reference=["3",2]),
        "5": node("WanVideoVAELoader", model_name="Wan2_1_VAE_bf16.safetensors", precision="fp16", use_cpu_cache=False),
        "6": node("WanVideoEmptyEmbeds", width=WIDTH, height=HEIGHT, num_frames=FRAMES),
        "7": node("WanVideoAddOneToAllReferenceEmbeds", embeds=["6",0], vae=["5",0], ref_image=["3",2], ref_mask=["3",3], strength=1.0, start_percent=0.0, end_percent=1.0),
        "8": node("WanVideoAddOneToAllPoseEmbeds", embeds=["7",0], pose_images=["4",0], pose_prefix_image=["3",1], strength=1.0, start_percent=0.0, end_percent=1.0, pose_cfg_scale=1.0),
        "9": node("LoadWanVideoT5TextEncoder", model_name="umt5-xxl-enc-bf16.safetensors", precision="fp16", load_device="offload_device", quantization="disabled"),
        "10": node("WanVideoTextEncode", t5=["9",0], positive_prompt="A man in a black suit running sideways through a misty temple courtyard at night, realistic natural human motion, cinematic lighting.", negative_prompt="cartoon, extra limbs, deformed hands, blurry, distorted face, floating feet, static pose, flicker", force_offload=True, use_disk_cache=False, device="gpu"),
        "11": node("WanVideoModelLoader", model="Wan21-OneToAllAnimation_1_3B_v2_fp16.safetensors", base_precision="fp16", quantization="disabled", load_device="offload_device", attention_mode="sdpa"),
        "12": node("WanVideoSampler", model=["11",0], image_embeds=["8",0], text_embeds=["10",0], steps=8, cfg=2.0, shift=5.0, seed=13147, force_offload=True, scheduler="dpm++_sde", riflex_freq_index=0, batched_cfg=False, rope_function="comfy"),
        "13": node("WanVideoDecode", vae=["5",0], samples=["12",0], enable_vae_tiling=False, tile_x=272, tile_y=272, tile_stride_x=144, tile_stride_y=128),
        "14": node("PrivatePilotOutput", images=["13",0], fps=FPS, expected_frames=FRAMES),
    }
