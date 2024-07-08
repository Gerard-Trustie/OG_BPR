import os
from dotenv import load_dotenv
import PyPDF2
import openai
from openai import OpenAI
from openai import AzureOpenAI
os.environ["AZURE_OPENAI_ENDPOINT"] = 'https://og-auto-openai.openai.azure.com/'
os.environ["AZURE_OPENAI_API_KEY"] = '2b622cd6fa304be68670fb661a83c896'

# Load environment variables from .env file
# load_dotenv()

# Set your OpenAI API key from the environment variable
# openai.api_key = os.getenv('OPENAI_API_KEY')
# client = OpenAI(
#     # This is the default and can be omitted
#     api_key=os.environ.get("OPENAI_API_KEY"),
# )


client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version="2024-02-01"
)

# Define expert prompts
prompts = {
    "Marketing": "As a marketing expert, analyze the following text. Identify positive and negative developments and the reasons given for these. If no reasons are given, raise a question. If there is no content related to marketing, or the page is simply a header or title page, please state that there is no content to analyze.",
    "Operational": "As an operational expert, analyze the following text. Identify positive and negative developments and the reasons given for these. If no reasons are given, raise a question.",
    "Technical": "As a technical expert, analyze the following text. Identify positive and negative developments and the reasons given for these. If no reasons are given, raise a question.",
    "Financial": "As a financial expert, analyze the following text. Identify positive and negative developments and the reasons given for these. If no reasons are given, raise a question."
}

# Function to analyze text using OpenAI
def analyze_text(text, perspective):
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": f"You are a {perspective} expert."},
            {"role": "user", "content": f"{prompts[perspective]}\n\n{text}"}
        ],
        model="gpt-4-turbo",
        max_tokens=500
    )
    return response.choices[0].message.content.strip()

# Function to read PDF and analyze each page
def analyze_pdf(pdf_path):
    results = {perspective: [] for perspective in prompts.keys()}
    
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        
        for page_num in range(num_pages):
            page_text = reader.pages[page_num].extract_text()
            page_title = page_text[0]
            print ("\n\n\n","Page",page_num+1,"of",num_pages,":",page_title)
            for perspective in prompts.keys():
                analysis = analyze_text(page_text, perspective)
                print ("\n\n",perspective," expert:",analysis)
                results[perspective].append({
                    "page": page_num + 1,
                    "analysis": analysis
                })
            
    return results

# Function to synthesize comments from all experts
def synthesize_comments(results):
    synthesis = []

    num_pages = len(results["Marketing"])
    for page_num in range(num_pages):
        page_synthesis = {
            "page": page_num + 1,
            "comments": []
        }
        
        for perspective in prompts.keys():
            page_synthesis["comments"].append({
                "perspective": perspective,
                "analysis": results[perspective][page_num]["analysis"]
            })
        
        synthesis.append(page_synthesis)
    
    return synthesis

# Function to summarize entire document
def summarize_document(synthesis):
    document_summary = {
        "positive_developments": [],
        "negative_developments": [],
        "questions_raised": []
    }
    
    for page in synthesis:
        for comment in page["comments"]:
            lines = comment["analysis"].split('\n')
            for line in lines:
                if "positive" in line.lower():
                    document_summary["positive_developments"].append(line)
                elif "negative" in line.lower():
                    document_summary["negative_developments"].append(line)
                elif "question" in line.lower():
                    document_summary["questions_raised"].append(line)
    
    return document_summary

# Main function to execute the analysis
def main(pdf_path):
    results = analyze_pdf(pdf_path)
    synthesis = synthesize_comments(results)
    document_summary = summarize_document(synthesis)

    # Print synthesis
    for page in synthesis:
        print(f"Page {page['page']}:")
        for comment in page["comments"]:
            print(f"{comment['perspective']} analysis:\n{comment['analysis']}\n")

    # Print document summary
    print("Document Summary:")
    print("Positive Developments:")
    for item in document_summary["positive_developments"]:
        print(item)

    print("\nNegative Developments:")
    for item in document_summary["negative_developments"]:
        print(item)

    print("\nQuestions Raised:")
    for item in document_summary["questions_raised"]:
        print(item)

# Path to your PDF document
pdf_path = "./OpCo_MPR.pdf"
main(pdf_path)
