import json
import requests
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from googleapiclient.discovery import build
from dotenv import dotenv_values

config = dotenv_values(".env")

API_KEY = config['GOOGLE_KEY']
SEARCH_ENGINE_ID = config['SEARCH_ENGINE_ID']
CACHE_FILENAME = "images_cache.json"
CACHE_DICT = {}

def open_cache():
    try:
        with open(CACHE_FILENAME, 'r') as cache_file:
            cache_contents = cache_file.read()
            cache_dict = json.loads(cache_contents)
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    dumped_json_cache = json.dumps(cache_dict)
    with open(CACHE_FILENAME, 'w') as cache_file:
        cache_file.write(dumped_json_cache)

def make_request(param):
    resource = build("customsearch", 'v1', developerKey=API_KEY).cse()
    print(param)
    # https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list?hl=pt-br
    result = resource.list(q=param, cx=SEARCH_ENGINE_ID, searchType='image', gl='br', lr="lang_pt").execute() # imgSize= 'HUGE'
    return result

def make_request_with_cache(param={}):
    key_to_find = param
    if key_to_find in CACHE_DICT:
        print('using cache')
        return CACHE_DICT[key_to_find]
    else: 
        print('feching')
        search_return = make_request(param)
        CACHE_DICT[key_to_find] = search_return
        save_cache(CACHE_DICT)
        return CACHE_DICT[key_to_find]


if __name__ == "__main__":
    CACHE_DICT = open_cache()
    while True:

        first_input = input('Enter a search term (e.g. Michigan, michigan) or "exit": ').lower()
        # first access, print national sites
        if first_input == 'exit':
            break
        else:
            search_results = make_request_with_cache(first_input)
            count = 0
            for item in search_results['items']:
                count += 1
                info = f"[{count}] {item['title']} {item['link']} {item['image']['height']}*{item['image']['width']}"
                print(info)
            # second access, print selected picture
            while True:
                second_input = input('Choose a number for showing picture or "exit" or "back": ')
                if second_input.isnumeric() and int(second_input) < 11 and int(second_input) > 0:
                    response = requests.get(search_results['items'][int(second_input)-1]['link'])
                    # print(type(response.content))
                    try:
                        img = Image.open(BytesIO(response.content))
                        img.show()
                    except UnidentifiedImageError:
                        second_input = int(second_input) + 1
                        response = requests.get(search_results['items'][int(second_input)-1]['link'])
                        img = Image.open(BytesIO(response.content))
                        img.show()
                elif second_input == 'back':
                    break
                elif second_input == 'exit':
                    exit()
                else: 
                    print('Invalid input')