import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import os

# Load model only once (global variable to save memory)
print("🔄 Loading local LLM...")

device = "cpu"
print(f"Device set to use {device}")

model_name = "tiiuae/falcon-rw-1b"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float32)

def get_llm_response(prompt, max_tokens=50):
    """
    Generate a friendly meeting suggestion from LLM.
    """
    print("📤 Sending prompt to LLM...")

    # Tokenize input with truncation
    input_ids = tokenizer(prompt, return_tensors="pt", truncation=True).input_ids

    # Move to CPU (or CUDA if available)
    input_ids = input_ids.to(model.device)

    # Generate response
    output_ids = model.generate(
        input_ids,
        max_new_tokens=max_tokens,
        temperature=0.7,
        top_p=0.9,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id,
       
    )

    # Decode and strip prompt from generated text
    generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    message = generated_text.replace(prompt, "").strip()
    return message
