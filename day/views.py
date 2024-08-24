from django.http import JsonResponse
from django.shortcuts import render
import wikipediaapi
import pyttsx3
import speech_recognition as sr
import webbrowser
from pytube import Search
import requests

# Initialize the recognizer and text-to-speech engine
recognizer = sr.Recognizer()

# Initialize Wikipedia API with a user agent
wiki_wiki = wikipediaapi.Wikipedia(
    language='en', 
    user_agent="day/1.0 (indraprakashsrivastav@gmail.com)"
)

# Function to convert text to speech
def speak(text):
    tts_engine = pyttsx3.init()  # Reinitialize the TTS engine
    tts_engine.say(text)
    tts_engine.runAndWait()
    tts_engine.stop()  # Stop the TTS engine after speaking
    return text

# Function to search Wikipedia
def search_wikipedia(query):
    page = wiki_wiki.page(query)
    if page.exists():
        # Return only the first paragraph for brevity
        summary = page.summary.split('\n')[0]
        return summary if summary else "No summary available."
    else:
        return "I couldn't find information on that topic. Please check the spelling or try a different query."

# Function to listen to voice commands
def listen():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command
        except sr.UnknownValueError:
            speak("Sorry, I did not understand that.")
            return None
        except sr.RequestError:
            speak("Sorry, there seems to be an issue with the service.")
            return None

# Function to search and play a video on YouTube
def play_on_youtube(query):
    search = Search(query)
    first_result = search.results[0]  # Get the first video from search results
    video_url = first_result.watch_url
    webbrowser.open(video_url)  # Open the video in the web browser
    return f"Playing {first_result.title} on YouTube."

# Function to get weather information
def get_weather(city_name):
    api_key = "9fcaa61a674bd3b78d86a43a77c545b6"  # Replace with your OpenWeatherMap API key
    base_url = "https://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "q=" + city_name + "&appid=" + api_key + "&units=metric"
    response = requests.get(complete_url)
    data = response.json()

    # Print response data for debugging
    print(data)

    # Check if the response contains the 'main' key
    if "main" in data:
        main = data["main"]
        weather = data["weather"][0]
        temp = main["temp"]
        description = weather["description"]
        weather_report = f"The temperature in {city_name} is {temp}°C with {description}."
    elif "message" in data:
        # Handle error messages from the API
        weather_report = data["message"]
    else:
        weather_report = "City not found or error occurred."

    return weather_report

def main(request):
    response_text = None  # Initialize response_text

    if request.method == 'POST':
        command = request.POST.get('voice_command')
        if command:
            print(f"Received command: {command}")  # Print in Django console for debugging
            command = command.lower()
            if "hello vajra" in command:
                response_text = speak("Hi sir! How can I assist you?")
            elif "your name" in command:
                response_text = speak("My name is Vajra.")
            elif "meaning of vajra" in command:
                response_text = speak(search_wikipedia("Vajra"))
            elif "what is" in command:
                query = command.replace("what is", "").strip()
                response_text = speak(search_wikipedia(query))
            elif "who is" in command:
                query = command.replace("who is", "").strip()
                response_text = speak(search_wikipedia(query))
            elif "play" in command:
                query = command.replace("play", "").strip()
                response_text = speak(play_on_youtube(query))
            elif "weather" in command:
                city_name = command.replace("weather in", "").strip()
                response_text = speak(get_weather(city_name))
            else:
                response_text = speak(search_wikipedia(command))
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'response_text': response_text})
    
    return render(request, 'main.html', {'response_text': response_text})

def index(request):
    return render(request, 'main.html')
