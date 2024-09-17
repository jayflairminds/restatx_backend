
# defines the prompts under predefined prompt buttons
def predefined_prompts(summary="default"):
    if summary == "bullet_points":
        user_question = """
        Summarize the document in a clear, structured list of bullet points. Include the main topics, key points, and important findings from each section. 
        Ensure that all major sections are covered comprehensively, avoiding unnecessary or irrelevant details. 
        Provide meaningful and concise bullet points, without any empty or vague responses.
        """
    elif summary == "detailed":
        user_question = """
        Provide a detailed summary of the document, including all major points, supporting evidence, and relevant context. 
        Ensure that the summary is well-organized, clear, and comprehensive. 
        Highlight key findings and conclusions, and use transition words to maintain a logical flow.
        """
    else:  
        user_question = """
        Summarize the document's content. Include the main topics, key points, and any important details or findings. 
        Make sure to cover all major sections. 
        Don't give empty responses.
        """

    return user_question
