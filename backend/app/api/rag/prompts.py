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
    prompt = (
        "Think step-by-step. Write the standalone query of the last user message so that it contains all the information of this question and best suited for context retrieval. Just write the query in detailed form. DO NOT write any extra explanation. DO NOT write the answer.\n"
    )

    # Append chat history
    for role, message in history:
        prompt += f"{role}: {message}\n"

    # Append current user input
    prompt += f"user: {user_input}\n\nStandalone Query: (Standalone Query should be in detailed form. DO NOT Answer the query here.)\n\n"

    return prompt
