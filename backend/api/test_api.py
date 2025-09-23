import requests
from loguru import logger


def test_api(question: str):
    """
    Make an HTTP API request and print the response.

    Parameters:
        headers (dict, optional): HTTP headers to include in the request.
        payload (dict, optional): Data to send with the request for POST/PUT.

    Returns:
        None
    """
    import json

    # Create a JSON string from the question and shell_history
    question_obj = json.dumps({"query": question, "shell_history": ""})
    logger.debug(f"rq: {question_obj}")
    url = "http://localhost:8000/api/chat_rq_stream"
    response = requests.post(url, json=question_obj)

    print(f"Status Code: {response.status_code}")
    print("Response Headers:", response.headers)
    print("Response Body:", response.text)


# Example usage:
if __name__ == "__main__":
    import pathlib

    current_file_dir = pathlib.Path(__file__).parent.resolve()
    with open(current_file_dir / "questions.txt", "r") as f:
        for line in f:
            question = line.strip()
            if question:
                test_api(question)
