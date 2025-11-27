from dotenv import load_dotenv
from agent.core import Agent

def test_news_agent():
    load_dotenv()
    print("Initializing News Agent...")
    agent = Agent()
    
    # Clear memory for a fresh test
    agent.memory.clear()
    
    query = "What are the latest developments in AI Agents?"
    print(f"\nUser: {query}")
    
    response = agent.run(query)
    print(f"\nAgent: {response}")

if __name__ == "__main__":
    test_news_agent()
