# AI-based Shipping Line Tracker
[Watch the demo video](./video.mp4)

An automated shipping container tracking system that uses AI to fetch voyage details from HMM's cargo tracking service.

## Features

- Automated tracking of HMM shipping containers
- Extracts voyage numbers and arrival dates
- Caches results to prevent duplicate requests
- Uses browser automation with AI assistance

## Prerequisites

- Python 3.8 or higher
- Chrome browser installed
- OpenAI API key

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/anuragsingh132200/ai-shipping-tracker.git
cd ai-shipping-tracker
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Unix/MacOS
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

Run the tracker with:
```bash
python tracker.py
```

The script will:
1. Check if results for the booking ID already exist
2. If not, navigate to the HMM tracking website
3. Enter the booking ID and extract voyage details
4. Save results to `results.json`

## Output Format

Results are stored in `results.json` in the following format:
```json
{
  "booking_id": "SINI25432400",
  "result": {
    "voyage_number": "YM MANDATE 0096W",
    "arrival_date": "2025-03-28 10:38"
  }
}
```

## Project Structure

- `tracker.py`: Main script that handles the tracking logic
- `requirements.txt`: Project dependencies
- `.env`: Environment variables configuration
- `results.json`: Cache file for tracking results
- `.gitignore`: Git ignore configuration

## Dependencies

- browser-use: For AI-powered browser automation
- langchain-openai: For OpenAI integration
- python-dotenv: For environment variable management
- pydantic: For data validation

## License

MIT License

## Contributing

Feel free to open issues and pull requests for any improvements.
