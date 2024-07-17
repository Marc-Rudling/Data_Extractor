import requests
import pandas as pd
import time
import warnings

# Replace with your actual Google Places API key
API_KEY = 'AIzaSyBjhf7w7_vUGBAAiWxbwwXPSn99NaAAYEk'

def get_car_wash_data(suburb):
    car_washes = []
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query=car+wash+in+{suburb}&key={API_KEY}"
    
    while url:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Request failed with status code {response.status_code}")
            break
        
        data = response.json()
        if 'error_message' in data:
            print(f"API error: {data['error_message']}")
            break
        
        results = data.get('results', [])
        for place in results:
            place_id = place['place_id']
            details = get_place_details(place_id)
            car_wash = {
                'Business Name': place.get('name'),
                'Address': place.get('formatted_address'),
                'Contact Number': details.get('formatted_phone_number', 'None'),
                'Email Address': 'None',  # Google Places API does not provide email addresses
                'Website': details.get('website', 'None'),
                'Social Media Page': get_social_media(details)
            }
            car_washes.append(car_wash)

        next_page_token = data.get('next_page_token')
        if next_page_token:
            url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?pagetoken={next_page_token}&key={API_KEY}"
            time.sleep(2)  # Wait a bit to avoid hitting rate limits
        else:
            url = None
    
    return car_washes

def get_place_details(place_id):
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Request for place details failed with status code {response.status_code}")
        return {}
    
    details = response.json()
    if 'error_message' in details:
        print(f"API error on details request: {details['error_message']}")
        return {}
    
    return details.get('result', {})

def get_social_media(details):
    social_media_pages = []
    for item in details.get('urls', []):
        if 'facebook.com' in item or 'instagram.com' in item or 'twitter.com' in item:
            social_media_pages.append(item)
    return ', '.join(social_media_pages) if social_media_pages else 'None'

def save_to_excel(data, suburb):
    df = pd.DataFrame(data)
    filename = f"car_wash_data_{suburb.replace(' ', '_')}.xlsx"
    df.to_excel(filename, index=False)
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    suburb = input("Enter the suburb: ")
    data = get_car_wash_data(suburb)
    save_to_excel(data, suburb)
