import os, json, markdown
from flask import Flask, render_template, request, flash
import google.generativeai as genai
from trend_collector import collect_and_store_trends, COUNTRIES

app = Flask(__name__, static_folder='static')
app.secret_key = os.urandom(24) # Necessary for flash messages

# Configure Gemini API
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
        return data["twitter_trends"], data["google_trends"],  data.get("country_code", "united_states"), data.get("errors", [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        flash(f"Error: Unable to retrieve trends data. ({e})", 'error')
        return [], [], "united_states", [] # Return empty lists to avoid issues # Handle JSON decoding issues

@app.route('/', methods=['GET', 'POST'])
def index():
    content = ""
    twitter_trends = []
    google_trends = []
    selected_country = "united_states"
    selected_model = "gemini-1.5-flash"
    error_message = None
    
    if request.method == 'POST':
        selected_country = request.form.get('country')
        selected_model = request.form.get('model', 'gemini-1.5-flash')
        
        try:
            data = collect_and_store_trends(selected_country)
            twitter_trends = data["twitter_trends"]
            google_trends = data["google_trends"]
        except Exception as e:
            error_message = f"Error: Could not retrieve trends for {selected_country}. {str(e)}"
    else:
        try:
            twitter_trends, google_trends, stored_country = get_latest_trends()
            selected_country = stored_country if stored_country else selected_country
        except Exception as e:
            error_message = f"Error: Could not load stored trends. {str(e)}"

    combined_trends = twitter_trends + google_trends

    if combined_trends:
        try:
            content = generate_newsletter_content(combined_trends[:5], selected_country, selected_model)
        except Exception as e:
            error_message = f"Error generating newsletter content: {str(e)}"
    else:
        error_message = "No trend data available. Please try another country or try again later."

    if error_message:
        flash(error_message, 'error')

    return render_template('index.html', content=content, twitter_trends=twitter_trends, google_trends=google_trends, 
                           selected_country=selected_country, COUNTRIES=COUNTRIES, 
                           selected_model=selected_model, GEMINI_MODELS=GEMINI_MODELS, error_message=error_message)

def generate_newsletter_content(trends, country_code, selected_model):
    if not trends:
        raise ValueError("No trends available to generate content")
    
    trend_names = ", ".join([trend["name"] for trend in trends])
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