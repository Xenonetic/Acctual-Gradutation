from pymongo import MongoClient

# MongoDB connection setup
mongo_connection_string = "mongodb://localhost:27017"
client = MongoClient(mongo_connection_string)
db = client.get_database("Sentiplus")  # Replace with your actual database name
users_collection = db.users

# Dummy user data
dummy_user = {
    "username": "test_user",
    "email": "test@example.com",
    "hashed_password": "hashed_password",  # You should replace this with the actual hashed password
}

# Insert dummy user into the collection
result = users_collection.insert_one(dummy_user)

print(f"Inserted user with ID: {result.inserted_id}")