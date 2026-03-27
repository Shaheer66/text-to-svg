Phase 1: High-Contrast Base Generation
1. Technical Stack
Orchestration: Python 3.10+ (Module-based architecture)

Generative Engine: huggingface_hub (InferenceClient)

Model: Stable Diffusion XL (SDXL) 1.0 (via Serverless Router)

Vision QA (The Gatekeeper): Groq Cloud (LPU Inference)

Vision Model: llama-3.2-90b-vision-preview

Environment: python-dotenv for API security

2. Implementation Logic (Function Breakdown)
A. VectorGenerator.generate_base_image
Input: Raw user prompt (e.g., "geometric cat").

Logic: * Appends Master Style Constraints (Hex-specific #FFFFFF, topological flatness, bold black outlines).

Appends Negative Constraints (Anti-shrapnel, no floating lines, no textures).

Sets guidance_scale to 9.0 to force strict adherence to the vector-ready rules.

Output: A high-contrast PNG optimized for edge detection.

B. ImageValidator.validate_clean_plate
Input: Generated PNG path.

Logic:

Encodes image to Base64.

Passes image to Llama 3.2 90B with a Strict QA Prompt.

Evaluates against 4 pillars: Background Purity, Edge Integrity, Topological Flatness, and Noise Floor.

Output: Binary (PASS/FAIL).

C. main.run_pipeline
Logic: Executes a Retry-Loop (Max 3 attempts).

If Validator returns FAIL, the loop restarts the Generator.

If PASS, the file is locked for Phase 2.

3. Agentic Flow: Bridging the Gap (Next Iteration)
Currently, the Generator is "blind" to why it failed. To bridge this gap, we will implement an Agentic Feedback Loop:

Diagnostic Reasoning: Instead of a binary FAIL, the Validator will generate a Failure Vector (e.g., "Noise in Top-Left Corner" or "Lines too thin").

Prompt Mutation: An intermediary "Refiner Agent" (LLM) will take that failure reasoning and rewrite the next prompt dynamically.

Example: If "Noise detected," the Refiner adds "REALLY emphasize pure white empty space" to the next attempt.

Hyper-Parameter Tuning: If "Fuzzy Edges" are detected, the agent automatically increases the guidance_scale for the next seed.

4. Enhancements for Next Iteration
Local Caching: Store failed images and their prompts to prevent repeating mistakes.

Dynamic Seed Management: Iterating through specific seeds if a prompt is 90% successful.

Pre-Processing Script: Use OpenCV to "auto-crop" or "auto-clean" minor noise before sending it to the Validator to save API costs.