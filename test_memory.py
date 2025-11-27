from agent.memory import Memory
import os

def test_persistence():
    test_file = "test_memory.json"
    if os.path.exists(test_file):
        os.remove(test_file)

    # 1. Create memory and add message
    mem1 = Memory(storage_file=test_file)
    mem1.add_message("user", "Hello Persistence")
    
    # 2. Create new memory instance pointing to same file
    mem2 = Memory(storage_file=test_file)
    history = mem2.get_history()
    
    # 3. Verify
    assert len(history) == 1
    assert history[0]["parts"][0] == "Hello Persistence"
    print("Persistence test passed!")
    
    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)

if __name__ == "__main__":
    test_persistence()
