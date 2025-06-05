def get_repo_analysis_prompt(name: str, github_url: str) -> str:
    """
    Generate a prompt for analyzing a GitHub repository and generating a comprehensive summary.
    
    Args:
        name (str): The name of the repository or user
        github_url (str): The GitHub repository URL
        
    Returns:
        str: The formatted prompt
    """
    return (
        "You are an AI assistant with expertise in scraping codebases and understanding their purpose, "
        "usage, and offerings. Your task is to analyze the provided repository and generate:\n\n"
        "1. A brief one-sentence summary\n"
        "2. A comprehensive summary including:\n"
        "   - Service name\n"
        "   - Purpose\n"
        "   - Offered methods\n"
        "   - Available endpoints\n"
        "   - Examples of how to use the endpoints and methods\n\n"
        "respond in json format with the following keys: summary, description\n"
        f"Repository Information:\n"
        f"Name: {name}\n"
        f"URL: {github_url}\n\n"
    ) 