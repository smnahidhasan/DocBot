from datetime import datetime


def get_chat_prompt(user_input, history=[], context=None):
    prompt = (
        "You are a helpful medical preliminary assesment bot. You do not have specific name. If user asks about basic chit-chat, reply them. DO NOT provide information which is not present on the Retrieved Context. If there is no information about the question on the context just say 'I do not know about it'. Provide precise response.\n"
    )

    # Add retrieved context if available
    if context:
        prompt += "\nRetrieved Context:\n" + context + "\n"
    # Append chat history
    for role, message in history:
        prompt += f"{role}: {message}\n"

    # Append current user input
    prompt += f"user: {user_input}\nassistant:\n\n"

    return prompt


def get_standalone_query_generation_prompt(user_input, history):
    # Initialize the prompt with system instruction
    prompt = (
        "<|im_start|>system<start_of_turn>You are a helpful medical assistant. Think step-by-step to rewrite the user's last message as a detailed standalone query for context retrieval. Only provide the standalone query without explanations or answers. These are the previous conversations:\n"
    )

    # Append chat history
    for role, message in history:
        prompt += f"{role.lower()}: {message}\n"

    prompt+="<end_of_turn><|im_end|>\n"

    # Append current user input and instruction for standalone query
    prompt += (
        f"<|im_start|>user<start_of_turn>{user_input}\n\nPlease rewrite the above query as a detailed standalone query for context retrieval. Do not provide explanations or answers, only the standalone query.<end_of_turn><|im_end|>\n"
        "<|im_start|>assistant<start_of_turn>"
    )

    return prompt