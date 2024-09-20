# Import necessary libraries
import os, json, pytrends
from datetime import datetime
from dotenv import load_dotenv
from pytrends.request import TrendReq
from tenacity import retry, stop_after_attempt, wait_fixed
import praw

# Load environment variables from a .env file (contains API keys)
load_dotenv()

# Set up Reddit API client using credentials from the environment variables
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

# Set up Google Trends client
# `hl` sets the language (en-US for English), and `tz` is the timezone (360 for UTC+6)
pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25))

# List of country codes for Google Trends data (in snake_case format)
COUNTRIES = [
    'argentina', 'australia', 'austria', 'bangladesh', 'belgium', 'brazil', 'canada', 'chile', 'china', 'colombia',
    'czech_republic', 'denmark', 'egypt', 'ethiopia', 'finland', 'france', 'germany', 'ghana', 'greece', 'hungary',
    'india', 'indonesia', 'iran', 'iraq', 'ireland', 'israel', 'italy', 'ivory_coast', 'jamaica', 'japan',
    'kazakhstan', 'kenya', 'malaysia', 'mexico', 'morocco', 'myanmar', 'nepal', 'netherlands', 'new_zealand', 'nigeria',
    'norway', 'pakistan', 'panama', 'peru', 'philippines', 'poland', 'portugal', 'qatar', 'romania', 'russia',
    'saudi_arabia', 'senegal', 'serbia', 'singapore', 'south_africa', 'south_korea', 'spain', 'sri_lanka', 'sudan', 'sweden',
    'switzerland', 'taiwan', 'tanzania', 'thailand', 'tunisia', 'turkey', 'uganda', 'ukraine', 'united_arab_emirates', 'united_kingdom',
    'united_states', 'uruguay', 'uzbekistan', 'venezuela', 'vietnam', 'zambia', 'zimbabwe'
]


# Function to fetch Google Trends data for a given country
# This function retries up to 3 times in case of failure
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def get_google_trends(country):
    try:
        # Check if the country is in the allowed list, otherwise default to the US
        if country not in COUNTRIES:
            country = 'united_states'
        
        # Fetch trending searches for the given country
        trending_searches = pytrends.trending_searches(pn=country)
        
        # Convert trends into a list of dictionaries with trend names (and no search volume data)
        return [{"name": trend, "search_volume": None} for trend in trending_searches.values.flatten()]
    
    # Handle errors gracefully and return an empty list
    except Exception as e:
        print(f"Error getting Google trends for {country}: {e}")
        return []

# Function to fetch trending posts from Reddit's r/all subreddit
def get_reddit_trends():
    try:
        # Get the top 50 hot posts from r/all
        popular_posts = reddit.subreddit("all").hot(limit=50)  # Increased limit for better selection
        
        trends = []
        
        # Loop through the posts and filter based on engagement (score and number of comments)
        for post in popular_posts:
            if post.score < 1000 or post.num_comments < 50:
                continue
            
            # Extract relevant details from each post (e.g., title, score, subreddit, etc.)
            trend = {
                "name": post.title[:100],  # Limit the title length to 100 characters
                "type": "post",
                "score": post.score,
                "subreddit": post.subreddit.display_name,
                "num_comments": post.num_comments,
                "url": post.url,
                "is_video": post.is_video,
                "over_18": post.over_18,  # NSFW indicator
                "created_utc": post.created_utc  # When the post was created
            }
            
            # Add post flair if available
            if hasattr(post, 'link_flair_text') and post.link_flair_text:
                trend["flair"] = post.link_flair_text
            
            # Add post content if available, but limit to 500 characters
            if post.selftext:
                trend["content"] = post.selftext[:500]
            
            # Append the post to the trends list
            trends.append(trend)
        
        # Sort trends by a combination of score (70% weight) and number of comments (30% weight)
        trends = sorted(trends, key=lambda x: (x['score'] * 0.7 + x['num_comments'] * 0.3), reverse=True)
        
        # Return the top 10 trending posts
        return trends[:10]
    
    # Handle errors gracefully and return an empty list
    except Exception as e:
        print(f"Error getting Reddit trends: {e}")
        return []

# Main function to collect trends from both Google and Reddit, and store the data
def collect_and_store_trends(country_code):
    # Fetch Google and Reddit trends
    google_trends = get_google_trends(country_code)
    reddit_trends = get_reddit_trends()
    
    # If no trends are found, raise an exception
    if not google_trends and not reddit_trends:
        raise Exception("No trend data available for the selected country")
    
    # Combine the trends into a single dictionary with a timestamp
    data = {
        "timestamp": datetime.now().isoformat(),
        "country_code": country_code,
        "google_trends": google_trends,
        "reddit_trends": reddit_trends
    }
    
    # Save the trends to a JSON file
    with open("trends_data.json", "w") as f:
        json.dump(data, f, indent=2)
    
    # Print a success message
    print("Trends collected and stored successfully.")
    
    # Return the collected data
    return data

if __name__ == "__main__":
    collect_and_store_trends('united_states')
