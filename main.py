import sys
from dotenv import load_dotenv
from agent.core import Agent

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # You could allow the user to pick a model via args
    model_name = "gemma3n:e4b" 
    if len(sys.argv) > 1:
        model_name = sys.argv[1]

    print(f"Using model: {model_name}")
    
    try:
        agent = Agent(model_name=model_name)
    except Exception as e:
        print(f"Failed to initialize agent: {e}")
        return

    print("Agent ready! Type 'exit' or 'quit' to stop.")
    print("-" * 50)

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
            
            if not user_input.strip():
                continue

            response = agent.run(user_input)
            print(f"Agent: {response}")
            print("-" * 50)

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
