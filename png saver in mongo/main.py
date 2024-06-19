import pymongo
from PIL import Image
from io import BytesIO

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017")
database_name = "FRIENDS"
table_name = "detls"
db = client[database_name]
collection = db[table_name]

def create_database():
    # Create a database and collection if not present
    if database_name not in client.list_database_names():
        db.create_collection(table_name)
        print(f"Database '{database_name}' and collection '{table_name}' created.")

def upload_photo():
    # Get user input for photo and name
    photo_path = input("Enter the path to the photo: ")
    name = input("Enter the name: ")

    try:
        # Open and read the image file
        with open(photo_path, "rb") as file:
            photo_data = file.read()

        # Insert data into the MongoDB collection
        result = collection.insert_one({"name": name, "photo": photo_data})
        print(f"Photo uploaded successfully with ID: {result.inserted_id}")
    except FileNotFoundError:
        print("Error: Photo file not found.")
    except Exception as e:
        print(f"Error uploading photo: {e}")

def display_photo():
    # Get user input for the name
    name = input("Enter the name to display: ")

    # Query MongoDB for the photo with the given name
    user_data = collection.find_one({"name": name})

    if user_data:
        # Display the photo
        image = Image.open(BytesIO(user_data["photo"]))
        image.show()
        print(f"Name: {user_data['name']}")
    else:
        print(f"No data found for name: {name}")

def main():
    create_database()

    while True:
        # Display menu options
        print("\nMenu:")
        print("1. Upload")
        print("2. Display")
        print("3. Exit")

        try:
            choice = int(input("Enter your choice (1/2/3): "))

            if choice == 1:
                upload_photo()
            elif choice == 2:
                display_photo()
            elif choice == 3:
                print("Exiting program.")
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
        except ValueError:
            print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    main()