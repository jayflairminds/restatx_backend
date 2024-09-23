
# defines the prompts under predefined prompt buttons
def predefined_prompts(predefined_prompt):
    
    question_dict = { 
        "bullet_points":"""Summarize the document in a clear, structured list of bullet points. Include the main topics, key points, and important findings from each section. 
        Ensure that all major sections are covered comprehensively, avoiding unnecessary or irrelevant details. Provide meaningful and concise bullet points, without any empty or vague responses.""",
        
        "detailed": """Provide a detailed summary of the document, including all major points, supporting evidence, and relevant context. 
        Ensure that the summary is well-organized, clear, and comprehensive. Highlight key findings and conclusions, and use transition words to maintain a logical flow.""", 
        
        "tl;dr": """Summarize the document in 1-2 sentences, focusing only on the most essential information. Avoid unnecessary details and provide a clear, concise overview of key points.""" }
    
    return question_dict.get(predefined_prompt)
