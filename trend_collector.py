import os, json, tweepy, pytrends
from datetime import datetime
from dotenv import load_dotenv
from pytrends.request import TrendReq
# Load environment variables
load_dotenv()

# Twitter API credentials
consumer_key = os.getenv("TWITTER_API_KEY")
consumer_secret = os.getenv("TWITTER_API_SECRET")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# Authenticate with Twitter API
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


# Twitter API v2 credentials
bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

# Authenticate with Twitter API v2
client = tweepy.Client(bearer_token=bearer_token)

# Set up Google Trends client
pytrends = TrendReq(hl='en-US', tz=360)

COUNTRIES = [
    'afghanistan', 'albania', 'algeria', 'andorra', 'angola', 'antigua_and_barbuda', 'argentina', 'armenia', 'australia', 'austria', 
    'azerbaijan', 'bahamas', 'bahrain', 'bangladesh', 'barbados', 'belarus', 'belgium', 'belize', 'benin', 'bhutan', 
    'bolivia', 'bosnia_and_herzegovina', 'botswana', 'brazil', 'brunei', 'bulgaria', 'burkina_faso', 'burundi', 'cambodia', 'cameroon', 
    'canada', 'cape_verde', 'central_african_republic', 'chad', 'chile', 'china', 'colombia', 'comoros', 'congo', 'costa_rica', 
    'croatia', 'cuba', 'cyprus', 'czech_republic', 'denmark', 'djibouti', 'dominica', 'dominican_republic', 'east_timor', 'ecuador', 
    'egypt', 'el_salvador', 'equatorial_guinea', 'eritrea', 'estonia', 'ethiopia', 'fiji', 'finland', 'france', 'gabon', 
    'gambia', 'georgia', 'germany', 'ghana', 'greece', 'grenada', 'guatemala', 'guinea', 'guinea_bissau', 'guyana', 
    'haiti', 'honduras', 'hong_kong', 'hungary', 'iceland', 'india', 'indonesia', 'iran', 'iraq', 'ireland', 
    'israel', 'italy', 'ivory_coast', 'jamaica', 'japan', 'jordan', 'kazakhstan', 'kenya', 'kiribati', 'kuwait', 
    'kyrgyzstan', 'laos', 'latvia', 'lebanon', 'lesotho', 'liberia', 'libya', 'liechtenstein', 'lithuania', 'luxembourg', 
    'madagascar', 'malawi', 'malaysia', 'maldives', 'mali', 'malta', 'marshall_islands', 'mauritania', 'mauritius', 'mexico', 
    'micronesia', 'moldova', 'monaco', 'mongolia', 'montenegro', 'morocco', 'mozambique', 'myanmar', 'namibia', 'nauru', 
    'nepal', 'netherlands', 'new_zealand', 'nicaragua', 'niger', 'nigeria', 'north_korea', 'north_macedonia', 'norway', 'oman', 
    'pakistan', 'palau', 'palestine', 'panama', 'papua_new_guinea', 'paraguay', 'peru', 'philippines', 'poland', 'portugal', 
    'qatar', 'romania', 'russia', 'rwanda', 'saint_kitts_and_nevis', 'saint_lucia', 'saint_vincent_and_the_grenadines', 'samoa', 'san_marino', 'sao_tome_and_principe', 
    'saudi_arabia', 'senegal', 'serbia', 'seychelles', 'sierra_leone', 'singapore', 'slovakia', 'slovenia', 'solomon_islands', 'somalia', 
    'south_africa', 'south_korea', 'south_sudan', 'spain', 'sri_lanka', 'sudan', 'suriname', 'swaziland', 'sweden', 'switzerland', 
    'syria', 'taiwan', 'tajikistan', 'tanzania', 'thailand', 'togo', 'tonga', 'trinidad_and_tobago', 'tunisia', 'turkey', 
    'turkmenistan', 'tuvalu', 'uganda', 'ukraine', 'united_arab_emirates', 'united_kingdom', 'united_states', 'uruguay', 'uzbekistan', 'vanuatu', 
    'vatican_city', 'venezuela', 'vietnam', 'yemen', 'zambia', 'zimbabwe'
]

def get_twitter_trends():
    try:
        response = api.get_place_trends(1)
        trends = response.data[0]
        return [{"name": trend['name'], "tweet_volume": trend['tweet_volume']} for trend in trends]
    except Exception as e:
        print(f"Error getting Twitter trends: {e}")
        return []

def get_google_trends(country):
    try:
        if country not in COUNTRIES:
            country = 'united_states'
        trending_searches = pytrends.trending_searches(pn=country)
        return [{"name": trend, "search_volume": None} for trend in trending_searches.values.flatten()]
    except Exception as e:
        print(f"Error getting Google trends for {country}: {e}")
        return []

def collect_and_store_trends(country_code):
    twitter_trends = get_twitter_trends()
    google_trends = get_google_trends(country_code)
    
    if not twitter_trends and not google_trends:
        raise Exception("No trend data available for the selected country")
    
    data = {
        "timestamp": datetime.now().isoformat(),
        "country_code": country_code,
        "twitter_trends": twitter_trends,
        "google_trends": google_trends
    }
    
    with open("trends_data.json", "w") as f:
        json.dump(data, f, indent=2)
    
    print("Trends collected and stored successfully.")
    return data

if __name__ == "__main__":
    collect_and_store_trends('united_states')