import requests
import re
import json
from datetime import datetime
import os
import csv
import time
import random

def get_data(teacher_id):
    url = f"http://italki.com/en/teacher/{teacher_id}/english"
    response = requests.get(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })

    pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'

    matches = re.search(pattern, response.text, re.DOTALL)
    if matches:
        try:
            data = json.loads(matches.group(1))
            return data['props']['pageProps']['teacher'], data['props']['currency']
        except json.JSONDecodeError:
            print(f"Found match with pattern {pattern[:30]}... but couldn't decode JSON")
            return None, None
    else:
        print(f"No pattern match found for teacher ID {teacher_id}")
        return None, None

def write_to_csv(filename, data):
    """
    Write a list of 18 elements to the next line of a CSV file.
    Creates the file with headers if it doesn't exist.
    """
    
    headers = [
        "user_id", "nickname", "first_valid_time", "session_count", "timezone"
    ]
    
    file_exists = os.path.isfile(filename)
    
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write headers if file is being created
        if not file_exists:
            writer.writerow(headers)
        
        # Write data row
        writer.writerow(data)

def read_teacher_ids(filename="italki_tutors.csv"):
    """
    Read teacher IDs from a CSV file with the format:
    tutor_name,tutor_id
    
    Parameters:
    filename (str): The name of the CSV file containing tutor information
    
    Returns:
    list: A list of tutor IDs as integers
    """
    teacher_ids = []
    try:
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            # Skip the header row
            next(reader, None)
            
            for row in reader:
                if len(row) >= 2:  # Ensure we have at least 2 columns
                    try:
                        # Extract the tutor_id from the second column
                        tutor_id = int(row[1].strip())
                        teacher_ids.append((tutor_id, row[0].strip()))  # Store both ID and name
                    except ValueError:
                        # Skip rows where the ID isn't a valid integer
                        print(f"Warning: Could not convert '{row[1]}' to integer. Skipping this tutor.")
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found. Please ensure it exists in the workspace.")
    except Exception as e:
        print(f"Error reading file '{filename}': {str(e)}")
    
    return teacher_ids

def extract_teacher_fields(teacher_data, currency, teacher_id, teacher_name):
    """Extract the specific fields we need from the teacher data"""
    # Extract the fields we need
    user_id = str(teacher_id)  # Use the ID we already have
    nickname = teacher_data.get('user_info', {}).get('nickname', teacher_name)
    timezone = teacher_data.get('user_info', {}).get('timezone', '')
    session_count = teacher_data.get('teacher_info', {}).get('session_count', 0)
    
    # Extract teaching date (first_valid_time)
    first_valid_time = teacher_data.get('teacher_info', {}).get('first_valid_time', '')
    if first_valid_time:
        try:
            dt = datetime.strptime(first_valid_time, "%Y-%m-%dT%H:%M:%SZ")
            first_valid_time = dt.strftime("%Y-%m-%d")
        except ValueError:
            pass
    
    return [
        user_id,
        nickname,
        first_valid_time,
        session_count,
        timezone
    ]

def get_processed_ids(filename):
    """Get list of teacher IDs already processed"""
    processed_ids = set()
    
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)  # Skip header
            for row in reader:
                if row and len(row) > 0:
                    processed_ids.add(int(row[0]))
    
    return processed_ids

if __name__ == '__main__':
    input_filename = "italki_tutors.csv"
    output_filename = "italki_newdetails.csv"
    
    # Get already processed teacher IDs
    processed_ids = get_processed_ids(output_filename)
    print(f"Found {len(processed_ids)} already processed teachers")
    
    # Get teacher IDs from CSV
    teacher_info = read_teacher_ids(input_filename)
    print(f"Loaded {len(teacher_info)} teachers from {input_filename}")
    
    # Filter out already processed teachers
    teacher_info = [(tid, name) for tid, name in teacher_info if tid not in processed_ids]
    print(f"Need to process {len(teacher_info)} teachers")
    
    total_processed = 0
    for i, (teacher_id, teacher_name) in enumerate(teacher_info):
        start_time = time.time()
        
        # Skip if already processed
        if teacher_id in processed_ids:
            continue
        
        print(f"Processing teacher {teacher_id}: {teacher_name}")
        
        # Get teacher data
        teacher_data, currency = get_data(teacher_id)
        
        if teacher_data is None:
            print(f"Failed to get data for teacher {teacher_id}")
            continue
        
        # Extract fields
        data = extract_teacher_fields(teacher_data, currency, teacher_id, teacher_name)
        
        # Write to CSV
        write_to_csv(output_filename, data)
        
        # Add to processed IDs set to prevent duplicates within this run
        processed_ids.add(teacher_id)
        
        total_processed += 1
        end_time = time.time()
        
        # Output progress
        print(f"[{i+1}/{len(teacher_info)}] {teacher_id}: {end_time - start_time:.2f}s")
        
        # Add delay between page requests to avoid rate limiting
        if i < len(teacher_info) - 1:
            delay = 0.2 + random.uniform(0, 0.5)  # Random delay between 0.5-1 seconds
            print(f"Waiting {delay:.2f}s before next request...")
            time.sleep(delay)
    
    print(f"\nProcessing complete!")
    print(f"Processed {total_processed} teachers")
    print(f"Results saved to {output_filename}")





