from src.langchain.routing.router import classify_query


def debug_classification(message: str):
    res = classify_query(message)
    print("Query:", message, "Class:", res)


debug_classification("Tell me the current time.")
debug_classification("Tell me the main point of the following text:"
                     "The cars were invented in 1850 by Henry Ford in America to make transportation faster."
                     "Ford was pioneering transportation technology by making cars."
                     "We use cars today to travel and to transport heavy weights.")
debug_classification("Tell me the current position of John Doe at our company.")
