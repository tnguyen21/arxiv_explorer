from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd

# Sample profile data
DATA = {
    "id": [1, 2, 3],
    "name": ["Alex", "Jordan", "Taylor"],
    "age": [25, 30, 28],
    "bio": ["Loves hiking and outdoor activities.", "Enjoys reading and yoga.", "Passionate about technology and innovation."],
    "likes": [0, 0, 0]  # To keep track of likes
}
df = pd.DataFrame(DATA)

def profiles(request):
    # Convert DataFrame to HTML table; simple for demo purposes
    profiles_html = df.to_html()
    return HttpResponse(f"<html><body>{profiles_html}<br><a href='/like/'>Like the first profile</a></body></html>")

def like_profile(request):
    # Increment likes for the first profile as an example
    df.at[0, 'likes'] += 1
    return HttpResponse("Liked! <a href='/'>Back to profiles</a>")
