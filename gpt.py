import os
import base64
import os
from typing import Optional
from openai import OpenAI
from typing import List

import dotenv
dotenv.load_dotenv()

import dotenv
dotenv.load_dotenv()

class GPTService:
    def __init__(self, model_name: str, api_key: Optional[str] = None):
        """
        Initialize the GPTService with a model name and API key.
        """
        self.model_name = model_name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided or set in the environment variable 'OPENAI_KEY'.")
        self.client = OpenAI(api_key=self.api_key)

    def text_to_text(self, prompt: str, system_prompt: str, num_retries: int = 3) -> str:
        """
        Perform a text-to-text API call.
        """
        retry = 0
        while True:
            if retry == num_retries:
                print(f"Max retries reached: {num_retries}.")
                return "Max retries reached."

            try:
                response = self.client.responses.create(
                    model=self.model_name,
                    input=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ]
                )

                if not response.error:
                    return response.output_text.strip()

                else:
                    print(f"Retrying {retry} due to non-200 status code...")
                    retry += 1



            except Exception as e:
                print(f"Error during API call: {e}")
                print(f"Retrying {retry} due to non-200 status code...")
                raise


    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def image_to_text(self, prompt: str, image_paths: List[str], system_prompt: str, num_retries=3) -> str:
        """
        Perform an image-to-text API call using base64-encoded images.
        """

        retry = 0
        while True:
            if retry == num_retries:
                print(f"Max retries reached: {num_retries}.")
                return "Max retries reached."

            try:
                base64_images = [self.encode_image(image_path) for image_path in image_paths]
                input_images = [
                    {"type": "input_image", "image_url": f"data:image/jpeg;base64,{b64}"}
                    for b64 in base64_images
                ]

                response = self.client.responses.create(
                    model=self.model_name,
                    input=[
                        {"role": "system", "content": system_prompt},
                        {
                            "role": "user",
                            "content": [{"type": "input_text", "text": prompt}] + input_images
                        }
                    ]
                )

                if not response.error:
                    return response.output_text.strip()

                else:
                    print(f"Retrying {retry} due to non-200 status code...")
                    retry += 1

            except Exception as e:
                print(f"Error during API call: {e}")
                print(f"Retrying {retry} due to non-200 status code...")
                raise


    def upload_batch_file(self, file_path: str):
        """
        Create a batch file for processing.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist.")

        try:
            with open(file_path, "rb") as file:
                batch_file = self.client.files.create(
                    file=file,
                    purpose="batch"
                )
                return batch_file

        except Exception as e:
            print(f"Error uploading batch file: {e}")
            raise

    def create_batch_file(self, batch_file_id: str):
        """
        Create a batch file for processing.
        """
        if not batch_file_id:
            raise ValueError("Batch file ID must be provided.")

        try:
            self.client.batches.create(
                input_file_id=batch_file_id,
                endpoint="/v1/chat/completions",
                completion_window="24h",
                metadata={
                    "description": "nightly eval job"
                }
            )
        except Exception as e:
            print(f"Error creating batch file: {e}")
            raise




    def check_batch_status(self, batch_file_id: str):
        """
        Check the status of a batch file.
        """
        if not batch_file_id:
            raise ValueError("Batch file ID must be provided.")

        try:
            response = self.client.batches.retrieve(batch_file_id)
            return response
        except Exception as e:
            print(f"Error checking batch file status: {e}")
            raise

    def retrieval_batch_result(self, output_file_id: str):
        """
        Retrieve the result of a batch file.
        """
        if not output_file_id:
            raise ValueError("Retrieved batch ID must be provided.")

        try:
            response = self.client.files.content(output_file_id)
            return response.text
        except Exception as e:
            print(f"Error retrieving batch file result: {e}")
            raise

    def cancel_batch_result(self, batch_file_id: str):
        """
        Cancel a batch file.
        """
        if not batch_file_id:
            raise ValueError("Batch file ID must be provided.")

        try:
            self.client.batches.cancel(batch_file_id)
        except Exception as e:
            print(f"Error canceling batch file: {e}")
            raise

    def get_all_batch_id(self):
        """
        Retrieve all batch files.
        """
        try:
            response = self.client.batches.list(limit=10)
            return response
        except Exception as e:
            print(f"Error retrieving batch files: {e}")
            raise
    
    
if __name__ == "__main__":
    # Example usage
    system_prompt = ""
    gpt_service = GPTService(model_name="o3-mini")
    text_response = gpt_service.text_to_text("What is AI?", "You are an AI assistant.")
    print("Text Response:", text_response)



# Example usage:
# gpt_service = GPTService(model_name="gpt-4o")
# text_response = gpt_service.text_to_text("What is AI?", "You are an AI assistant.")
# image_response = gpt_service.image_to_text(["path/to/image.png", "path/to/another_image.png"], "Describe the images.", "You are an AI assistant.")