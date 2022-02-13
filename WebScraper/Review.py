import math

class UserReview:

    def __init__(self, itemContent):
        self.itemContent = itemContent

    def getRating(self):
        try:
            return self.itemContent.find("span", {"class": "rating-other-user-rating"}).getText().replace("\n","")
        except:
            return "NA"

    def getTitle(self):
        try:
            return self.itemContent.find("a", {"class": "title"}).getText().replace("\n","")
        except:
            return "NA"

    def getAuthor(self):
        try:
            return self.itemContent.find("span", {"class": "display-name-link"}).getText()
        except:
            return "NA"

    def getDate(self):
        try:
            return self.itemContent.find("span", {"class": "review-date"}).getText()
        except:
            return "NA"

    def getHelpful(self):
        try:
            text = self.itemContent.find("div", {"class": "actions text-muted"}).getText()
            text = text.replace("\n","").replace("  ","").split(" found this helpful")
            return text[0]
        except:
            return "NA"

    def getMessage(self):
        try:
            return self.itemContent.find("div", {"class": "text"}).getText()
        except:
            return "NA"

    def getRelevance(self):
        try:
            text = self.getHelpful()
            split = text.split(' out of ')
            probRev = round(int(split[0]) / int(split[1]), 1)
            if probRev >= 0.5:
                return math.ceil((probRev - 0.49) * 10)
            else:
                return 0
        except:
            return 0

class CriticReview:

    def __init__(self, details):
        self.details = details

    def getScore(self):
        try:
            return self.details.find("div", {"class": "critscore"}).getText().replace("\n","")
        except:
            return "NA"

    def getPublisher(self):
        try:
            text = self.details.find("b", {"itemprop": "publisher"}).getText()
            return text
        except:
            return "NA"

    def getAuthor(self):
        try:
            text = self.details.find("span", {"itemprop": "author"}).getText()
            return text
        except:
            return "NA"

    def getSummary(self):
        try:
            return self.details.find("div", {"class": "summary"}).getText()
        except:
            return "NA"