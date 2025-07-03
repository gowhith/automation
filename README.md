# LinkedIn Job Application Automation

An intelligent LinkedIn job application automation tool that uses AI to match job descriptions with your preferences and automatically applies to suitable positions.

## Features

- 🤖 **AI-Powered Matching**: Uses sentence transformers to calculate job relevance scores
- 🎯 **Smart Application**: Automatically applies to jobs with high match scores (≥75%)
- 📄 **Multi-Page Support**: Processes multiple pages of job listings
- ⚡ **Efficient Processing**: Optimized element detection and error handling
- 🔒 **Anti-Detection**: Chrome options to avoid bot detection
- 📊 **Detailed Logging**: Comprehensive progress tracking and statistics

## Prerequisites

- Python 3.8 or higher
- Chrome browser installed
- ChromeDriver (automatically managed by Selenium)

## Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Download ChromeDriver** (if not already installed):
   - The script will automatically download the appropriate ChromeDriver version
   - Or manually download from: https://chromedriver.chromium.org/

## Configuration

Edit the `CONFIG` dictionary in the script to customize:

```python
CONFIG = {
    'min_match_score': 60,      # Minimum score to consider applying (0-100)
    'max_jobs_per_page': 25,    # Maximum jobs to process per page
    'max_pages': 3,             # Maximum pages to search
    'wait_timeout': 10,         # Timeout for element waits (seconds)
    'scroll_pause': 2,          # Pause between scrolls (seconds)
}
```

## Usage

1. **Run the script**:
   ```bash
   python test_for _py.py
   ```

2. **Login to LinkedIn**:
   - The script will open LinkedIn login page
   - You have 30 seconds to manually log in
   - The script will verify successful login

3. **Monitor the process**:
   - Watch the console output for real-time progress
   - The script will show job details, match scores, and application status

## How It Works

1. **Setup**: Opens Chrome with anti-detection options
2. **Login**: Navigates to LinkedIn login page for manual authentication
3. **Search**: Goes to LinkedIn Jobs search page for "Data Scientist" positions
4. **Processing**: For each job:
   - Extracts job title, company, and location
   - Opens job details to get full description
   - Calculates AI similarity score with your target description
   - Applies automatically if score ≥ 75%
5. **Pagination**: Moves to next page and repeats until max pages reached
6. **Summary**: Displays total jobs processed and applications submitted

## Target Job Description

The script is configured to look for roles involving:
- Software Engineering Intern
- Software Development Intern
- Programming Intern
- Computer Science Intern
- Web Development Intern
- Full Stack Intern
- Frontend/Backend Intern
- Python/Java/JavaScript Intern
- React/Node.js Intern
- Database/API Intern
- Mobile App/UI/UX Intern
- DevOps/Cloud Intern
- Testing/QA Intern
- Remote or hybrid flexibility
- Competitive stipend
- Mentorship opportunities

You can modify the `target_job_description` variable to match your preferences.

## Safety Features

- **Rate Limiting**: Built-in delays to avoid overwhelming LinkedIn
- **Error Handling**: Graceful handling of network issues and element changes
- **Manual Override**: You can manually complete applications if needed
- **Session Management**: Proper cleanup of browser resources

## Troubleshooting

### Common Issues

1. **"No Easy Apply button found"**
   - Some jobs don't have Easy Apply option
   - The script will skip these automatically

2. **"Login verification failed"**
   - Ensure you're logged in within 30 seconds
   - Check if LinkedIn requires additional verification

3. **"Element not found" errors**
   - LinkedIn may have updated their interface
   - The script includes multiple fallback selectors

4. **ChromeDriver issues**
   - Ensure Chrome browser is up to date
   - Try reinstalling selenium: `pip install --upgrade selenium`

### Performance Tips

- **Lower the match score** (e.g., 60%) to apply to more jobs
- **Increase max_pages** to search more extensively
- **Adjust wait_timeout** based on your internet speed

## Important Notes

⚠️ **Use Responsibly**:
- This tool is for educational purposes
- Respect LinkedIn's terms of service
- Don't overwhelm the platform with too many applications
- Consider manual review of applications before submission

🔒 **Privacy**:
- Your login credentials are not stored
- All processing happens locally on your machine
- No data is sent to external servers

## Customization

### Changing Job Search Criteria

Edit the search URL in the `main()` function:
```python
search_url = "https://www.linkedin.com/jobs/search/?keywords=Software%20Engineer&location=United%20States"
```

### Modifying Target Description

Update the `target_job_description` variable:
```python
target_job_description = """
Looking for roles involving Software Engineering, Full Stack Development, 
React, Node.js, with competitive salary and benefits.
"""
```

## License

This project is for educational purposes. Please use responsibly and in accordance with LinkedIn's terms of service. 