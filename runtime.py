import json
import ollama  # pip install ollama

# 1. Load your local FORM specification
with open("form_v0_1.json", "r") as f:
    FORM_SPEC = json.load(f)

class LocalFormRuntime:
    def __init__(self, spec, model_name="llama3.2"):
        self.spec = spec
        self.model_name = model_name
        self.cycle_memory = []

    def _build_system_prompt(self):
        return f"""
You are executing under the FORM runtime framework.
Framework Spec: {json.dumps(self.spec)}

Current Cycle Memory (Preserved State):
{json.dumps(self.cycle_memory, indent=2)}

Enforce the Information Layers (Fact vs Interpretation vs Inference vs Hypothesis) and execute the 8-step Cycle Protocol.
End your response with a JSON block inside ```json ... ``` that contains ONLY the updated cycle memory to carry forward:
{{
  "cycle_about": "...",
  "discoveries": [...],
  "changed_assumptions": [...],
  "open_questions": [...]
}}
"""

    def run_turn(self, user_input):
        system_prompt = self._build_system_prompt()
        
        # Executes directly against your local Ollama instance
        response = ollama.chat(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        )
        
        output_text = response['message']['content']
        self._extract_and_update_memory(output_text)
        return output_text

    def _extract_and_update_memory(self, output_text):
        if "```json" in output_text:
            try:
                json_str = output_text.split("```json")[1].split("```")[0].strip()
                new_memory = json.loads(json_str)
                self.cycle_memory.append(new_memory)
            except Exception as e:
                print(f"[Runtime Warning] Memory parse skipped: {e}")

if __name__ == "__main__":
    # Choose any local open-weights model installed via Ollama (e.g., llama3.2, deepseek-r1, mistral)
    runtime = LocalFormRuntime(FORM_SPEC, model_name="llama3.2")
    
    print("FORM Local Runtime Active (Zero Proprietary APIs). Type 'exit' to quit.\n")
    while True:
        user_msg = input("User > ")
        if user_msg.lower() == "exit":
            break
            
        result = runtime.run_turn(user_msg)
        print(f"\nFORM >\n{result}\n")