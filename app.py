import os, json, markdown
from flask import Flask, render_template, request
import google.generativeai as genai
from trend_collector import collect_and_store_trends, COUNTRIES

app = Flask(__name__, static_folder='static')

# Configure Gemini API (replace with your actual API key)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

GEMINI_MODELS = [
    'gemini-pro',
    'gemini-1.5-flash',
    # Add other models here as they become available
]

def get_latest_trends():
    try:
        with open("trends_data.json", "r") as f:
            data = json.load(f)
        return data["twitter_trends"], data["google_trends"],  data.get("country_code", "united_states")
    except FileNotFoundError:
        return [], [], "united_states"

@app.route('/', methods=['GET', 'POST'])
def index():
    content = ""
    twitter_trends = []
    google_trends = []
    selected_country = "united_states"
    selected_model = "gemini-1.5-flash"
    
    if request.method == 'POST':
        selected_country = request.form.get('country')
        selected_model = request.form.get('model', 'gemini-1.5-flash')  # Default to gemini-pro
        collect_and_store_trends(selected_country)  # Refresh trends
    
    twitter_trends, google_trends, stored_country = get_latest_trends()
    selected_country = stored_country if stored_country else selected_country
    combined_trends = twitter_trends + google_trends

    if combined_trends:
        content = generate_newsletter_content(combined_trends[:5], selected_country, selected_model)  # Use top 20 combined trends
    return render_template('index.html', content=content, twitter_trends=twitter_trends, google_trends=google_trends, 
                           selected_country=selected_country, COUNTRIES=COUNTRIES, selected_model=selected_model, GEMINI_MODELS=GEMINI_MODELS)

def generate_newsletter_content(trends, country_code, selected_model):
    trend_names = ", ".join([trend["name"] for trend in trends])
    # model = genai.GenerativeModel('gemini-pro')
    model = genai.GenerativeModel(selected_model)
    prompt = f"""Generate a newsletter section about these trends: {trend_names}. 
        Output Format:
        1. Main Headline:
        [Create a catchy main headline that combines the top three trends]
        For each trend, provide the following on separate lines:
        2. Trend Sections:
        For each trend, provide:
        - Trend Headline: [Catchy headline for the specific trend]
        - Overview: [Brief description of the trend, its significance, impact, and any notable events. Aim for about 200-350 words per trend.]
        Please ensure each trend is clearly separated with its own headline and overview. Make headline more than just name of the trend be creative.
        Do not include following on the output 
        - Use of word headline
        - Any additional subheadings or sections beyond what is specified above."""
    print(f"Generating content for trends in {country_code}: {trend_names}")
    response = model.generate_content(prompt)
        
    # Convert Markdown to HTML
    html_content = markdown.markdown(response.text)
    return html_content

if __name__ == '__main__':
    app.run(debug=True)