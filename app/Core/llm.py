import boto3

client = boto3.client("bedrock-runtime", region_name="us-east-1")

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
        modelId="us.anthropic.claude-haiku-4-5-20251001-v1:0",
        messages=[
            {
                "role": "user",
                "content": [{"text": prompt}]
            }
        ],
        inferenceConfig={
            "maxTokens": 500,
            "temperature": 0
        }
    )

    return response["output"]["message"]["content"][0]["text"]

