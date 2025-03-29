# Italki Tutor Scraper

## Overview
This project is a web scraper designed to gather information about English tutors from the Italki platform. The scraper retrieves comprehensive data about each tutor, including their teaching specialties, ratings, and pricing information.

## Features
- Scrapes all available English tutors from the Italki API.
- Collects detailed information for each tutor,

## Data Storage
- Raw JSON responses are saved in the `pages` directory.
- Basic tutor information is saved in `italki_tutors.csv`.
- Detailed tutor information is saved in `italki_teachers_details.csv`.

## Usage
1. **Setup**: Ensure you have Python installed along with the required libraries. You can install the necessary packages using:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Scraper**: Execute the scraper by running:
   ```bash
   python italki_api_scraper.py
   ```

3. **Data Collection**: The scraper will continue to run until it has collected all available tutors or encounters an error. The total number of unique tutors collected will be displayed at the end of the run.

## Notes
- The scraper is designed to handle pagination and will stop when it detects that no new tutors are available.
- The current implementation has successfully detected a total of 784 unique tutors, which may be the total available on the platform or limited by the API's response.

## Future Improvements
- Implement a scheduling feature to run the scraper at regular intervals.
- Enhance error handling and logging for better debugging.
- Create a user interface for easier access to the collected data.

## License
This project is licensed under the MIT License.

## Customization

You can customize the scraper by modifying parameters:

```python
scrape_italki_teachers(
    output_csv='custom_output.csv',
    language='french',  # Change language
    max_pages=5,        # Limit number of pages
    delay=3             # Increase delay between requests
)
```

## Ethical Considerations

- This scraper is for educational purposes of University of Toronto.
- Be respectful of Italki's servers by using reasonable delays between requests.
- Check Italki's terms of service before using the data for commercial purposes.

## Troubleshooting

If you encounter issues:
1. Check your internet connection
2. Verify the API structure hasn't changed
3. Try increasing the delay between requests
4. Ensure you have the required packages installed