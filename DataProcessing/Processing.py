from WebScraper.Review import UserReview, CriticReview
import random, re

#Things needed:
""" 1. Filtering out special characters (if there are any)
2. Relevance factoring: 
   - Reviews receive relevance ranking i.e. "11 out of 19 people found this helpful"
   - So the probability of relevance is about 0.578   
   - Could round up to the nearest 10th, subtract 0.5 and multiply by 10
   - So in the case of 11/19 ~= 0.578 ~= 0.6, 0.6 - 0.5 = 0.1, 0.1 * 10 = 1
   - And take this final number and append the review to the review list that many times
   - Then shuffle the review list to make sure that there aren't the same reviews side by side
3. Join the review list on spaces and return it as string
"""

class DataProcessing:
    userReviewList=[]
    crictReviewList=[]
    
    def __init__(self, data):
        self.data = data
        self.movieDetails = data
        self.criticRvw = data["criticReviews"]
        self.userRevw = data["userReviews"]    

        self.processedData = ""

        self.cleanReviews()
       
    def cleanReviews(self):

        proCriticRev = []
        proUserRev = []
        proMovieDetails = []

        # Appends User Reviews to user review list
        for i in self.userRevw:
            text = ""
            if i.getTitle() != 'NA':
                text = i.getTitle()
            if i.getMessage() != 'NA':
                text += " " + i.getMessage()
            proText = re.sub("[^a-zA-Z0-9.,!?\"']+", ' ', text)

            # Calculates helpfulness and copies for required number of times out of 10.
            if i.getHelpful() != 'NA':
                weight = i.getRelevance()

                for x in range(int(weight)):
                    proUserRev.append(proText)

        # Appends Critic Reviews to critic review list
        for i in self.criticRvw:
            text = ""
            if i.getSummary() != 'NA':
                text = i.getSummary()
            proText = re.sub("[^a-zA-Z0-9.,!?\"']+", ' ', text)
            for x in range(int(len(proUserRev)/len(self.criticRvw))):
                proCriticRev.append(proText)
        
        allProData = proCriticRev + proUserRev

        print("Critic Reviews Initial: " + str(len(self.criticRvw)) + " --> Adjusted: " + str(len(proCriticRev)))
        print("User Reviews Initial: " + str(len(self.userRevw)) + " --> Adjusted: " + str(len(proUserRev)))

        # Appends title, plot, and actors with 20% weight.
        for x in range(int(len(allProData)/15)):
            proMovieDetails.append(self.data['title'])
            proMovieDetails.append(self.data['plot'])
            proMovieDetails.append(self.data['actors'])

        # Combines shuffles and saves all lists as a string.
        allProData = allProData + proMovieDetails
        random.shuffle(allProData)
        print("Total data set includes " + str(len(allProData)) + " data points.")
        self.processedData = " ".join(allProData)

    # Getter for processedData String
    def getProcessedData(self):    
        return self.processedData