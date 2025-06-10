def prepare_code_content(code_content):
    # Remove any leading/trailing whitespace and normalize line endings
    code_content = code_content.strip()
    # Replace triple quotes with escaped double quotes if needed
    code_content = code_content.replace('"""', '\\"\\"\\"')
    return code_content