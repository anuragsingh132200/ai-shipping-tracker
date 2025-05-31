# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install

# Run the tracker (replace YOUR_REFERENCE_ID)
python cargo_tracker.py YOUR_REFERENCE_ID

# Run in headless mode
python cargo_tracker.py YOUR_REFERENCE_ID --headless