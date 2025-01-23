import pandas as pd
import PyPDF2
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os

# Define the base URL for the site
base_url = "https://detroitatwork.com"

# Define the URL of the webpage you want to scrape
url = "https://detroitatwork.com/training"

# Folder to store PDFs
pdf_folder = 'pdfs'

# Create the PDFs directory if it doesn't exist
if not os.path.exists(pdf_folder):
    os.makedirs(pdf_folder)

# Fetch the HTML content from the webpage
response = requests.get(url)
html = response.text  

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# Find the section header for "Information Technology & Professional Services"
target_section = soup.find('h2', string='Information Technology & Professional Services')

# If the section is not found, exit or display a message
if target_section is None:
    print("Could not find the 'Information Technology & Professional Services' section.")
else:
    # Find the next sibling <ul> (unordered list) which contains the links
    ul_element = target_section.find_next_sibling('ul')

    # Ensure we found the <ul> element
    if ul_element is None:
        print("Could not find the unordered list (<ul>) under 'Information Technology & Professional Services'.")
    else:
        # Extract all the links from the <ul> element and convert to absolute URLs
        links = [urljoin(base_url, a['href']) for a in ul_element.find_all('a', href=True)]

        # Filter out links that are media URLs (those starting with "/media/" or "/sites/detroitatwork/files/")
        pdf_links = [link for link in links if link.endswith('.pdf')]

        # If PDF links are found, print and process them
        if pdf_links:
            for link in pdf_links:
                print(link)

                # Download the PDF
                pdf_name = link.split('/')[-1]  # Get the file name from the link
                pdf_path = os.path.join(pdf_folder, pdf_name)

                # Send a GET request to download the PDF
                pdf_response = requests.get(link, stream=True)
                if pdf_response.status_code == 200:
                    with open(pdf_path, 'wb') as pdf_file:
                        for chunk in pdf_response.iter_content(chunk_size=1024):
                            if chunk:
                                pdf_file.write(chunk)

        # Now handle media links (those starting with "/media/")
        media_links = [link for link in links if link.startswith(base_url + "/media/")]

        # If media links are found, process them
        if media_links:
            for link in media_links:
                print(link)

                # Now follow these media links to extract the PDF
                # Send a GET request to the media page
                media_response = requests.get(link)

                # Check if the request was successful
                if media_response.status_code == 200:
                    media_soup = BeautifulSoup(media_response.content, 'html.parser')
                        
                    # Try to find a PDF link in the page
                    pdf_link = None
                    for a_tag in media_soup.find_all('a', href=True):
                        if a_tag['href'].endswith('.pdf'):
                            pdf_link = urljoin(base_url, a_tag['href'])  # Full PDF link
                            break
                        
                    # If a PDF link is found, download it
                    if pdf_link:
                        pdf_name = pdf_link.split('/')[-1]  # Get the file name from the link
                        pdf_path = os.path.join(pdf_folder, pdf_name)

                        # Download the PDF
                        pdf_response = requests.get(pdf_link, stream=True)
                        if pdf_response.status_code == 200:
                            with open(pdf_path, 'wb') as pdf_file:
                                for chunk in pdf_response.iter_content(chunk_size=1024):
                                    if chunk:
                                        pdf_file.write(chunk)

# Function to clean field names
def clean_field_name(field_name):
    """
    Remove 'Yes No' prefix or similar redundant text from field names.
    """
    cleaned_name = re.sub(r"^Yes No", "", field_name).strip()
    return cleaned_name

# Function to standardize phone number format
def standardize_phone_number(number):
    """
    Standardize phone number format to (XXX) XXX-XXXX.
    """
    # Remove all non-numeric characters
    number = re.sub(r'\D', '', number)
    # Ensure the number has exactly 10 digits
    if len(number) == 10:
        return f"({number[:3]}) {number[3:6]}-{number[6:]}"
    else:
        return number  # Return the number if it's not 10 digits long (e.g., invalid numbers)

# Function to extract fields from PDF
def extract_pdf_fields(pdf_path):
    """
    Extract form fields from a single PDF file.
    Clean field names and transpose data so that field names become columns.
    """
    field_data = {}

    with open(pdf_path, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        fields = {}
        fields = pdf_reader.get_fields()

        # Process fields if found
        if fields:
            for field_name, field_data_obj in fields.items():
                value = field_data_obj.get("/V", "")

                # Clean up field names
                cleaned_field_name = clean_field_name(field_name)

                # Handle checkboxes
                if isinstance(value, str) and value == "/Yes":
                    value = "Yes"
                elif isinstance(value, str) and value == "":
                    value = "No"
                else:
                    value = str(value)

                field_data[cleaned_field_name] = value
    return pd.DataFrame([field_data])

# Directory containing PDF files
pdf_folder = r"C:/Users/abhi/Desktop/Documents/ARPA/Job Training Scrape/pdfs" 

try:
    pdf_files = [os.path.join(pdf_folder, f) for f in os.listdir(pdf_folder) if f.lower().endswith(".pdf")]
except Exception as e:
    pdf_files = []

# Initialize a master DataFrame for all PDFs
all_data = pd.DataFrame()

# Process each PDF and append data
for pdf_file in pdf_files:
    pdf_data = extract_pdf_fields(pdf_file)
    if not pdf_data.empty:
        all_data = pd.concat([all_data, pdf_data], ignore_index=True)

# Merge 'Dropdown11' and 'Dropdown13' into a new column 'MergedColumn'
all_data['Training Delivery'] = all_data['Dropdown11'].fillna('') + ' ' + all_data['Dropdown13'].fillna('')

# Clean up extra spaces if any
all_data['Training Delivery'] = all_data['Training Delivery'].str.strip()

all_data.drop(columns=['Dropdown11', 'Dropdown13', 'RESET FORM'], inplace=True)

all_data['Check Box1'] = all_data['Check Box1'].fillna('') + ' ' + all_data['Check Box14'].fillna('')
all_data['Check Box3'] = all_data['Check Box3'].fillna('') + ' ' + all_data['Check Box16'].fillna('')
all_data['Check Box5'] = all_data['Check Box5'].fillna('') + ' ' + all_data['Check Box18'].fillna('')
all_data['Check Box7'] = all_data['Check Box7'].fillna('') + ' ' + all_data['Check Box20'].fillna('')
all_data['Check Box9'] = all_data['Check Box9'].fillna('') + ' ' + all_data['Check Box22'].fillna('')

all_data.drop(columns=['Check Box10','Check Box14','Check Box15','Check Box16', 'Check Box17','Check Box18', 'Check Box2','Check Box20','Check Box21','Check Box22', 'Check Box23','Check Box4', 'Check Box6','Check Box8','Check Box19'], inplace=True)

# Rename the column
all_data.rename(columns={'Check Box1': 'High School Diploma / GED', 'Check Box3': 'Drug Screen', 'Check Box5': 'Criminal Background Check', 'Check Box7': 'Valid Driver License', 'Check Box9': 'Is there am exam required at the end of the training?'}, inplace=True)

all_data = all_data.replace({'NA': 'N/A', 'Not Available': 'N/A'})

# Apply the function to the 'Phone Number' column
all_data['Phone Number'] = all_data['Phone Number'].apply(standardize_phone_number)

# Output combined data to Excel
all_data.to_excel('C:/Users/abhi/Desktop/Documents/ARPA/Job Training Scrape/Extracted_PDF_Content.xlsx', index=False)



