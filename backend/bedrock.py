import boto3
import json


def create_embeddings(text: str):
    """Creates embeddings for a given text using the Amazon Titan Embeddings G1 - Text model."""

    bedrock_runtime = boto3.client(service_name="bedrock-runtime", region_name="eu-central-1")

    body = json.dumps({
        "inputText": text
    })

    response = bedrock_runtime.invoke_model(
        body=body,
        modelId="amazon.titan-embed-text-v1",
        accept="application/json",
        contentType="application/json"
    )

    response_body = json.loads(response.get("body").read())

    return response_body.get("embedding")


def invoke_model(prompt: str):
    """Invokes the Anthropic Claude 3 Sonnet model to generate a response for a given prompt."""

    bedrock_runtime = boto3.client(service_name="bedrock-runtime", region_name="eu-central-1")

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    })

    response = bedrock_runtime.invoke_model(
        body=body,
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        accept="application/json",
        contentType="application/json"
    )

    response_body = json.loads(response.get("body").read())

    return response_body.get("content")[0].get("text")
