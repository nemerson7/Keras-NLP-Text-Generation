
from WebScraper.WebScraperMain import Webscraper
from DataProcessing.Processing import DataProcessing
from AI.Model import ModelLSTM

if __name__ == '__main__':
    #IMDB Movie URL for input. Example URL:
    # https://www.imdb.com/title/tt0076759/?ref_=nv_sr_srsg_7
    url = input("Enter IMDB Url for the Movie: ")

    # Web Scraper initializer and output
    scraper = Webscraper(url)
    scraper.makeCall()
    data = scraper.getData()

    # Outputs size of data set that was imported into the model.
    print("Imported " + str(scraper.getReviewPages()) + " pages of user reviews with " + str(len(data["userReviews"])) + " reviews")

    # Data processor initializer and output
    # Cleans and formats data as plain string for model
    dataProcessor = DataProcessing(data)
    processedData = dataProcessor.getProcessedData()

    # AI model initializer
    model = ModelLSTM(processedData)
    epochs = int(input("Enter the number of epochs you would like to train for: "))
    model.train(epochs=epochs)

    # AI Output
    print("\n\n****** AI Model ******")
    print("\n\n****** Generated Review, Low Randomness ******")
    print(model.generate_review(randomness=0.25))
    print("\n\n****** Generated Review, Medium Randomness ******")
    print(model.generate_review())
    print("\n\n****** Generated Review, High Randomness ******")
    print(model.generate_review(randomness=0.6))
