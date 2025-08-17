# IRC Project

An end-to-end toolkit for conducting in-depth Instagram hashtag and user analysis via command-line and GUI interfaces.

## Features

- **irc_analysis.py**  
  Command-line analytics for hashtag and profile data, including:
  - CSV import/export  
  - Frequency analysis and sorting  
  - Automated logging of key metrics  

- **irc_analysis_gui.py**  
  PyQt5-powered desktop GUI offering:
  - Intuitive data loading and filtering  
  - Real-time charts and tables (via Matplotlib)  
  - Interactive export of filtered results  

- **QR Code Utilities**  
  - `qr_scanner/` module for scanning and decoding QR images  
  - Batch scanning support with CSV output  

- **User Management**  
  - `signin_system/` for user authentication and role-based access  
  - Secure storage of credentials in `users.csv`  

- **Data**  
  - `event.csv` and `scanned_data.csv` samples for processing  
  - `sorted.csv` and `event_analysis.log` generated via analysis runs  

## Requirements

- Python 3.7+  
- PyQt5  
- pandas, matplotlib  
- qrcode, pillow (for QR utilities)  

## Installation

1. Clone the repo:  
   ```bash
   git clone https://github.com/IchigoSolos69/IRC.git
   cd IRC
   ```

2. Install dependencies:  
   ```bash
   pip install PyQt5 pandas matplotlib qrcode pillow
   ```

## Usage

### Command-Line Analysis

```bash
python irc_analysis.py --input event.csv --output sorted.csv
```

Follow on-screen prompts to filter by hashtag frequency, date, or user.

### GUI Analysis

```bash
python irc_analysis_gui.py
```

Use the file picker to load CSV data, explore tables, and export results.

### QR Scanner

```bash
python qr_scanner/scan.py --folder instagram_qr.png --output scanned_data.csv
```

## File Structure

```
IRC/
├── irc_analysis.py           # CLI analysis script
├── irc_analysis_gui.py       # GUI application
├── qr_scanner/               # QR code scanning module
├── signin_system/            # Authentication module
├── event.csv                 # Sample event data
├── scanned_data.csv          # Sample scanned QR data
├── sorted.csv                # Example sorted output
├── event_analysis.log        # Sample analysis log
└── README.md                 # This file
```


***

*“Decode data, unlock insights.”*



[1] https://github.com/IchigoSolos69/IRC
