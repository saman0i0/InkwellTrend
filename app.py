# app.py 
import os, json, markdown
from flask import Flask, render_template, request, flash
import google.generativeai as genai
from trend_collector import collect_and_store_trends, COUNTRIES

# Initialize Flask app
app = Flask(__name__, static_folder='static')
app.secret_key = os.urandom(24) # Necessary for flash messages

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# List of available Gemini models
GEMINI_MODELS = [
    'gemini-pro',
    'gemini-1.5-flash',
]

# Function to retrieve the latest trends from a JSON file
def get_latest_trends():
    try:
        with open("trends_data.json", "r") as f:
            data = json.load(f)
        return data["google_trends"], data["reddit_trends"], data.get("country_code", "united_states")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        flash(f"Error: Unable to retrieve trends data. ({e})", 'error')
        return [], [], "united_states" 

# Route for the index page
@app.route('/', methods=['GET', 'POST'])
def index():
    content = "" 
    google_trends = []
    reddit_trends = []
    selected_country = "united_states"
    selected_model = "gemini-1.5-flash"
    error_message = None
    num_trends = 5

    # Handle form submission
    if request.method == 'POST':
        selected_country = request.form.get('country')
        selected_model = request.form.get('model', 'gemini-1.5-flash')
        tone = request.form.get('tone', 'Informative')  
        keywords = request.form.get('keywords') 
        num_trends = int(request.form.get('num_trends', 5))  # Get num_trends from form
        
        try:
            data = collect_and_store_trends(selected_country) 
            google_trends = data["google_trends"]
            reddit_trends = data["reddit_trends"]

            # Combine all trends
            combined_trends = (
                [{"name": t["name"], "source": "Google", "relevance": t.get("search_volume", 0) or 0} for t in google_trends] +
                [{"name": t["name"], "source": "Reddit", "relevance": t["score"] * 0.7 + t["num_comments"] * 0.3, 
                    "subreddit": t["subreddit"], "url": t["url"]} for t in reddit_trends]
            )
            
            # Apply source filtering after combining trends
            source = request.form.get('source', None)
            if source == 'google':
                combined_trends = [t for t in combined_trends if t['source'] == 'Google']
            elif source == 'reddit': 
                combined_trends = [t for t in combined_trends if t['source'] == 'Reddit']
            
             # Sort trends by relevance and limit to the number requested
            top_trends = sorted(combined_trends, key=lambda x: x['relevance'], reverse=True)[:num_trends]

            if top_trends:
                try:
                    content = generate_newsletter_content(top_trends, selected_country, selected_model, tone, keywords)
                except Exception as e:
                    error_message = f"Error generating newsletter content: {str(e)}"
            else:
                error_message = "No trends available to generate content. Please try another country or try again later."
        
        except Exception as e:
            error_message = f"Error: Could not retrieve trends for {selected_country}. {str(e)}"

    if error_message:
        flash(error_message, 'error')

    # Render the index template with collected data
    return render_template('index.html', content=content, google_trends=google_trends, 
                           reddit_trends=reddit_trends, selected_country=selected_country, COUNTRIES=COUNTRIES, num_trends=num_trends,
                           selected_model=selected_model, GEMINI_MODELS=GEMINI_MODELS, error_message=error_message)

# Function to generate newsletter content based on trends
def generate_newsletter_content(trends, country_code, selected_model, keywords="", tone="Informative", num_trends=5):
    trend_details = []
    for i in range(num_trends):  # Iterate using num_trends
        try:
            trend = trends[i]
            detail = f"{trend['name']} (Source: {trend['source']})"
            if trend['source'] == 'Reddit':
                detail += f" - From r/{trend['subreddit']} - {trend['url']}"
            trend_details.append(detail)
        except IndexError:
            break 
    
    trend_info = "\n".join(trend_details)
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

    prompt = f"""Generate a newsletter section about these trends: {trend_info}.
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
        
    print(f"Generating content for trends in {country_code}: {trend_info}")
    response = model.generate_content(prompt)
        
    # Convert Markdown to HTML
    html_content = markdown.markdown(response.text)
    return html_content

if __name__ == '__main__':
    app.run(debug=True)