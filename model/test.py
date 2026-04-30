# # import torch
# # from diffusers import FluxPipeline

# # lora_path = "C:/Users/Shaheer.Ahmad/Downloads/Simple_Vector_Flux_v2_renderartist.safetensors"

# # prompt = "v3ct0r style, simple flat vector art, isolated on white bg, a robotic dog playing fetch"

# # print(" Loading FLUX Base Model (CPU optimized)...")

# # pipe = FluxPipeline.from_pretrained(
# #     "black-forest-labs/FLUX.1-schnell", 
# #     torch_dtype=torch.float32 
# # )

# # print(f" Applying LoRA weights from: {lora_path}")
# # pipe.load_lora_weights(".", weight_name=lora_path, adapter_name="vector")
# # pipe.fuse_lora(lora_scale=0.85)  
 
# # print(" Generating Image... Grab a coffee, this will take a while on CPU.")
# # with torch.no_grad():
# #     image = pipe(
# #         prompt,
# #         guidance_scale=0.0,           
# #         num_inference_steps=4,       
# #         max_sequence_length=512,      
# #     ).images[0]
 
# # output_file = "vector_output.png"
# # image.save(output_file)
# # print(f" Success! Image saved to {output_file}")





# # import torch
# # from diffusers import FluxPipeline
# # from safetensors.torch import load_file
# # from dotenv import load_dotenv
# # import os

# # load_dotenv()
# # HF_TOKEN = os.getenv("HF_TOKEN")
# # BASE_MODEL = "black-forest-labs/FLUX.1-schnell"
# # LOCAL_TENSOR_PATH = "C:/Users/Shaheer.Ahmad/Downloads/flux-2-klein-9b-kv-fp8.safetensors"


# # print("Loading FLUX Base Model from Hugging Face...")
# # pipe = FluxPipeline.from_pretrained(
# #     BASE_MODEL, 
# #     token=HF_TOKEN,
# #     torch_dtype=torch.bfloat16,
# #     low_cpu_mem_usage=True
# # )

# # print(f"Attaching local weights from: {LOCAL_TENSOR_PATH}")
 
# # state_dict = load_file(LOCAL_TENSOR_PATH)
# # pipe.load_lora_weights(state_dict)

# # print("Moving model to CPU...")
# # pipe.to("cpu")

 
# # pipe.enable_model_cpu_offload()

# # prompt =  ""
# # print("Starting CPU inference (this will take time)...")
# # with torch.no_grad():
# #     image = pipe(
# #         prompt,
# #         guidance_scale=0.0,
# #         num_inference_steps=4,
# #         max_sequence_length=256,
# #     ).images[0]

# # image.save("./local_test_output.png")
# # print("Done! Check local_test_output.png")


# def analyze_logs(logs: list[dict]) ->list:
#     avg_fail_response_time_per_endpoint = {}
#     for log in logs:
#         endpoint = log["endpoint"]
#         response_time = log["response_time"]
#         if log["status"] > 400:
#             if endpoint not in avg_fail_response_time_per_endpoint:
#                 avg_fail_response_time_per_endpoint[endpoint] = []
#                 avg_fail_response_time_per_endpoint[endpoint].append(response_time)
          
#             avg_fail_response_time_per_endpoint[endpoint].append(response_time)
#     for endpoint, time in avg_fail_response_time_per_endpoint.items():
#         avg_fail_response_time_per_endpoint[endpoint] = sum(time) / len(time)   
#     return avg_fail_response_time_per_endpoint             



# logs = [
#     {"endpoint": "/users", "status": 200, "response_time": 0.4},
#     {"endpoint": "/users", "status": 500, "response_time": 1.2},
#     {"endpoint": "/orders", "status": 200, "response_time": 0.8},
#     {"endpoint": "/orders", "status": 500, "response_time": 2.1},
#     {"endpoint": "/users", "status": 200, "response_time": 0.3},
# ]
# from collections import defaultdict
# def analyze_log2(logs:list[dict]):
#     failed = defaultdict(list)
#     for log in logs:
#         if log["status"] > 400:
#             failed[log["endpoint"]].append(log["response_time"])
#     return {endpoint:sum(times)/len(times) for endpoint, times in failed.items()}

# print(analyze_log2(logs))


# from fastapi import FastAPI, HTTPException
# app = FastAPI()

# @app.get("/users/{user_id}/include_orders")
# def get_user(user_id: int, include_orders: bool =False):
#     if user_id > 0:
#         user=get_user_from_db(user_id) 
#         # the db will handle using the select username, email from users where id = user_id
#         # else reurn None amd the API will handle the rror response
#         if user:
#             if include_orders:
#                 orders = get_orders_for_user(user_id)
#                 if orders:   
#                     return {user_id: user, "orders": orders} 
#             return {"user_id": user_id, "user": user}    
#         return {"error":"No user found", "status_code":404}
#     raise HTTPException(status_code=400, detail="isis")
    
#     # fetch from DB
#     return {"user_id": user_id}


# users = [
#     {"id": 1, "name": "Ali", "age": 25, "active": True},
#     {"id": 2, "name": "Sara", "age": 17, "active": True},
#     {"id": 3, "name": "Ahmed", "age": 30, "active": False},
#     {"id": 4, "name": "Zara", "age": 22, "active": True},
# ]
# # active_user = sorted([user["name"] for user in users if user["active"] and user["age"] >= 18])

# def my_decorator(func):
#     def wrapper():
#         print("Something before the function.")
#         func()
#         print("Something after the function.")
#     return wrapper

# @my_decorator
# def say_hello():
#     print("Hello!")

# say_hello()


# def process_data(n):
#     total = sum(range(n))
#     return total

# def timer(func):
#     import time
#     def wrapper(*args, **kwargs):
#         start_time = time.time()
#         result = func(*args, **kwargs)
#         end_time = time.time()
#         print(f"Execution time: {end_time - start_time:.4f} seconds")
# @timer
# def run_process():
#     return process_data(1000)
 

# import time

# def timer(func):
#     def wrapper(*args, **kwargs):
#         start = time.time()
#         result = func(*args, **kwargs)
#         end = time.time()
#         print(f"{func.__name__} took {end - start:.4f} seconds")
#         return result  #   must return
#     return wrapper  #   must return wrapper

# @timer
# def process_data(n):
#     total = sum(range(n))
#     return total

# print(process_data(1000000))


# import time

# def timer(func):
#     def wrapper(*args, **kwargs):
#         start = time.time()
#         result = func(*args, **kwargs)
#         end = time.time()
#         print(f"{func.__name__} took {end-start:.4f} seconds")
#         return result
#     return wrapper

# @timer
# def process_data(n):
#     total = sum(range(n))
#     return total



# import asyncio

# async def fetch_user(user_id: int):
#     await asyncio.sleep(1)  # simulates DB call
#     return {"id": user_id, "name": f"User_{user_id}"}
# async def main():
#     users=await asyncio.gather(*(fetch_user(i) for i in range(5)))
#     print(users)

# asyncio.run(main())    


# from contextlib import contextmanager

# @contextmanager
# def db_connection():
#     conn = create_db_connection()
#     try:
#         yield conn
#     finally:
#         conn.close()

# with db_connection() as conn:
#     print("DB conected")
# from fastapi import FastAPI
# import uvicorn
# from pydantic import BaseModel, EmailStr

# class user(BaseModel):
#     username:str
#     email: EmailStr
#     age: int | None

# app = FastAPI()

# @app.get("/")
# def home():
#     return {"message":"Hello"}

 


# if __name__ == "__main__":
#     uvicorn.run(app , host="127.0.0.1",port=5500)


# from collections import defaultdict



# def analyzer(logs):
#     failed = defaultdict(list)
#     for log in logs:
#         if log["status"] > 400:
#             failed[log["endpoint"]].append(log["response_time"])

#     return {endpoint:sum(times)/len(times) for endpoint, times in failed.items()}
# print(analyzer(logs)) 


# class Product:
#     def __init__(self, name:str, price: float, stock:int):
#         self.name = name
#         self.price = price
#         self.stock = stock
#     def apply_discount(self,percent:int):
#         old_price= self.price
#         self.price= (self.price*percent)/100
#         print(f"price updated from {old_price} to {self.price} after {percent}% dicount")
#     def is_available(self):
#         return True if self.stock > 0 else False
#     def __repr__(self):
#         return f"Product(name={self.name}, price={self.price}, stock={self.stock})"
  
# bat = Product(name="Bat", price=100.25, stock=11) 
# bat.__repr__()          

# target="""
# 🔹  Compress a given string (e.g., "aaabbc" → "a3b2c1")
# 🔹 Find the frequency of words in a sentence
# 🔹  Find duplicates in a list (output in list format)
# 🔹  Find the missing number from a list (1 to 4)
# 🔹 Find the sum of elements in a list
# 🔹 ⭐ Solve Two Sum problem
# """


# x = "aaabbc"
# # res = []
# # count = 1
# # for i in range(1, len(x)):
# #     if x[i]==x[i-1]:
# #         count+=1
# #     else:
# #         res.append(f"{x[i]}{count}")  
# # res.append(f"{x[-1]}{count}")
# # print("".join(res))   

# def compress_string(s):
 
#     res = []
#     count = 1
 
#     for i in range(1, len(s)):
#         if s[i] == s[i-1]:
#             count += 1
#         else: 
#             res.append(f"{s[i-1]}{count}")
#             count = 1
 
#     res.append(f"{s[-1]}{count}")
#     return "".join(res)       
# # print(compress_string(x))

# #find the frequency of a word in a sentence

# sentence = "The AI model is a powerful model for AI tasks."
# target_word = "AI"
# def get_freq(sentence, target_word):
#     words =sentence.lower().split()
#     freq = words.count(target_word.lower())
#     return freq


# def get_duplicate(sample: list)->list: 
#     res = []
#     #unique = set(sample)
#     for num in sample:
#         if num not in res:
#             temp=sample.count(num)
#         #print(temp)
#             if temp>1:
#                 res.append(num)
#     return res
# num=[1, 2, 3, 2,4 ,4, 5,5,6, 1, 6]
# # print(get_duplicate(num))

# def missing_element(num:list)->int:
#     #n(n+1)/2
#     n=len(num)+1
     
#     total = (n*(n+1))/2
     
#     missing = total-sum(num)
#     return missing
# num = [1,2,3]
# #print(missing_element(num))

# def sum_of_list(num: list)->int:
#     total=0
#     for i in range(len(num)):
#         total+=num[i]
#     return total    
# #print(sum_of_list(num))

# def two_sum(nums, target):
#     seen = {}  
#     for i, num in enumerate(nums):
#         complement = target - num
#         if complement in seen:
#             return [seen[complement], i]
#         seen[num] = i

# nums = [1,5,8,90]
# print(two_sum(nums,91))


# from fastapi import HTTPException, Depends, 

logs = [
    "2024-01-15 ERROR /api/users timeout",
    "2024-01-15 INFO /api/orders success",
    "2024-01-16 ERROR /api/payments timeout",
    "2024-01-16 INFO /api/users success",
    "2024-01-16 ERROR /api/users forbidden",
]

{
    "/api/users":    {"ERROR": 2, "INFO": 1},
    "/api/orders":   {"ERROR": 0, "INFO": 1},
    "/api/payments": {"ERROR": 1, "INFO": 0}
}

def analyze_logs(logs: list) -> dict:
    results = {}
    for log in logs:
        parts = log.split()
        level = parts[1]      # ERROR / INFO
        endpoint = parts[2]   # /api/users

        if endpoint not in results:
            results[endpoint] = {"ERROR": 0, "INFO": 0}
        
        results[endpoint][level] += 1
    
    return results

print(analyze_logs(logs))        