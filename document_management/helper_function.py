def document_detail_list_json(serializer):
    organized_data = dict()
    for item in serializer.data:        
        if item['document_type'] not in organized_data.keys():
            organized_data[item['document_type']] = [item]
        else:
            organized_data[item['document_type']].append(item)
    
    return organized_data

    