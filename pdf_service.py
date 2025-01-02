# pdf_service.py
import streamlit as st
import boto3
import fitz

def init_textract_client():
    """Initialize AWS Textract client"""
    return boto3.client(
        'textract',
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
        region_name=st.secrets["AWS_DEFAULT_REGION"]
    )

def convert_pdf_to_images(pdf_file):
    """Convert PDF file to list of images"""
    pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    images = []
    
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        pix = page.get_pixmap()
        img_bytes = pix.tobytes("png")
        images.append(img_bytes)
    
    return images

def extract_text_with_textract(pdf_file):
    """Extract text from PDF using Amazon Textract"""
    try:
        textract_client = init_textract_client()
        # Convert PDF to images first
        images = convert_pdf_to_images(pdf_file)
        
        # Create a progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Process each page with Textract
        full_text = ""
        total_pages = len(images)
        
        for page_num, img_bytes in enumerate(images, 1):
            # Update progress bar and status
            progress = page_num / total_pages
            progress_bar.progress(progress)
            status_text.text(f'Processing page {page_num} of {total_pages}')
            
            # Send to Textract
            response = textract_client.detect_document_text(
                Document={'Bytes': img_bytes}
            )
            
            # Extract text from response
            page_text = ""
            for block in response['Blocks']:
                if block['BlockType'] == 'LINE':
                    page_text += block['Text'] + "\n"
            
            full_text += f"\n--- Page {page_num} ---\n{page_text}"
        
        # Clear the status text and show completion
        status_text.text('Processing complete!')
        progress_bar.progress(1.0)
                
        return full_text
        
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return None
