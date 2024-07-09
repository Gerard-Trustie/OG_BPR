import os
from dotenv import load_dotenv
import PyPDF2
import openai
from openai import OpenAI
from openai import AzureOpenAI


load_dotenv()

client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version="2024-02-01"
)

# Define expert prompts
prompts = {
    "Marketing": 
    "Act as an expert in Marketing of Mobile Networks, analyze the following text."
    "Summarise the marketing content and identify the key points in 10 bullet points."
    "If there is content that is better suited to another expert, please state this."
    "Identify positive and negative developments and the reasons given for these."
    "If no reasons are given for the change, raise a question."
    ,
    "Technical and Operational": 
    "Act as a Technical and Operational expert in  Mobile Networks, analyze the following text."
    "Summarise the Technical and Operational content and identify the key points in 10 bullet points."
    "If there is content that is better suited to another expert, please state this."
    "Identify positive and negative developments and the reasons given for these."
    "If no reasons are given for the change, raise a question."
    ,
    "Financial": 
    "Act as a Financial expert in  Mobile Networks, analyze the following text."
    "Summarise the Financial content and identify the key points in 10 bullet points."
    "If there is content that is better suited to another expert, please state this."
    "Identify positive and negative developments and the reasons given for these."
    "If no reasons are given for the change, raise a question."
}

# Function to analyze text using OpenAI
def analyze_text(text, perspective):

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": f"{prompts[perspective]}"},
            {"role": "user", "content": f"\n\n{text}"}
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

def analyze_full_doc(pdf_path):
    results = {perspective: [] for perspective in prompts.keys()}
    all_pages_text = ""

    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)

        for page_num in range(num_pages):
            page_text = reader.pages[page_num].extract_text()
            all_pages_text += "\n" + page_text  # Append each page's text with a newline

    # Assuming page_title is the first line of the entire document
    page_title = all_pages_text.split('\n', 1)[0]
    print("\n\n\n", "Text in document:", page_title)

    for perspective in prompts.keys():
        analysis = analyze_text(all_pages_text, perspective)
        print("\n\n", perspective, " expert:", analysis)
        results[perspective].append({
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
def oldmain(pdf_path):
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

def main(pdf_path):

    results = analyze_full_doc(pdf_path)
    
    for perspective, analyses in results.items():
        print(f"\nPerspective: {perspective}")
        for analysis in analyses:
            print(f"Analysis: {analysis['analysis']}")
        

# Path to your PDF document
pdf_path = "./OpCo_MPR.pdf"
main(pdf_path)
