import requests, time
from bs4 import BeautifulSoup
from selenium import webdriver
from sys import platform
from WebScraper.Review import UserReview, CriticReview

class Webscraper:

    # 100 Calls per day limit from www.imdb-api.com
    API_KEY = "k_67xixrkv"
    LANGUAGE = "en"

    def __init__(self, url):
        self.url = url
        self.movieId = self.processUrl()

        self.reviewPagesProcessed = None
        self.imdbData = {}

    # Makes GET request to imdb-api.com and saves output as JSON.
    def makeCall(self):
        callUrl = "https://imdb-api.com/" + self.LANGUAGE + "/API/Title/" + self.API_KEY + "/" + self.movieId
        response = requests.get(callUrl)
        data = response.json()
    
        # Saves API answer to list
        self.processCall(data)
        # Starts selenium to get user reviews.
        self.seleniumScrape()

    # Starts selenium browser for required operating system.
    # Then navigates to user reviews loads all of them.
    def seleniumScrape(self):
        try:
            if platform == "linux":
                options = webdriver.FirefoxOptions()
                options.add_argument("--no-sandbox")
                options.add_argument("--headless")
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1080")
                driver = webdriver.Firefox(options=options, executable_path='WebScraper/driver/geckodriver')
            elif platform == "win32":
                driver = webdriver.Chrome(executable_path='WebScraper/driver/chromedriver')
            elif platform == "darwin":
                driver = webdriver.Chrome(executable_path='WebScraper/driver/macdriver')
        except OSError:
            print("Unsupported system. Currently supporting: Windows and Linux")  

        driver.get("https://www.imdb.com/title/" + self.movieId + "/reviews/")
        
        cnt = 0
        time.sleep(5)
        end = False
        print("Beginning Review Scrape")

        while not end:
            try:
                element = driver.find_element_by_id("load-more-trigger")
                element.click()
                cnt += 1
            except:
                end = True
            time.sleep(1.5)

        self.reviewPagesProcessed = cnt+1
        time.sleep(1)

        html = driver.page_source

        driver.quit()

        # Sends full HTML of selenium browser to reviewScrape.
        self.reviewScrape(html)

    def getReviewPages(self):
        return self.reviewPagesProcessed

    def reviewScrape(self, html):
        print("Saving Movie Reviews")
        userReviews = []

        # Starts BeautifulSoup to parse review.
        reviewSoup = BeautifulSoup(html, 'html.parser')

        # Appends each user review to a list as UserReview class object.
        reviewList = reviewSoup.find_all("div", {"class": "lister-item-content"})
        for itemContent in reviewList:
            userReviews.append(UserReview(itemContent))

        self.imdbData["userReviews"] = userReviews

        # Appends critic review to list as CriticReview class object.
        criticReviews = []
        criticUrl = "https://www.imdb.com/title/" + self.movieId + "/criticreviews"
        criticResponse = requests.get(criticUrl)
        criticSoup = BeautifulSoup(criticResponse.text, 'html.parser')
        criticList = criticSoup.find_all("tr", {"class": "even detailed"})
        for details in criticList:
            criticReviews.append(CriticReview(details))

        self.imdbData["criticReviews"] = criticReviews

    # Saves data from API call to imdbData dictionary.
    def processCall(self, data):
        self.imdbData["title"] = data["title"]
        self.imdbData["fullTitle"] = data["fullTitle"]
        self.imdbData["movieId"] = self.movieId
        self.imdbData["plot"] = data["plot"]
        self.imdbData["actors"] = data["stars"]
        self.imdbData["overallRating"] = data["imDbRating"]
        self.imdbData["ratingCount"] = data["imDbRatingVotes"]
        self.imdbData["criticRating"] = data["metacriticRating"]
        
    # Getter for imdbData
    def getData(self):
        return self.imdbData

    # Retrieves movieID from URL
    def processUrl(self):
        headlessUrl = self.url[26:]
        chunkedUrl = headlessUrl.split("/")
        if (chunkedUrl[0] != ''):
            return chunkedUrl[0]
        else:
            return chunkedUrl[1]