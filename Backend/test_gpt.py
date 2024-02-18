from gpt import generate_trivia_questions
import json

if __name__ == "__main__":
    # Generate trivia questions
    questions = generate_trivia_questions("Dogs", 5, "spanish", "gpt4")
    print(questions)
