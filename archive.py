# OLD Function to analyze text using OpenAI
def analyze_text(text, perspective):
    response = client.completions.create(
        model="gpt-4o",
        prompt=f"{prompts[perspective]}\n\n{text}",
        max_tokens=500
    )
    return response.choices[0].text.strip()
