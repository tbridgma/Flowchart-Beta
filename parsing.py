import requests
from bs4 import BeautifulSoup
import json
import re

# Define the URL
#url = "https://catalog.mines.edu/undergraduate/programs/ams/#coursestext"
url = "https://catalog.mines.edu/undergraduate/programs/chemicalandbiologicalengineering/#coursestext"

# Fetch the page content
response = requests.get(url)
response.raise_for_status()  # Raise an error for bad status codes

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Find the section containing the courses
courses_section = soup.find('div', class_='sc_sccoursedescs')

if not courses_section:
    print("Error: Could not find the courses section.")
    exit()

# Extract course details
courses = []

# Regular expression to match course codes (e.g., MATH101, PHYS202)
course_code_pattern = re.compile(r'\b[A-Z]{4}\d{3}\b')

# Iterate over each course block
for course_block in courses_section.find_all('div', class_='courseblock'):
    title_block = course_block.find('p', class_='courseblocktitle')
    desc_block = course_block.find('p', class_='courseblockdesc')
    
    if not title_block or not desc_block:
        continue
    
    # Extract course title and number
    title_text = title_block.get_text(strip=True)
    
    # Split the title text to get course name and number
    title_parts = title_text.split('.')
    if len(title_parts) < 2:
        continue
    
    course_number = title_parts[0].strip()
    course_name = title_parts[1].strip()
    
    # Extract terms offered and prerequisites/corequisites from the description block
    desc_text = desc_block.get_text(strip=True)
    
    terms_offered = ""
    prerequisites = []
    corequisites = []
    
    # Extract terms offered
    if '(' in desc_text and ')' in desc_text:
        terms_offered = desc_text[desc_text.find('(')+1:desc_text.find(')')].strip()
    
    # Only consider the part of the description after terms offered
    terms_offered_end = desc_text.find(')')
    if terms_offered_end != -1:
        relevant_text = desc_text[terms_offered_end+1:].strip()
    else:
        relevant_text = desc_text

    # Extract all course codes from the relevant part of the description block
    for link in desc_block.find_all('a', href=True):
        course_code = link.get_text(strip=True)
        if course_code_pattern.match(course_code):
            if 'Prerequisite' in relevant_text:
                prerequisites.append(course_code)
            elif 'concurrent enrollment' in relevant_text or 'Corequisite' in relevant_text:
                corequisites.append(course_code)
    
    course_info = {
        'Course Name': course_name,
        'Course Number': course_number,
        'Terms Offered': terms_offered,
        'Prerequisites': prerequisites,
        'Corequisites': corequisites
    }
    
    courses.append(course_info)

# Convert the list of courses to JSON format
courses_json = json.dumps(courses, indent=4)

# Print the JSON
print(courses_json)

# Optionally, save the JSON to a file
with open('courses.json', 'w') as f:
    f.write(courses_json)