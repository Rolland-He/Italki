import json
import csv
import os
import glob

def extract_tutor_info(json_file='pages/page_1.json'):
    """
    Extract just tutor names and IDs from the JSON data and append to a CSV file
    """
    # Path to CSV file
    output_csv = 'italki_tutors.csv'
    
    if not os.path.exists(json_file):
        print(f"Error: {json_file} does not exist. Please run the scraper first.")
        return 0
    
    try:
        # Load JSON data
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        tutors = []
        existing_tutor_ids = set()
        
        # Check if CSV file exists and read existing tutor IDs
        if os.path.exists(output_csv):
            with open(output_csv, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    existing_tutor_ids.add(row['tutor_id'])
            print(f"Found {len(existing_tutor_ids)} existing tutors in the CSV file.")
        
        # Check if data has expected structure
        teachers = []
        if 'data' in data and isinstance(data['data'], list):
            teachers = data['data']
            print(f"Found {len(teachers)} teachers in the JSON data.")
        else:
            print("Warning: Could not find teachers in the expected format.")
            print("JSON structure:")
            print(json.dumps(data, indent=2)[:500] + "...")
            return 0
        
        # Process each teacher
        for teacher in teachers:
            user_info = teacher.get('user_info', {})
            
            tutor_id = str(user_info.get('user_id', ''))
            tutor_name = user_info.get('nickname', '')
            
            # Skip if we already have this tutor
            if tutor_id in existing_tutor_ids:
                print(f"Skipping tutor {tutor_name} (ID: {tutor_id}) - already in CSV")
                continue
            
            tutors.append({
                'tutor_name': tutor_name,
                'tutor_id': tutor_id
            })
        
        # Append to CSV
        if tutors:
            write_header = not os.path.exists(output_csv)
            with open(output_csv, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['tutor_name', 'tutor_id']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                if write_header:
                    writer.writeheader()
                
                writer.writerows(tutors)
            
            print(f"Successfully added {len(tutors)} new tutors.")
            print(f"Data appended to {output_csv}")
            
            # Print the list of new tutors
            print("\nNew tutors added:")
            for tutor in tutors:
                print(f"{tutor['tutor_name']} (ID: {tutor['tutor_id']})")
        else:
            print("No new tutors found to add.")
        
        return len(tutors)
    
    except Exception as e:
        print(f"Error processing JSON file: {e}")
        import traceback
        traceback.print_exc()
        return 0

def save_json_with_incremented_filename(data):
    """
    Save JSON data to a file with an automatically incremented filename
    """
    # Create pages directory if it doesn't exist
    os.makedirs('pages', exist_ok=True)
    
    # Find the highest existing page number
    existing_files = glob.glob('pages/page_*.json')
    if not existing_files:
        next_page = 1
    else:
        page_numbers = []
        for file_path in existing_files:
            try:
                filename = os.path.basename(file_path)  # e.g., page_1.json
                page_num = int(filename.split('_')[1].split('.')[0])  # Extract 1 from page_1.json
                page_numbers.append(page_num)
            except (IndexError, ValueError):
                continue
        
        next_page = max(page_numbers) + 1 if page_numbers else 1
    
    # Save the JSON file
    output_file = f'pages/page_{next_page}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"Saved JSON data to {output_file}")
    return output_file

if __name__ == "__main__":
    # If running directly, process the most recent JSON file
    json_files = sorted(glob.glob('pages/page_*.json'))
    
    if json_files:
        most_recent_file = json_files[-1]
        print(f"Processing most recent file: {most_recent_file}")
        extract_tutor_info(most_recent_file)
    else:
        print("No JSON files found in the pages directory.") 