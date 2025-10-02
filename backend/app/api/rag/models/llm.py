import requests
import os
from typing import Any, Dict, List, Optional
from langchain_core.language_models.llms import BaseLLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.outputs import Generation, LLMResult
from pydantic import Field, BaseModel as PydanticBaseModel
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("API_URL", "").rstrip("/")
counter = 0


class LLM(BaseLLM, PydanticBaseModel):
    """
    Custom LLM class for interfacing with a local API endpoint.
    Now supports multimodal input (text + images).

    Attributes:
        api_url (str): The URL of the local API endpoint for text generation
        multimodal_api_url (str): The URL for multimodal (text + image) generation
        api_key (Optional[str]): API key for authentication (if required)
    """

    api_url: str = Field(default=f"{BASE_URL}/api/v1/generate")
    multimodal_api_url: str = Field(default=f"{BASE_URL}/generate/vision")
    api_key: Optional[str] = Field(default=None)

    def __init__(
            self,
            api_url: str = f"{BASE_URL}/generate/text",
            multimodal_api_url: str = f"{BASE_URL}/generate/vision",
            api_key: Optional[str] = None,
            **kwargs,
    ):
        """
        Initialize the LocalAPILLM.

        Args:
            api_url (str): URL of the API endpoint for text-only generation
            multimodal_api_url (str): URL of the API endpoint for vision (multimodal) generation
            api_key (Optional[str]): API key for authentication
        """
        super().__init__(
            api_url=api_url,
            multimodal_api_url=multimodal_api_url,
            api_key=api_key,
            **kwargs
        )

    def _call(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> str:
        """
        Call the local API with the given prompt.

        Args:
            prompt (str): The input prompt
            stop (Optional[List[str]]): Optional list of stop sequences
            run_manager (Optional[CallbackManagerForLLMRun]): Callback manager

        Returns:
            str: Generated text from the API
        """
        global counter

        # Prepare headers
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        # Prepare payload
        payload = {"text": prompt}

        try:
            # Make API request
            response = requests.post(self.api_url, json=payload, headers=headers)

            # Raise an exception for bad responses
            response.raise_for_status()

            # Extract prediction
            result = response.json().get("response", "")

            return result

        except requests.RequestException as e:
            raise ValueError(f"API request failed: {e}")

    def _call_with_image(
            self,
            prompt: str,
            image_base64: str,
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> str:
        """
        Call the local API with both text prompt and image.

        Args:
            prompt (str): The input prompt
            image_base64 (str): Base64 encoded image
            stop (Optional[List[str]]): Optional list of stop sequences
            run_manager (Optional[CallbackManagerForLLMRun]): Callback manager

        Returns:
            str: Generated text from the API
        """
        # Prepare headers
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        # Prepare payload with both text and image
        # Match the Vision LLM server's expected format
        payload = {
            "text": prompt,
            "image_base64": image_base64
        }

        # Debug logging
        print(f"[LLM] Sending vision request to: {self.multimodal_api_url}")
        print(f"[LLM] Payload keys: {list(payload.keys())}")
        print(f"[LLM] Text length: {len(payload['text'])}")
        print(f"[LLM] Image base64 length: {len(payload['image_base64'])}")
        print(f"[LLM] Image base64 preview: {payload['image_base64'][:100]}...")

        try:
            # Make API request to multimodal endpoint
            response = requests.post(
                self.multimodal_api_url,
                json=payload,
                headers=headers,
                timeout=60  # Longer timeout for image processing
            )

            print(f"[LLM] Response status: {response.status_code}")

            # Raise an exception for bad responses
            response.raise_for_status()

            # Extract prediction
            result = response.json().get("response", "")
            print(f"[LLM] Response received: {result[:100]}...")

            return result

        except requests.RequestException as e:
            print(f"[LLM] Multimodal API request failed: {e}")
            # Fallback: if multimodal endpoint fails, try text-only
            print(f"[LLM] Falling back to text-only.")
            return self._call(prompt, stop, run_manager, **kwargs)

    def _generate(
            self,
            prompts: List[str],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> LLMResult:
        """
        Generate responses for multiple prompts.

        Args:
            prompts (List[str]): List of input prompts
            stop (Optional[List[str]]): Optional list of stop sequences
            run_manager (Optional[CallbackManagerForLLMRun]): Callback manager

        Returns:
            LLMResult: Generated responses
        """
        generations = []
        for prompt in prompts:
            text = self._call(prompt, stop, run_manager, **kwargs)
            generations.append([Generation(text=text)])

        return LLMResult(generations=generations)

    @property
    def _llm_type(self) -> str:
        """
        Return the type of LLM.

        Returns:
            str: Type identifier for the LLM
        """
        return "local_api_llm"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """
        Return identifying parameters for the LLM.

        Returns:
            Dict[str, Any]: Dictionary of identifying parameters
        """
        return {
            "api_url": self.api_url,
            "multimodal_api_url": self.multimodal_api_url
        }

    def generate_response(self, prompt: str, image_base64: Optional[str] = None) -> str:
        """
        Generate a response from the LLM.
        Now supports optional image input for multimodal processing.

        Args:
            prompt (str): The text prompt
            image_base64 (Optional[str]): Base64 encoded image (optional)

        Returns:
            str: The generated response
        """
        try:
            if image_base64:
                # Use multimodal endpoint when image is provided
                generated_text = self._call_with_image(prompt, image_base64)
            else:
                # Use text-only endpoint
                llm_response = self.generate([prompt])
                text = llm_response.flatten()

                if not text or not text[0].generations:
                    return "I'm sorry, I couldn't generate a response. Please try again."

                generated_text = text[0].generations[0][0].text

            # Clean up response
            response = generated_text.replace('"', "")
            return response

        except Exception as e:
            print(f"Error generating response: {e}")
            return f"I encountered an error while processing your request. Please try again."

