# analysis_service.py
from openai import OpenAI
import streamlit as st

def analyze_text_with_openai(text):
    """Process text with OpenAI API focusing on foreclosure details"""
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        
        # Split text into chunks
        chunks, total_chunks = chunk_text(text)
        all_analyses = []
        
        # Create a progress bar for chunk processing
        if total_chunks > 1:
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        # Define the system prompt as a raw string
        system_prompt = r"""You are a real estate and legal document analysis expert.
Analyze this section of a foreclosure document and extract key information.
Focus on identifying:
1. Property Address and Details
2. List of Claims and Judgements (including amounts)
3. Plaintiff/Lender Information
4. Defendant/Property Owner Information
5. Important Dates
6. Any Red Flags or Special Conditions
7. Liens or Additional Encumbrances

Only include information that is explicitly mentioned in this section.
If you find partial information that seems to connect with other sections,
note it as "Partial Information".

Format the response with clear headings and bullet points."""
        
        for i, chunk in enumerate(chunks, 1):
            if total_chunks > 1:
                status_text.text(f'Analyzing section {i} of {total_chunks}')
                progress_bar.progress(i/total_chunks)
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system", 
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": "Analyze this section of the document:\n\n" + chunk
                    }
                ],
                temperature=0.3
            )
            all_analyses.append(response.choices[0].message.content)
        
        # Clear progress indicators if they were created
        if total_chunks > 1:
            progress_bar.empty()
            status_text.empty()
        
        # Define the summary system prompt as a raw string
        summary_system_prompt = r"""You are a real estate and legal document analysis expert.
Combine and summarize the following analyses of different sections of a foreclosure document.
Remove duplicates, resolve any conflicts, and present a clear, unified analysis.
Organize the information under these headings:

# Property Information
# Claims and Judgements
# Parties Involved
# Important Dates
# Liens and Encumbrances
# Risk Factors and Red Flags
# Additional Notes

Use bullet points for clarity and highlight any particularly important information."""
        
        # Combine and summarize all analyses
        final_summary = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": summary_system_prompt
                },
                {
                    "role": "user",
                    "content": "Combine and summarize these analyses:\n\n" + "\n---\n".join(all_analyses)
                }
            ],
            temperature=0.3
        )
        
        return final_summary.choices[0].message.content
        
    except Exception as e:
        st.error(f"OpenAI Error: {str(e)}")
        return None

def chunk_text(text, max_tokens=6000):
    """Split text into chunks of approximately max_tokens"""
    # Rough approximation: 1 token ~= 4 characters
    chars_per_chunk = max_tokens * 4
    chunks = []
    current_chunk = []
    current_length = 0
    
    # Split by pages (assuming "--- Page" is the separator)
    pages = text.split("--- Page")
    
    for page in pages:
        if not page.strip():
            continue
            
        # Add page marker back if it's not the first chunk
        page_text = f"--- Page{page}" if page.startswith(" ") else page
        page_length = len(page_text)
        
        if current_length + page_length > chars_per_chunk and current_chunk:
            # Join the current chunk and add it to chunks
            chunks.append("\n".join(current_chunk))
            current_chunk = []
            current_length = 0
        
        current_chunk.append(page_text)
        current_length += page_length
    
    # Add the last chunk if it exists
    if current_chunk:
        chunks.append("\n".join(current_chunk))
    
    return chunks, len(chunks)  # Return both chunks and chunk count
