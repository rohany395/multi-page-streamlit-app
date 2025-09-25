import streamlit as st
import openai
import requests
import json

# Set up the page
st.title("🌤️ Weather-Based Clothing Suggestion Bot")
st.write("Enter a city to get weather-appropriate clothing suggestions!")

# Initialize session state for API keys
if 'openai_api_key' not in st.session_state:
    st.session_state.openai_api_key = st.secrets["API_KEY"]
if 'weather_api_key' not in st.session_state:
    st.session_state.weather_api_key = st.secrets["OPEN_WEATEHER_API"]

def get_current_weather(location, api_key):
    """Get current weather for a given location"""
    if ',' in location:
        location = location.split(",")[0].strip()
    
    urlbase = "https://api.openweathermap.org/data/2.5/"
    urlweather = f"weather?q={location}&appid={api_key}"
    url = urlbase + urlweather
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Extract temperatures & Convert Kelvin to Celsius
        temp = data['main']['temp'] - 273.15
        feels_like = data['main']['feels_like'] - 273.15
        temp_min = data['main']['temp_min'] - 273.15
        temp_max = data['main']['temp_max'] - 273.15
        humidity = data['main']['humidity']
        weather_desc = data['weather'][0]['description']
        
        return {
            "location": location,
            "temperature": round(temp, 2),
            "feels_like": round(feels_like, 2),
            "temp_min": round(temp_min, 2),
            "temp_max": round(temp_max, 2),
            "humidity": round(humidity, 2),
            "description": weather_desc
        }
    except Exception as e:
        st.error(f"Error fetching weather data: {e}")
        return None

def weather_tool_function(location):
    """Tool function for OpenAI to call"""
    if not location:
        location = "Syracuse NY"
    
    weather_data = get_current_weather(location, st.session_state.weather_api_key)
    return json.dumps(weather_data) if weather_data else json.dumps({"error": "Could not fetch weather data"})

def get_clothing_suggestions(user_input):
    """Get clothing suggestions using OpenAI with weather tool"""
    if not st.session_state.openai_api_key or not st.session_state.weather_api_key:
        return "Please provide both OpenAI and OpenWeatherMap API keys in the sidebar."
    
    # Define the weather tool for OpenAI
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather for a specific location to provide clothing recommendations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city name, e.g. Syracuse NY. If no location is provided, use 'Syracuse NY' as default."
                        }
                    },
                    "required": ["location"]
                }
            }
        }
    ]
    
    try:
        # First call to OpenAI with the user input and tool
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a helpful assistant that provides clothing recommendations based on weather. When asked about clothing for a location, use the weather tool to get current conditions."
                },
                {
                    "role": "user", 
                    "content": f"What clothes should I wear in {user_input}? If no specific location is mentioned, use Syracuse NY."
                }
            ],
            tools=tools,
            tool_choice="auto"
        )
        
        message = response.choices[0].message
        
        # Check if the model wants to call the weather function
        if message.tool_calls:
            # Extract the location from the tool call
            tool_call = message.tool_calls[0]
            location = json.loads(tool_call.function.arguments).get("location", "Syracuse NY")
            
            # Get weather data
            weather_data = get_current_weather(location, st.session_state.weather_api_key)
            
            if weather_data:
                # Second call to OpenAI with weather information
                second_response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that provides specific clothing recommendations based on weather conditions. Be practical and specific in your suggestions."
                        },
                        {
                            "role": "user",
                            "content": f"""Based on the current weather in {weather_data['location']}:
                                - Temperature: {weather_data['temperature']}°C (feels like {weather_data['feels_like']}°C)
                                - Weather: {weather_data['description']}
                                - Humidity: {weather_data['humidity']}%
                                - Min/Max: {weather_data['temp_min']}°C / {weather_data['temp_max']}°C

                                Please provide specific clothing recommendations for today."""
                        }
                    ]
                )
                
                return second_response.choices[0].message.content
            else:
                return "Sorry, I couldn't get the weather information to provide clothing suggestions."
        else:
            return message.content
            
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Main interface
city_input = st.text_input("Enter a city name:", placeholder="e.g., New York, London, Tokyo")

if st.button("Get Clothing Suggestions", type="primary"):
    if city_input or st.session_state.openai_api_key:
        location = city_input if city_input.strip() else "Syracuse NY"
        
        with st.spinner("Getting weather information and clothing suggestions..."):
            suggestions = get_clothing_suggestions(location)
            
        st.success("Clothing Suggestions:")
        st.write(suggestions)
    else:
        st.warning("Please enter a city name and make sure API keys are configured.")