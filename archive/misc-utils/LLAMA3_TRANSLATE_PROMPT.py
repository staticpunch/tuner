TRANSLATE_TEMPLATE = """
**TASK**: I want you to act as a translator. Translate the instruction and its response provided below into Vietnamese, ensuring it sounds natural and fluent.

### Instruction:
{instruction}

### Response: 
{response}

**Format requirement:**
The output must be solely in the following format without any additional explanation:
```
<INSTRUCTION>
// Vietnamese translation the instruction.
</INSTRUCTION>

<RESPONSE>
// Vietnamese translation the response.
</RESPONSE>
```
""".strip()
