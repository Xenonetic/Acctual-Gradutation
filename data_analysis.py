from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt

def perform_data_analysis():
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['Grad']
    collection = db['FormResponses']

    # Fetch all documents from the collection
    documents = collection.find()

    # Convert documents to a DataFrame
    data = pd.DataFrame(documents)

    # Ensure 'form_data' column exists and is not empty
    if 'form_data' in data.columns and data['form_data'].map(type).eq(dict).all():
        # Extract relevant information from the DataFrame
        question_counts = data['form_data'].apply(lambda x: len(x['questions']))

        # Plot a histogram of question counts
        plt.hist(question_counts, bins=range(min(question_counts), max(question_counts) + 1, 1), edgecolor='black')
        plt.xlabel('Number of Questions')
        plt.ylabel('Frequency')
        plt.title('Distribution of Questions in Forms')
        plt.savefig('static/question_distribution.png')  # Save the plot as an image
        plt.close()
    else:
        print("No data found for analysis or 'form_data' field is not a dictionary.")

    # Close the MongoDB client
    client.close()