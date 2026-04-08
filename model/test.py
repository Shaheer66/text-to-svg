# import torch
# from diffusers import FluxPipeline

# lora_path = "C:/Users/Shaheer.Ahmad/Downloads/Simple_Vector_Flux_v2_renderartist.safetensors"

# prompt = "v3ct0r style, simple flat vector art, isolated on white bg, a robotic dog playing fetch"

# print(" Loading FLUX Base Model (CPU optimized)...")

# pipe = FluxPipeline.from_pretrained(
#     "black-forest-labs/FLUX.1-schnell", 
#     torch_dtype=torch.float32 
# )

# print(f" Applying LoRA weights from: {lora_path}")
# pipe.load_lora_weights(".", weight_name=lora_path, adapter_name="vector")
# pipe.fuse_lora(lora_scale=0.85)  
 
# print(" Generating Image... Grab a coffee, this will take a while on CPU.")
# with torch.no_grad():
#     image = pipe(
#         prompt,
#         guidance_scale=0.0,           
#         num_inference_steps=4,       
#         max_sequence_length=512,      
#     ).images[0]
 
# output_file = "vector_output.png"
# image.save(output_file)
# print(f" Success! Image saved to {output_file}")





import torch
from diffusers import FluxPipeline
from safetensors.torch import load_file
from dotenv import load_dotenv
import os

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
BASE_MODEL = "black-forest-labs/FLUX.1-schnell"
LOCAL_TENSOR_PATH = "C:/Users/Shaheer.Ahmad/Downloads/flux-2-klein-9b-kv-fp8.safetensors"


print("Loading FLUX Base Model from Hugging Face...")
pipe = FluxPipeline.from_pretrained(
    BASE_MODEL, 
    token=HF_TOKEN,
    torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=True
)

print(f"Attaching local weights from: {LOCAL_TENSOR_PATH}")
 
state_dict = load_file(LOCAL_TENSOR_PATH)
pipe.load_lora_weights(state_dict)

print("Moving model to CPU...")
pipe.to("cpu")

 
pipe.enable_model_cpu_offload()

prompt =  ""
print("Starting CPU inference (this will take time)...")
with torch.no_grad():
    image = pipe(
        prompt,
        guidance_scale=0.0,
        num_inference_steps=4,
        max_sequence_length=256,
    ).images[0]

image.save("./local_test_output.png")
print("Done! Check local_test_output.png")