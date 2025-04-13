import requests
import json
import csv
import os
import time
from datetime import datetime
from extract_tutors import extract_tutor_info, save_json_with_incremented_filename


def get_page(page=1, origin_country_ids=None, teacher_type=None):
    """
    Fetch a page of English teachers from the italki API
    
    Args:
        page: Page number to fetch
        origin_country_ids: List of country codes to filter by (e.g. ["US", "GB"])
        teacher_type: Filter by teacher type (1 or 2)
    """
    # Based on the example payload in try.py
    payload = {
        "teach_language": {
            "language": "english",
        },
        "page": page,
        "page_size": 20,
        "has_package": 0  # Filter teachers without package lessons
    }
    
    # Add teacher_info filters (country and teacher type)
    if "teacher_info" not in payload:
        payload["teacher_info"] = {}
        
    # Add origin country filter if provided
    if origin_country_ids and isinstance(origin_country_ids, list) and len(origin_country_ids) > 0:
        payload["teacher_info"]["origin_country_id"] = origin_country_ids
    
    # Add teacher type filter if provided
    if teacher_type is not None:
        payload["teacher_info"]["teacher_type"] = teacher_type
    
    url = 'https://api.italki.com/api/v2/teachers'
    headers = {
        'authority': 'api.italki.com',
        'accept-language': 'en-us',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36',
        'content-type': 'application/json',
        'accept': 'application/json, text/plain, */*',
        'origin': 'https://www.italki.com',
        'referer': 'https://www.italki.com/',
    }
    
    print(f"Requesting page {page}...")
    print(f"Request payload: {json.dumps(payload)}")
    if origin_country_ids:
        print(f"Filtering by origin countries: {', '.join(origin_country_ids)}")
    if teacher_type is not None:
        print(f"Filtering by teacher type: {teacher_type}")
    print("Filtering to only show teachers without package lessons")
    
    response = requests.post(url, json=payload, headers=headers)
    
    # Check if response contains JSON data
    try:
        data = response.json()
        
        # Print sample teacher info for debugging
        if 'data' in data and isinstance(data['data'], list) and len(data['data']) > 0:
            sample_teacher = data['data'][0]
            teacher_info = sample_teacher.get('teacher_info', {})
            sample_teacher_type = teacher_info.get('teacher_type')
            print(f"Sample teacher found, teacher_type: {sample_teacher_type}")
                
        return data
    except json.JSONDecodeError:
        print(f"Error: Response is not valid JSON. First 200 characters of response: {response.text[:200]}")
        # Save the full response to a file for inspection
        with open("error_response.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"Full response saved to error_response.html")
        
        # Return an empty dict to avoid errors
        return {"error": "Failed to decode JSON response"}

def get_total_pages(data):
    """Calculate the total number of pages based on API response"""
    try:
        # Try to get pagination information
        # In the newer API, we can't get explicit page info, but we can estimate from the data
        if 'data' in data and isinstance(data['data'], list):
            # If we got 20 items (full page), then we assume there are more pages
            items_per_page = 20  # Default page size
            if len(data['data']) >= items_per_page:
                # We can't determine the exact total, so return a very high number
                # to ensure we keep going until we actually run out of data
                return 999, items_per_page * 999
            else:
                # If less than a full page, we're probably on the last page
                return 1, len(data['data'])
        
        # Fallback to old API format
        if 'paging' in data:
            total = data.get('paging', {}).get('total', 0)
            per_page = data.get('paging', {}).get('per_page', 20)
            return total // per_page + (1 if total % per_page else 0), total
            
        # If we can't determine the pagination, assume there are many pages
        return 999, 999 * 20  # Essentially unlimited
    except Exception as e:
        print(f"Error determining total pages: {e}")
        return 999, 999 * 20  # Essentially unlimited

def has_next(data, current_page):
    """Check if there are more pages - NO MAX PAGE LIMIT"""
    # If the current page had a full set of results, assume there are more
    if 'data' in data and isinstance(data['data'], list):
        return len(data['data']) >= 20  # 20 is the default page size
    
    # Fallback to checking if we found teachers
    teachers = []
    if 'teachers' in data:
        teachers = data.get('teachers', [])
    elif 'data' in data and isinstance(data['data'], list):
        teachers = data.get('data', [])
    
    # If we found teachers on this page, assume there might be more
    return len(teachers) > 0

def extract_teacher_data(teacher):
    """Extract comprehensive information from a teacher record"""
    user_info = teacher.get('user_info', {})
    teacher_info = teacher.get('teacher_info', {})
    course_info = teacher.get('course_info', {})
    
    # Extract basic info
    teacher_id = user_info.get('user_id', '')
    name = user_info.get('nickname', '')
    
    # Extract teacher type
    teacher_type = teacher_info.get('teacher_type', '')
    
    # Extract origin country and living country
    origin_country = user_info.get('origin_country_id', '')
    living_country = user_info.get('living_country_id', '')
    
    # Extract ratings and stats
    rating = teacher_info.get('overall_rating', '')
    student_count = teacher_info.get('student_count', 0)
    session_count = teacher_info.get('session_count', 0)
    
    # Extract languages taught
    languages_taught = []
    for lang in teacher_info.get('teach_language', []):
        languages_taught.append(f"{lang.get('language', '')}: {lang.get('level', '')}")
    
    # Extract teaching date
    first_valid_time = teacher_info.get('first_valid_time', '')
    if first_valid_time:
        try:
            dt = datetime.strptime(first_valid_time, "%Y-%m-%dT%H:%M:%SZ")
            first_valid_time = dt.strftime("%Y-%m-%d")
        except ValueError:
            pass
    
    # Extract price information
    price = course_info.get('min_price', 0) / 100  # Convert cents to dollars
    trial_price = course_info.get('trial_price', 0) / 100
    
    # Extract specialties
    specialties = []
    for cert in teacher_info.get('specialty_cert', []):
        specialties.append(cert.get('certificate', ''))
    
    
    return {
        "Teacher ID": teacher_id,
        "Name": name,
        "Teacher Type": teacher_type,
        "Origin Country": origin_country,
        "Living Country": living_country,
        "Overall Rating": rating,
        "Student Count": student_count,
        "Session Count": session_count,
        "Languages Taught": '; '.join(languages_taught),
        "Teaching Since": first_valid_time,
        "Price": price,
        "Trial Price": trial_price,
        "Specialties": '; '.join(specialties),
    }

if __name__ == "__main__":
    # Create directory for json files if it doesn't exist
    os.makedirs('pages', exist_ok=True)
    
    # Initialize tracking variables
    page = 1
    total_teachers = 0
    known_teacher_ids = set()
    known_detailed_teacher_ids = set()  # Track IDs in the detailed CSV separately
    consecutive_empty_pages = 0
    max_consecutive_empty_pages = 100  # Effectively disabled - will continue until we run out of pages
    
    # Filter by origin country (set to None to get all countries)
    origin_country_filter = [
        "US" 
    ]
    
    # Filter by teacher type
    # 1 = One type of teacher
    # 2 = Another type of teacher
    # None = Both types
    teacher_type_filter = 2  # Set to filter for teacher_type 1
    
    filter_description = []
    if origin_country_filter:
        filter_description.append(f"countries: {', '.join(origin_country_filter)}")
    if teacher_type_filter is not None:
        filter_description.append(f"teacher type: {teacher_type_filter}")
    
    if filter_description:
        print(f"Starting dynamic scraping of tutors filtered by {' and '.join(filter_description)}...")
    else:
        print("Starting dynamic scraping of all available tutors...")
    
    print("Will continue until we encounter an error or stop finding new tutors")
    
    try:
        # Read existing tutor IDs from CSV if it exists
        csv_file = 'italki_tutors.csv'
        if os.path.exists(csv_file):
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'tutor_id' in row:
                        known_teacher_ids.add(row['tutor_id'])
                    elif 'Teacher ID' in row:
                        known_teacher_ids.add(row['Teacher ID'])
            print(f"Found {len(known_teacher_ids)} existing tutors in CSV file")
            
        # Read existing teacher IDs from detailed CSV if it exists
        details_csv_file = 'italki_teachers_details.csv'
        if os.path.exists(details_csv_file):
            with open(details_csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'Teacher ID' in row:
                        known_detailed_teacher_ids.add(str(row['Teacher ID']))
            print(f"Found {len(known_detailed_teacher_ids)} existing tutors in detailed CSV file")
        
        # Keep scraping until we hit a stopping condition
        while True:
            # Get data for current page
            data = get_page(page, origin_country_filter, teacher_type_filter)
            
            # Save raw JSON response with incremented filename
            json_file = save_json_with_incremented_filename(data)
            print(f"Raw JSON data saved to {json_file}")
            
            # Update the CSV file with the new tutors
            new_tutor_count = extract_tutor_info(json_file)
            
            # Check if there was an error with the JSON response
            if 'error' in data:
                print(f"Error in API response: {data['error']}")
                break
            
            # Process teachers on this page
            teachers = []
            if 'teachers' in data:
                teachers = data.get('teachers', [])
            elif 'data' in data and isinstance(data['data'], list):
                teachers = data.get('data', [])
            
            page_count = len(teachers)
            print(f'Found {page_count} teachers on page {page}')
            total_teachers += page_count
            
            # If no teachers found, break the loop
            if not teachers:
                print("No teachers found on this page. We've reached the end.")
                break
            
            # Check if we've hit our consecutive empty pages limit
            if new_tutor_count == 0:
                consecutive_empty_pages += 1
                print(f"No new tutors on page {page}. ({consecutive_empty_pages}/{max_consecutive_empty_pages})")
                
                if consecutive_empty_pages >= max_consecutive_empty_pages:
                    print(f"Reached {max_consecutive_empty_pages} consecutive pages with no new tutors. Stopping.")
                    break
            else:
                # Reset the counter if we found new tutors
                consecutive_empty_pages = 0
                print(f"Found {new_tutor_count} new tutors on page {page}. Continuing search...")
            
            # Extract comprehensive teacher data for CSV
            page_teacher_data = [extract_teacher_data(teacher) for teacher in teachers]
            
            # Filter out duplicates for the detailed CSV
            new_teacher_data = []
            for teacher in page_teacher_data:
                teacher_id = str(teacher["Teacher ID"])
                # Check if this teacher is already in our detailed database or this page's batch
                if teacher_id not in known_detailed_teacher_ids and not any(t["Teacher ID"] == teacher_id for t in new_teacher_data):
                    new_teacher_data.append(teacher)
                    known_detailed_teacher_ids.add(teacher_id)  # Add to our tracking set
            
            # Save to CSV - append mode to avoid losing previous data
            details_csv_file = 'italki_teachers_details.csv'
            
            # Check if file exists to determine if we need to write headers
            file_exists = os.path.isfile(details_csv_file)
            
            # Only write to the file if we have new teacher data
            if new_teacher_data:
                print(f"Adding {len(new_teacher_data)} new teachers to detailed CSV")
                with open(details_csv_file, 'a', newline='', encoding='utf-8') as csvfile:
                    fieldnames = list(new_teacher_data[0].keys())
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    if not file_exists:
                        writer.writeheader()
                        
                    writer.writerows(new_teacher_data)
            
            # Add a small delay between requests to be nice to the server
            time.sleep(0.5)
            
            # Increment page number for next iteration
            page += 1
            
    except Exception as e:
        print(f"Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\nScraping Summary:")
        print(f"Pages scraped: {page-1}")
        print(f"Total teachers seen in this run: {total_teachers}")
        print(f"Total unique teachers in database: {len(known_detailed_teacher_ids)}")
        if origin_country_filter:
            print(f"Filter applied: Origin countries {', '.join(origin_country_filter)}")
        if teacher_type_filter is not None:
            print(f"Filter applied: Teacher type {teacher_type_filter}")
        print(f"Scraping complete. Data saved to:")
        print(f"- italki_tutors.csv (basic info)")
        print(f"- italki_teachers_details.csv (detailed info)")
        print(f"- Individual JSON files in the 'pages' directory")