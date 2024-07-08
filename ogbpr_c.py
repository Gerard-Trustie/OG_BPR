import os
from dotenv import load_dotenv
import PyPDF2
import openai
import anthropic
from typing import List, Tuple


# Load environment variables from .env file
load_dotenv()

# Replace with your actual API keys
OPENAI_API_KEY = "your_openai_api_key"
ANTHROPIC_API_KEY = "your_anthropic_api_key"

def extract_pdf_text(pdf_path: str) -> List[str]:
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        return [page.extract_text() for page in reader.pages]

def split_into_sections(pages: List[str]) -> Tuple[List[str], List[str], List[str]]:
    # This is a simplified split. You may need to adjust based on your PDF structure
    total_pages = len(pages)
    marketing = pages[:total_pages//3]
    technology = pages[total_pages//3:2*total_pages//3]
    financial = pages[2*total_pages//3:]
    return marketing, technology, financial

def analyze_marketing(pages: List[str]) -> str:
    openai.api_key = OPENAI_API_KEY
    prompt = ("You are an Expert in Marketing for Mobile Network Operators. "
              "Comment on each page in the pdf and highlight positive developments, "
              "negative developments, and any strategic comments.\n\n")
    prompt += "\n".join(pages)
    
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=1000
    )
    return response.choices[0].text.strip()

def analyze_technology(pages: List[str]) -> str:
    client = anthropic.Client(api_key=ANTHROPIC_API_KEY)
    prompt = ("You are an Expert in Technology and Operations for Mobile Network Operators. "
              "Comment on each page in the pdf and highlight positive developments, "
              "negative developments, and any strategic comments.\n\n")
    prompt += "\n".join(pages)
    
    response = client.completion(
        prompt=prompt,
        model="claude-2",
        max_tokens_to_sample=1000
    )
    return response.completion

def analyze_financial(pages: List[str]) -> str:
    # For this example, we'll use OpenAI for financial analysis as well
    openai.api_key = OPENAI_API_KEY
    prompt = ("You are an Expert in Finance for Mobile Network Operators. "
              "Comment on each page in the pdf and highlight positive developments, "
              "negative developments, and any strategic comments.\n\n")
    prompt += "\n".join(pages)
    
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=1000
    )
    return response.choices[0].text.strip()

def main(pdf_path: str):
    pages = extract_pdf_text(pdf_path)
    marketing, technology, financial = split_into_sections(pages)
    
    marketing_analysis = analyze_marketing(marketing)
    technology_analysis = analyze_technology(technology)
    financial_analysis = analyze_financial(financial)
    
    print("Marketing Analysis:")
    print(marketing_analysis)
    print("\nTechnology Analysis:")
    print(technology_analysis)
    print("\nFinancial Analysis:")
    print(financial_analysis)

if __name__ == "__main__":
    main("path_to_your_pdf_file.pdf")
