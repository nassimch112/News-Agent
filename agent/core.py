import ollama
import json
from agent.memory import Memory
from agent.tools import Tool, SearchTool, ScrapeTool

class Agent:
    def __init__(self, model_name: str = "gemma3n:e4b"):
        self.model_name = model_name
        self.memory = Memory(storage_file="agent_memory.json")
        self.tools = [SearchTool(), ScrapeTool()]
        self.tool_map = {t.name: t for t in self.tools}
        
    def _get_system_prompt(self) -> str:
        tool_desc = "\n".join([f"- {t.name}: {t.description}" for t in self.tools])
        return f"""You are a helpful AI assistant with access to the following tools:
{tool_desc}

To use a tool, you MUST respond with a JSON object in the following format:
{{
    "tool": "tool_name",
    "input": "tool_input"
}}

If you do not need to use a tool, just respond normally.
When you receive a tool result, use it to answer the user's question.
Always verify news by checking multiple sources if possible.

IMPORTANT: When using the 'search' tool, you can use natural language queries, but specific keywords often yield better results.
The search tool now returns content snippets. You may not always need to scrape if the snippet answers the question.
"""

    def run(self, user_input: str) -> str:
        """
        Processes user input and returns the agent's response using Ollama with ReAct.
        """
        self.memory.add_message("user", user_input)

        # Max turns to prevent infinite loops
        max_turns = 5
        current_turn = 0

        while current_turn < max_turns:
            current_turn += 1
            
            # Prepare messages for Ollama
            ollama_messages = [{"role": "system", "content": self._get_system_prompt()}]
            
            for msg in self.memory.get_history():
                content = msg.get("parts", [""])[0] if isinstance(msg.get("parts"), list) else msg.get("content", "")
                role = "assistant" if msg["role"] == "model" else msg["role"]
                ollama_messages.append({"role": role, "content": content})

            try:
                response = ollama.chat(model=self.model_name, messages=ollama_messages)
                response_text = response['message']['content']
                
                # Check for tool call
                try:
                    # Attempt to parse JSON. 
                    # LLMs might wrap JSON in markdown blocks ```json ... ``` or add text around it.
                    # Simple heuristic: look for { and }
                    start = response_text.find('{')
                    end = response_text.rfind('}')
                    
                    if start != -1 and end != -1:
                        json_str = response_text[start:end+1]
                        tool_call = json.loads(json_str)
                        
                        tool_name = tool_call.get("tool")
                        tool_input = tool_call.get("input")
                        
                        if tool_name in self.tool_map:
                            print(f"DEBUG: Calling tool {tool_name} with input: {tool_input}")
                            tool_result = self.tool_map[tool_name].run(tool_input)
                            
                            # Add the tool call and result to memory so the model sees it
                            # We represent tool interactions as:
                            # Assistant: {tool call}
                            # User (System): Tool Result: ...
                            
                            # Note: We don't want to show the raw JSON to the user in the final output usually,
                            # but for the model's context, it's necessary.
                            # We'll add the assistant's "thought" (the JSON) to memory.
                            self.memory.add_message("model", response_text)
                            
                            # Then add the result as a "user" message (or system, but user is safer for simple chat models)
                            self.memory.add_message("user", f"Tool Result: {tool_result}")
                            
                            # Continue the loop to let the agent process the result
                            continue
                            
                except json.JSONDecodeError:
                    pass # Not a valid JSON tool call, treat as normal response

                # If no tool call or tool call failed/finished, return the response
                # But if we just executed a tool, we `continue`d above.
                # So if we are here, it means the model generated a final answer (or a malformed one).
                
                self.memory.add_message("model", response_text)
                return response_text

            except Exception as e:
                return f"Error communicating with Ollama: {e}"
        
        return "Error: Maximum turn limit reached."
