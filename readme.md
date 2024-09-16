
## Trend-Based Newsletter Generator

This project is a Flask web application that generates newsletter content based on current trending topics. It combines Twitter and Google Trends data to provide a comprehensive list of trending topics and then utilizes the Gemini Pro model from Google AI to create engaging content for each trend.

### Features

* **Trend Collection:**
    * Collects real-time trending topics from both Twitter and Google Trends for various countries.
    * Stores the collected trends data in a JSON file for future reference.
* **Content Generation:**
    * Generates a newsletter section for the top trends using the Gemini Pro model.
    * Provides a clear and engaging overview of each trend, including its significance and impact.
* **Customization:**
    * Users can select the country and model they want to use for generating content.
    * Supports a range of Gemini models, including `gemini-pro` and `gemini-1.5-flash`.
* **Easy Integration:**
    * The generated content is formatted in HTML, allowing for easy integration into your website or newsletter platform.
### Requirements

* Python 3.7 or higher
* Flask
* Markdown
* Google Generative AI
* tweepy
* pytrends
* dotenv
* JSON

### Installation

1. Create a virtual environment and activate it.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your environment variables (refer to the `.env` file example).
4. Obtain a Gemini Pro API key from Google AI and set the `GEMINI_API_KEY` environment variable.
5. Set up your Twitter API credentials (refer to the `.env` file example).

### Running the App

1. Run the app using the command:
   ```bash
   flask run
   ```
2. Access the application in your browser at `http://127.0.0.1:5000/`.

### Customization

* You can add more Gemini models to the `GEMINI_MODELS` list in `app.py`.
* Customize the content generation prompt and output format in the `generate_newsletter_content` function in `app.py`.
* Add more countries to the `COUNTRIES` list in `trend_collector.py`.
