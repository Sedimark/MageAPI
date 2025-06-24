    
import re

def replace_pipeline_name(input_string: str, replacement: str) -> str:
    """
    Replace all occurrences of <pipeline_name> in the input string with the specified replacement.
    
    Args:
        input_string (str): The original string containing <pipeline_name>
        replacement (str): The value to replace <pipeline_name> with
        
    Returns:
        str: The modified string with all replacements made
        
    Example:
        >>> text = "This is <pipeline_name> and another <pipeline_name>"
        >>> replace_pipeline_name(text, "MyPipeline")
        'This is MyPipeline and another MyPipeline'
    """
    if input_string is None:
        return ""
        
    pattern = r'<pipeline_name>'
    return re.sub(pattern, replacement, input_string)