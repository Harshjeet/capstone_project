from fhir.resources import get_fhir_model_class

def validate_fhir_resource(resource_type, data):
    """
    Validates data against FHIR R4 models using fhir.resources.
    Returns (validated_data_dict, error_message).
    """
    try:
        ResourceTypeClass = get_fhir_model_class(resource_type)
        # Use parse_obj or instantiation
        resource = ResourceTypeClass(**data)
        # Convert to JSON and back to dict to ensure all custom types (like date) 
        # are converted to JSON primitives (strings) which Mongo/Flask handle better 
        # and matches our existing logic (expecting date strings).
        import json
        return json.loads(resource.json()), None
    except Exception as e:
        with open("/tmp/validation_errors.log", "a") as f:
             f.write(f"Validation Error for {resource_type}: {str(e)}\nData: {data}\n\n")
        return None, str(e)

def sanitize_text(text):
    """
    Simple sanitization to remove potential HTML/Script tags.
    """
    if not isinstance(text, str):
        return text
    import re
    # Remove <script> tags and html tags
    text = re.sub(r'<[^>]*>', '', text)
    return text.strip()
