import requests
from flask import Flask, render_template, request
import datetime
import functools

app = Flask(__name__)

my_latitude = Your Latitude
my_longitude = Your Longitude
weather_api_key = "YOUR API"
weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={my_latitude}&lon=" \
              f"{my_longitude}&appid={weather_api_key}"


def get_date():
    current_date = datetime.datetime.now()
    formatted_date = current_date.strftime("%A, %d %B")
    return {
        "date": formatted_date
    }


def get_weather():
    response = requests.get(url=weather_url)
    data = response.json()
    weather_temp = int(data['main']['temp'])-273
    location_name = data['name']
    weather_description = data['weather'][0]['main']
    return {
        "temp": weather_temp,
        "location": location_name,
        "overall": weather_description,
        "lat": my_latitude,
        "long": my_longitude,
    }


def get_stock(stock_name):
    stock_key = "YOUR API"
    stock_url = "https://www.alphavantage.co/query"
    stock_parameters = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': stock_name,
        'apikey': stock_key,
    }
    stock_response = requests.get(url=stock_url, params=stock_parameters)
    stock_data = stock_response.json()

    stock_data_details = stock_data['Time Series (Daily)']
    stock_timestamp = list(stock_data_details.keys())[:2]
    stock_close_price_today = round(float(stock_data_details[stock_timestamp[0]]['4. close'])*83.15, 2)
    stock_close_price_yesterday = round(float(stock_data_details[stock_timestamp[1]]['4. close'])*83.15, 2)

    stock_price_change = round(float(((stock_close_price_today-stock_close_price_yesterday)
                                         /stock_close_price_yesterday)*100), 2)
    difference = round(float(stock_close_price_today-stock_close_price_yesterday), 2)
    if difference > 0:
        col = "#008561"
        arrow = "%▲"
    elif difference < 0:
        col = "#c1433d"
        arrow = "%▼"
    else:
        col = "black"
        arrow = ""
    return {
            "name": stock_name,
            "price": stock_close_price_today,
            "percentage": stock_price_change,
            "change": difference,
            "col": col,
            "arrow": arrow,
    }


@functools.lru_cache(maxsize=1)  # Cache the result for get_top_news
def get_top_news(num, country, category):
    NEWS_KEY = "YOUR API"
    news_url = "https://newsapi.org/v2/top-headlines?"
    news_parameters = {
        'apiKey': NEWS_KEY,
        'country': country,
        'category': category,
    }
    response = requests.get(url=news_url, params=news_parameters)
    data = response.json()
    news_list = []

    for i in range(num):
        news_source = data['articles'][i]['source']['name']
        news_title = data['articles'][i]['title']
        news_url = data['articles'][i]['url']
        news_img_url = data['articles'][i]['urlToImage']
        publishedAt = data['articles'][i]['publishedAt']
        date = datetime.datetime.strptime(publishedAt, "%Y-%m-%dT%H:%M:%SZ")
        current_time = datetime.datetime.utcnow()
        time_difference = current_time - date
        if time_difference.total_seconds() < 3600:
            minutes_ago = int(time_difference.total_seconds() / 60)
            uploadedIn = f"{minutes_ago} minutes ago"
        elif time_difference.total_seconds() < 86400:
            hours_ago = int(time_difference.total_seconds() / 3600)
            uploadedIn = f"{hours_ago} hours ago"
        else:
            days_ago = int(time_difference.total_seconds() / 86400)
            uploadedIn = f"{days_ago} days ago"
        news_item = {
            "news_source": news_source,
            "news_title": news_title,
            "news_url": news_url,
            "news_img_url": news_img_url,
            "uploadedIn": uploadedIn,
        }
        news_list.append(news_item)

    return news_list


@functools.lru_cache(maxsize=1)  # Cache the result for get_top_news
def get_keyword_news(num, keyword):
    NEWS_KEY = "YOUR API"
    news_url = "https://newsapi.org/v2/everything?"
    news_parameters = {
        'apiKey': NEWS_KEY,
        'q': keyword,
    }
    response = requests.get(url=news_url, params=news_parameters)
    data = response.json()
    print(data)
    news_list = []

    for i in range(num):
        news_source = data['articles'][i]['source']['name']
        news_title = data['articles'][i]['title']
        news_url = data['articles'][i]['url']
        news_img_url = data['articles'][i]['urlToImage']
        publishedAt = data['articles'][i]['publishedAt']
        date = datetime.datetime.strptime(publishedAt, "%Y-%m-%dT%H:%M:%SZ")
        current_time = datetime.datetime.utcnow()
        time_difference = current_time - date
        if time_difference.total_seconds() < 3600:
            minutes_ago = int(time_difference.total_seconds() / 60)
            uploadedIn = f"{minutes_ago} minutes ago"
        elif time_difference.total_seconds() < 86400:
            hours_ago = int(time_difference.total_seconds() / 3600)
            uploadedIn = f"{hours_ago} hours ago"
        else:
            days_ago = int(time_difference.total_seconds() / 86400)
            uploadedIn = f"{days_ago} days ago"
        news_item = {
            "news_source": news_source,
            "news_title": news_title,
            "news_url": news_url,
            "news_img_url": news_img_url,
            "uploadedIn": uploadedIn,
        }
        news_list.append(news_item)

    return news_list


@app.route("/")
def home():
    title = "Your briefing"
    currently = "local_label"
    date_data = get_date()
    weather_data = get_weather()

    if 'Rain' in weather_data['overall']:
        weather_icon = "rain.png"
    elif 'Cloud' in weather_data['overall'] or 'cloudy' in weather_data['description']:
        weather_icon = "cloud.png"
    elif 'Sun' in weather_data['overall'] or 'sun' in weather_data['description']:
        weather_icon = "sun.png"
    else:
        weather_icon = "default.png"

    stock_data = get_stock("TSLA")
    stock_data1 = get_stock("NVDA")
    stock_data2 = get_stock("AMZN")

    news_items = get_top_news(20, country='in', category='general')

    return render_template("index.html", weather_data=weather_data, date_data=date_data, weather_icon=weather_icon,
                           stock_data=stock_data, stock_data1=stock_data1, stock_data2=stock_data2,
                           news_items=news_items, title=title, currently=currently)


@app.route("/sports")
def sports():
    title = "Sports briefing"
    currently = "sports_label"
    date_data = get_date()
    weather_data = get_weather()

    if 'Rain' in weather_data['overall']:
        weather_icon = "rain.png"
    elif 'Cloud' in weather_data['overall'] or 'cloudy' in weather_data['description']:
        weather_icon = "cloud.png"
    elif 'Sun' in weather_data['overall'] or 'sun' in weather_data['description']:
        weather_icon = "sun.png"
    else:
        weather_icon = "default.png"

    stock_data = get_stock("TSLA")
    stock_data1 = get_stock("NVDA")
    stock_data2 = get_stock("AMZN")

    news_items = get_top_news(20, country='in', category='sports')

    return render_template("index.html", weather_data=weather_data, date_data=date_data, weather_icon=weather_icon,
                           stock_data=stock_data, stock_data1=stock_data1, stock_data2=stock_data2,
                           news_items=news_items, title=title, currently=currently)


@app.route("/entertainment")
def entertainment():
    title = "Entertainment briefing"
    currently = "entertainment_label"
    date_data = get_date()
    weather_data = get_weather()

    if 'Rain' in weather_data['overall']:
        weather_icon = "rain.png"
    elif 'Cloud' in weather_data['overall'] or 'cloudy' in weather_data['description']:
        weather_icon = "cloud.png"
    elif 'Sun' in weather_data['overall'] or 'sun' in weather_data['description']:
        weather_icon = "sun.png"
    else:
        weather_icon = "default.png"

    stock_data = get_stock("TSLA")
    stock_data1 = get_stock("NVDA")
    stock_data2 = get_stock("AMZN")

    news_items = get_top_news(20, country='in', category='entertainment')

    return render_template("index.html", weather_data=weather_data, date_data=date_data, weather_icon=weather_icon,
                           stock_data=stock_data, stock_data1=stock_data1, stock_data2=stock_data2,
                           news_items=news_items, title=title, currently=currently)


@app.route("/technology")
def technology():
    title = "Technology briefing"
    currently = "technology_label"
    date_data = get_date()
    weather_data = get_weather()

    if 'Rain' in weather_data['overall']:
        weather_icon = "rain.png"
    elif 'Cloud' in weather_data['overall'] or 'cloudy' in weather_data['description']:
        weather_icon = "cloud.png"
    elif 'Sun' in weather_data['overall'] or 'sun' in weather_data['description']:
        weather_icon = "sun.png"
    else:
        weather_icon = "default.png"

    stock_data = get_stock("TSLA")
    stock_data1 = get_stock("NVDA")
    stock_data2 = get_stock("AMZN")

    news_items = get_top_news(20, country='in', category='technology')

    return render_template("index.html", weather_data=weather_data, date_data=date_data, weather_icon=weather_icon,
                           stock_data=stock_data, stock_data1=stock_data1, stock_data2=stock_data2,
                           news_items=news_items, title=title, currently=currently)


@app.route("/business")
def business():
    title = "Business briefing"
    currently = "business_label"
    date_data = get_date()
    weather_data = get_weather()

    if 'Rain' in weather_data['overall']:
        weather_icon = "rain.png"
    elif 'Cloud' in weather_data['overall'] or 'cloudy' in weather_data['description']:
        weather_icon = "cloud.png"
    elif 'Sun' in weather_data['overall'] or 'sun' in weather_data['description']:
        weather_icon = "sun.png"
    else:
        weather_icon = "default.png"

    stock_data = get_stock("TSLA")
    stock_data1 = get_stock("NVDA")
    stock_data2 = get_stock("AMZN")

    news_items = get_top_news(20, country='in', category='business')

    return render_template("index.html", weather_data=weather_data, date_data=date_data, weather_icon=weather_icon,
                           stock_data=stock_data, stock_data1=stock_data1, stock_data2=stock_data2,
                           news_items=news_items, title=title, currently=currently)


@app.route("/science")
def science():
    title = "Science briefing"
    currently = "science_label"
    date_data = get_date()
    weather_data = get_weather()

    if 'Rain' in weather_data['overall']:
        weather_icon = "rain.png"
    elif 'Cloud' in weather_data['overall'] or 'cloudy' in weather_data['description']:
        weather_icon = "cloud.png"
    elif 'Sun' in weather_data['overall'] or 'sun' in weather_data['description']:
        weather_icon = "sun.png"
    else:
        weather_icon = "default.png"

    stock_data = get_stock("TSLA")
    stock_data1 = get_stock("NVDA")
    stock_data2 = get_stock("AMZN")

    news_items = get_top_news(20, country='in', category='science')

    return render_template("index.html", weather_data=weather_data, date_data=date_data, weather_icon=weather_icon,
                           stock_data=stock_data, stock_data1=stock_data1, stock_data2=stock_data2,
                           news_items=news_items, title=title, currently=currently)


@app.route("/health")
def health():
    title = "Health briefing"
    currently = "health_label"
    date_data = get_date()
    weather_data = get_weather()

    if 'Rain' in weather_data['overall']:
        weather_icon = "rain.png"
    elif 'Cloud' in weather_data['overall'] or 'cloudy' in weather_data['description']:
        weather_icon = "cloud.png"
    elif 'Sun' in weather_data['overall'] or 'sun' in weather_data['description']:
        weather_icon = "sun.png"
    else:
        weather_icon = "default.png"

    stock_data = get_stock("TSLA")
    stock_data1 = get_stock("NVDA")
    stock_data2 = get_stock("AMZN")

    news_items = get_top_news(20, country='in', category='health')

    return render_template("index.html", weather_data=weather_data, date_data=date_data, weather_icon=weather_icon,
                           stock_data=stock_data, stock_data1=stock_data1, stock_data2=stock_data2,
                           news_items=news_items, title=title, currently=currently)


@app.route("/process", methods=['POST'])
def process():
    input_keyword = request.form['user_input']
    title = input_keyword.capitalize()+" briefing"
    date_data = get_date()
    weather_data = get_weather()

    if 'Rain' in weather_data['overall']:
        weather_icon = "rain.png"
    elif 'Cloud' in weather_data['overall'] or 'cloudy' in weather_data['description']:
        weather_icon = "cloud.png"
    elif 'Sun' in weather_data['overall'] or 'sun' in weather_data['description']:
        weather_icon = "sun.png"
    else:
        weather_icon = "default.png"

    stock_data = get_stock("TSLA")
    stock_data1 = get_stock("NVDA")
    stock_data2 = get_stock("AMZN")

    news_items = get_keyword_news(20, keyword=input_keyword)
    input_keyword = ""

    return render_template("index.html", weather_data=weather_data, date_data=date_data, weather_icon=weather_icon,
                           stock_data=stock_data, stock_data1=stock_data1, stock_data2=stock_data2,
                           news_items=news_items, input_keyword=input_keyword, title=title)


if __name__ == "__main__":
    app.run(debug=True)
