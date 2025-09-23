import requests


def test_api(question: str):
    """
    Make an HTTP API request and print the response.

    Parameters:
        headers (dict, optional): HTTP headers to include in the request.
        payload (dict, optional): Data to send with the request for POST/PUT.

    Returns:
        None
    """

    question_obj = f"""
        "query": {question}
        "shell_history": []
        """

    url = "http://localhost:/api/chat_rq_stream"
    response = requests.post(url, json=question_obj)

    print(f"Status Code: {response.status_code}")
    print("Response Headers:", response.headers)
    print("Response Body:", response.text)


# Example usage:
if __name__ == "__main__":
    with open("questions.txt", "r") as f:
        for line in f:
            question = line.strip()
            if question:
                test_api(question)
