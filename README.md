# Cargo Tracking System
[Watch the demo video](./video.mp4)

An intelligent cargo tracking system that automates the process of tracking shipping containers using HMM's tracking system. The system uses browser automation to fetch real-time tracking information and generates interactive route maps.

## 🌟 Features

- **Automated Tracking**: Fetches real-time cargo tracking information
- **Interactive Maps**: Generates visual route maps between ports
- **Multiple Identifiers**: Works with booking references, container numbers, or B/L numbers
- **Headless Mode**: Option to run without a browser UI for server use
- **History Tracking**: Maintains a history of all tracked shipments
- **Simple CLI**: Easy-to-use command-line interface

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Google Chrome browser installed
- Google API key with access to Google Maps and Gemini

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/cargo-tracker.git
   cd cargo-tracker
   ```

2. **Set up a virtual environment** (recommended):
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   # or
   source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browser**:
   ```bash
   playwright install
   ```

5. **Create a `.env` file** in the project root with your API key:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```

## 🛠 Usage

### Basic Tracking

```bash
python cargo_tracker.py YOUR_REFERENCE_ID
```

### Headless Mode (no browser UI)

```bash
python cargo_tracker.py YOUR_REFERENCE_ID --headless
```

### Example

```bash
python cargo_tracker.py HMMU1234567 --headless
```

### Where to Find Your Reference ID

You can use any of these as your reference ID:
- Booking number (e.g., `HMMU1234567`)
- Bill of Lading (B/L) number
- Container number (e.g., `HMCU1234567`)

These can typically be found in your shipping documents, booking confirmation emails, or invoices.

## 📂 Project Structure

```
cargo-tracker/
├── .env                    # Environment variables
├── cargo_tracker.py        # Main application code
├── requirements.txt        # Python dependencies
└── tracking_results/      # Directory for tracking history and maps
    ├── tracking_history.json  # JSON log of all tracked shipments
    └── route_*.html          # Interactive route maps
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```
GOOGLE_API_KEY=your_google_api_key_here
```

### Command Line Arguments

- `reference_id`: The booking reference, container number, or B/L number to track
- `--headless`: (Optional) Run in headless mode (no browser UI)

## 📝 Output

For each tracking request, the system will:
1. Display tracking information in the console
2. Save the tracking data to `tracking_results/tracking_history.json`
3. Generate an interactive map in `tracking_results/` if port information is available

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Uses [Playwright](https://playwright.dev/) for browser automation
- [Google Maps API](https://developers.google.com/maps) for geocoding and mapping
- [Folium](https://python-visualization.github.io/folium/) for interactive maps
- [LangChain](https://python.langchain.com/) for LLM integration
