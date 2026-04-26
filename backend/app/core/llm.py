import boto3
from dotenv import load_dotenv
import os

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 500))
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.2))

if not AWS_REGION:
    raise ValueError("AWS_REGION is not set in environment variables.")

if not MODEL_ID:
    raise ValueError("BEDROCK_MODEL_ID is not set in environment variables.")

client = boto3.client("bedrock-runtime", region_name=AWS_REGION)

def generate_answer(question, context):

    prompt = f"""
You are an assistant for consulting documents.

Answer the question using ONLY the context below.

Context:
{context}

Question:
{question}

Answer:
"""

    response = client.converse(
        modelId=MODEL_ID,
        messages=[
            {
                "role": "user",
                "content": [{"text": prompt}]
            }
        ],
        inferenceConfig={
            "maxTokens": MAX_TOKENS,
            "temperature": TEMPERATURE
        }
    )

    return response["output"]["message"]["content"][0]["text"]

