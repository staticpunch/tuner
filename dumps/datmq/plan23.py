PLAN2 = """
Based on the chat history, your task is to create the next user turn in Vietnamese.  Please follow these steps to generate the new user turn in Vietnamese:

Step 1: Carefully review the 'Chat History.' Identify key topics and information shared in the conversation. Consider the user's persona and the current context. Brainstorm different ways to continue the conversation, focusing on generating new and relevant questions or tasks that align with the conversation flow. Ensure the language is in Vietnamese, includes relevant Vietnamese context, and is easily understandable for a Vietnamese audience. **If the provided user turn is a translation of the example user turn, consider generating a new user turn that is entirely different from the example turn while still remaining relevant to the context of the conversation. If the user turn is a question, consider generating a new question with a different focus or a new request for information. Additionally, consider adding some context-specific details or nuances that are relevant to Vietnamese culture or daily life.**

Step 2: Create a detailed plan using the 'Methods List' from Step 1 to develop the 'New User Turn.' The plan should incorporate multiple methods from the list, ensuring the new user turn is different from the example turn and provides sufficient information for the AI assistant to complete the task effectively. **If the provided user turn is a translation of the example user turn, ensure that the new user turn is a task or question for the AI assistant to complete, written in Vietnamese. If the user turn is a question, ensure the new question is different from the example question and is relevant to the conversation. Additionally, consider adding a specific request or a follow-up question to make the user turn more engaging and complex.**

Step 3: Execute the plan step by step and provide the 'New User Turn'. 

Step 4: Thoroughly review the 'New User Turn' to identify any unreasonable parts. Ensure that the new user turn is a task or question for the AI assistant to complete, written in Vietnamese. Provide only the final user turn, without any explanation.
""".strip()

PLAN3 = """
Your task is to create a new conversation in Vietnamese between a user and an AI assistant. The conversation should mirror the format of the provided English example. The goal is to simulate a real-life interaction where the seeks support or information related to real life problems. The conversation must include both the USER and ASSISTANT roles, and be entirely in Vietnamese. Please follow these steps carefully:

Step 1: Begin by thoroughly examining the structure of the ##Example Conversation## provided in English. Pay close attention to the flow of the dialogue, the number of conversational turns, and the distribution of dialogue between the USER and ASSISTANT. Make sure you note the exact number of turns in the example, as your new conversation should match this structure closely.

Step 2: Dive deeper into the example conversation to grasp its tone, context, and structure. Consider the kinds of questions the USER asks and the type of responses provided by the ASSISTANT. The tone should be professional yet friendly, with the AI assistant demonstrating helpfulness, politeness to user.

For the ##New Conversation##, think about how a Vietnamese user might interact with an AI assistant. Adapt the themes, vocabulary, and cultural nuances to fit a Vietnamese audience. 
- USER Turns: Aim for 20-30 words per turn, written in a natural, conversational Vietnamese tone that reflects how a typical Vietnamese user would communicate.
- ASSISTANT Turns: The assistant's replies should be more detailed, with 100-200 words per response. It should provide clear and concise information while maintaining the professionalism.
- In the ##New Conversation##, there must be interleaving between a USER turn and an ASSISTANT turn. There are no two consecutive USER turns or ASSISTANT turns.

Step 3: Using the insights gathered in Step 2, create a detailed outline for the ##New Conversation##. This outline should identify a new topic—distinct from the one in the original example—but should maintain the same number of turns and overall structure.

Step 4: Proceed to write the ##New Conversation##. Follow the established structure of the example while incorporating the relevant tools and responses available to the AI assistant. Ensure that the USER’s questions are clear and specific, and that the ASSISTANT’s responses are both informative and supportive. Make sure that:
- The conversation maintains the same number of turns as the original.
- The interaction feels natural and seamless, as though it could occur in a real customer support scenario.

Step 5: Once the conversation is written, review it thoroughly to ensure that all components align logically. Check that the flow of the conversation is smooth, that the responses make sense in context, and that the turns follow a natural rhythm. Pay special attention to cultural references and the tone of the Vietnamese dialogue to ensure authenticity. The conversation must be interleavning between a USER turn and an ASSISTANT turn.

Note: It’s essential that the structure of the conversation remains consistent with the original example. While the content should focus on a different topic, the number of turns and the balance between USER and ASSISTANT dialogue should stay the same.
""".strip()
