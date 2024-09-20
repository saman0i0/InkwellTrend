
## Trend Newsletter Generator

This application collects trending topics from Google Trends and Reddit and generates a customizable newsletter section based on them using Google's Gemini API.

### Features

- **Trend Aggregation:** Pulls trending searches from Google Trends and top posts from Reddit's r/all for a comprehensive view of current trends.
- **Country-Specific Trends:**  Retrieves Google Trends data for specific countries, allowing users to tailor the newsletter to different regions.
- **Customizable Newsletter Content:**  Utilizes the Gemini AI model to generate newsletter content. Users can adjust the:
    - Number of trends to include
    - Preferred Gemini model 
    - Keywords to focus on
    - Overall tone of the writing (Informative, Humorous, Formal, Casual)
- **Markdown to HTML Conversion:**  The generated newsletter content is formatted using Markdown and then automatically converted to HTML for easy integration into existing platforms.
- **Error Handling and User Feedback:** Includes error handling mechanisms and user-friendly messages (using Flask's flash messaging) to provide a smooth experience. 

### How It Works

1. **Trend Collection:** The `trend_collector.py` module retrieves:
    - Top Google search trends for a specific country using the `pytrends` library. 
    - Hot posts from Reddit's r/all subreddit using the `praw` library, considering post scores and comments for relevancy.
2. **Trend Storage:** Collected trends are saved to `trends_data.json` with a timestamp for later retrieval. 
3. **Flask Web Application:** The `app.py` file uses Flask to:
    - Render a web interface where users can:
        - Select a country to fetch trends from.
        - Choose the number of trends to include. 
        - Specify optional keywords.
        - Select the desired tone of the newsletter content.
    - Handle user submissions and call the `generate_newsletter_content` function.
4. **Newsletter Generation:** The `generate_newsletter_content` function:
    - Structures a prompt for the Gemini AI model. The prompt includes:
        - A list of the collected trends
        - User-specified keywords 
        - Tone instructions 
        - Specific formatting requests (headlines, overviews)
    - Sends the prompt to the Gemini API for content generation.
    - Converts the generated Markdown response into HTML. 
5. **Content Display:** The generated HTML content is displayed on the webpage, providing a ready-to-use newsletter section. 

### Setup and Installation

1. **Prerequisites:** Ensure you have Python 3.7 or higher installed. 
2. **Clone the repository:**
   ```bash
   git clone https://github.com/saman0i0/InkwellTrend
   cd your-repo 
   ```
3. **Create a Virtual Environment (Recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt 
   ```
5. **Obtain API Keys:**
   - **Gemini API Key:**  
      - Follow instructions at [https://developers.generativeai.google](https://developers.generativeai.google) to obtain an API key and set the `GEMINI_API_KEY` environment variable in your system. 
   - **Reddit API Credentials:**
      - Create an app on Reddit's developer platform: [https://www.reddit.com/prefs/apps/](https://www.reddit.com/prefs/apps/)
      - Get your client ID, client secret, and set up a user agent string. Store these as environment variables: `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, and `REDDIT_USER_AGENT`.
6. **Run the application:**
   ```bash
   flask run 
   ```
7. **Access the app in your browser:**  Go to `http://127.0.0.1:5000/`


This project uses open-source libraries for trend analysis and content generation and provides a basic but customizable framework for automatically creating engaging newsletter content. 
### Video Demo
[screen-capture (1).webm](https://github.com/user-attachments/assets/f5b7f37b-624f-471a-ae85-4d2c821b9842)
