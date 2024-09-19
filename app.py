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
        return data["twitter_trends"], data["google_trends"], data["reddit_trends"], data.get("country_code", "united_states"), data.get("errors", [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        flash(f"Error: Unable to retrieve trends data. ({e})", 'error')
        return [], [], [], "united_states", [] # Return empty lists to avoid issues # Handle JSON decoding issues

@app.route('/', methods=['GET', 'POST'])
def index():
    content = ""
    twitter_trends = []
    google_trends = []
    reddit_trends = []
    selected_country = "united_states"
    selected_model = "gemini-1.5-flash"
    error_message = None
    
    if request.method == 'POST':
        selected_country = request.form.get('country')
        selected_model = request.form.get('model', 'gemini-1.5-flash')
        keywords = request.form.get('keywords') 
        tone = request.form.get('tone', 'Informative') 
        
        try:
            data = collect_and_store_trends(selected_country)
            twitter_trends = data["twitter_trends"]
            google_trends = data["google_trends"]
            reddit_trends = data["reddit_trends"]
        
            # Combine all trends and select top 5 based on volume/score
            combined_trends = (
                sorted(twitter_trends, key=lambda x: x.get('tweet_volume', 0) or 0, reverse=True) +
                sorted(google_trends, key=lambda x: x.get('search_volume', 0) or 0, reverse=True) +
                sorted(reddit_trends, key=lambda x: x.get('score', 0) or 0, reverse=True)
            )
            top_trends = combined_trends[:5]

            if top_trends:
                try:
                    content = generate_newsletter_content(top_trends[:5], selected_country, selected_model, tone, keywords)
                except Exception as e:
                    error_message = f"Error generating newsletter content: {str(e)}"
            else:
                error_message = "No trends available to generate content. Please try another country or try again later."
        
        except Exception as e:
            error_message = f"Error: Could not retrieve trends for {selected_country}. {str(e)}"

    if error_message:
        flash(error_message, 'error')

    return render_template('index.html', content=content, twitter_trends=twitter_trends, google_trends=google_trends, 
                           reddit_trends=reddit_trends, selected_country=selected_country, COUNTRIES=COUNTRIES, 
                           selected_model=selected_model, GEMINI_MODELS=GEMINI_MODELS, error_message=error_message)

def generate_newsletter_content(trends, country_code, selected_model, keywords="", tone="Informative"):
    trend_names = ", ".join([trend["name"] for trend in trends])
    model = genai.GenerativeModel(selected_model)

    # Tone Instruction Mapping: 
    tone_instructions = {
        "Informative": "Provide a neutral and informative tone suitable for a general audience.",
        "Humorous": "Incorporate humor and a lighthearted tone in the writing.",
        "Formal": "Use a professional and formal tone suitable for a news report.",
        "Casual": "Write with a casual, conversational, and friendly tone, as if talking to a friend."
    } 
    # Get the tone instruction or default to "Informative"
    tone_instruction = tone_instructions.get(tone, tone_instructions["Informative"])

    prompt = f"""Generate a newsletter section about these trends: {trend_names}.
        Consider these keywords: {keywords}.
        {tone_instruction}
        - Main Headline: 
          [Create a catchy main headline that creatively combines the top three trends. Keep it under 100 words.]
        - Trend Sections:
          For each trend, provide: 
            Trend Headline:
            [Write a catchy and creative headline about the trend, without explicitly using the trend's name. Keep it brief.] 
            Overview:
            [Provide a detailed overview of the trend, highlighting its significance, impact, and any recent events, in about 200-350 words.]
        Please ensure each trend is clearly separated with its own headline and overview.
        Do not include following on the output 
        - Use of word trend headline, overview.
        - Any additional subheadings or sections beyond what is specified above.
        """ 

    for i, trend in enumerate(trends): 
        prompt += f"\n\nTrend {i+1}: {trend['name']}\n"  
        
    print(f"Generating content for trends in {country_code}: {trend_names}")
    response = model.generate_content(prompt)
        
    # Convert Markdown to HTML
    html_content = markdown.markdown(response.text)
    return html_content

if __name__ == '__main__':
    app.run(debug=True)