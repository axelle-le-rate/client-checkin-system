# Client-Check-In

A lightweight AI-powered pipeline that helps concierge banks stay informed about their clients' lives so no important moment falls through the cracks.

## The Problem
Private concierge banks build their brand on personal relationships. But with dozens of clients across very different life situations — nonprofit directors, professional poker players, athletes, business owners — it is nearly impossible to keep up with everyone manually. A client might get acquired, face a legal issue, or experience a major life event, and the bank finds out too late or not at all.
The result is that follow-up slacks, the data the bank has is not actionable, and the personal relationship that defines the concierge experience starts to suffer.

## The Solution
A client check-in system where clients periodically share life and business updates through a simple Google Form. The bank's team gets an AI-powered dashboard that reads those responses, flags anything significant, and tells the banker exactly who to reach out to and why.
The banker still makes the call. The AI just makes sure nobody falls through the cracks.

## How It Works

1. Clients receive a Google Form link and fill out a short monthly check-in
2. Responses flow automatically into a Google Sheet
3. Make.com detects each new response and sends an email alert to the banker with a link to the dashboard
4. A Python script reads the sheet, sends each response to Gemini AI for analysis, and generates a structured summary
5. The Streamlit dashboard displays all responses with urgency levels, categories, AI summaries, and recommended banker actions

## The Form

Clients receive a simple, mobile-friendly check-in form with conditional logic that adapts based on their answers.

![Form Page 1](/Users/axellejimenez/Desktop/gf1.png)
![Form Page 2](/Users/axellejimenez/Desktop/gf2.png)
![Form Page 3](/Users/axellejimenez/Desktop/gf3.png)

## Tech Stack

- Google Forms — client-facing check-in form with conditional logic

- Google Sheets — automatic response storage

- Make.com — no-code automation for banker email notifications

- Python — core pipeline logic

- gspread — connects Python to Google Sheets via API

- Google Gemini AI — analyzes client responses and generates structured recommendations

- Streamlit — interactive banker-facing dashboard

- pandas — data manipulation and dataframe management

- python-dotenv — secure API key management

## Project Structure
```
client-checkin-system/
├── app.py                        # Streamlit dashboard
├── client_checkin_notebook.ipynb # Full pipeline walkthrough
├── .env.example                  # Template for environment variables
├── .gitignore                    # Excludes sensitive files from GitHub
└── README.md                     # This file
```

## Setup Instructions

### 1. Clone the repository

git clone https://github.com/yourusername/client-checkin-system.git
cd client-checkin-system

###2. Install dependencies

pip install streamlit gspread google-auth google-genai pandas python-dotenv
```
### 3. Set up Google Sheets API
- Go to console.cloud.google.com and create a new project
- Enable the Google Sheets API and Google Drive API
- Create a service account and download the JSON key file
- Rename the file to `credentials.json` and place it in the project folder
- Share your Google Sheet with the service account email address

### 4. Set up your Gemini API key
- Go to aistudio.google.com and generate a free API key
- Create a `.env` file in the project folder using `.env.example` as a template:
```
GEMINI_API_KEY=your-key-here

### 5. Run the dashboard

streamlit run app.py


## Future Improvements

. Deep link from the banker notification email directly to the specific client's record in the dashboard rather than the main page

. Group multiple check-ins per client so each person appears once in the dashboard with a full history of their submissions

. Add a biweekly automated form distribution so clients receive the check-in link on a schedule without manual outreach

. Build a client profile system that tracks patterns across check-ins over time
