from doc_summary_qna.doc_processing import *
from doc_summary_qna.prompts import *
def document_detail_list_json(serializer):
    organized_data = dict()
    for item in serializer.data:        
        if item['document_type'] not in organized_data.keys():
            organized_data[item['document_type']] = [item]
        else:
            organized_data[item['document_type']].append(item)
    
    return organized_data

def generate_summary_and_store(pdf_file, document_instance):
    # Process the PDF and generate the summary
    text = get_pdf_text_doc_manager(pdf_file) 
    chunks = get_text_chunks(text)
    get_vector_store(chunks)
    user_question = predefined_prompts()
    response = user_input(user_question)

    # Prepare the summary data to be stored in JSON format
    summary_data = {"summary": response}  # Wrap the response if needed
    # Save the instance with the updated summary
    return summary_data  