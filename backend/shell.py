from typing import List

from api import generate_numbers
from langutils import LangUtils, build_query, build_explanation_question
from redmine.context import init_context

print("=" * 10)

history: List[str] = []

context = init_context()
lang_utils = LangUtils(context)

if __name__ == "__main__":

    while True:
        user_input = input("Ask me >>> ")
        if user_input == "exit":
            break
        try:
            response_iterator = lang_utils.call_chat(build_query(user_input))
            response: str = "".join(response_iterator)
            if not response == LangUtils.unknown_context_response:
                lang_utils.process_response(response,True)
            else:
                print("Context explanation call...")
                response_iterator = lang_utils.call_chat(build_explanation_question(user_input))
                lang_utils.process_response("".join(response_iterator),True)
        except Exception as e:
            print("Error execute", e)




