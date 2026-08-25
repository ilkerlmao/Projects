import ollama

# 1. Choose the model you want to talk to
model_name = "qwen2.5:0.5b"

# 2. Ask the user for input in the terminal
user_prompt = input("Ask your local AI a question: ")

# 3. Send the message to Ollama
response = ollama.chat(
    model=model_name,
    messages=[{"role": "user", "content": user_prompt}]
)

# 4. Print the AI's reply
print("\nAI Response:")
print(response["message"]["content"])