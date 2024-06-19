from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

# Function to generate random dates
def random_date(start, end):
    return start + timedelta(
        seconds=random.randint(0, int((end - start).total_seconds()))
    )

# Generate insert commands for Users table
users_insert_commands = []
for i in range(13, 25):
    username = fake.user_name()
    email = fake.email()
    join_date = random_date(datetime(2020, 1, 1), datetime(2024, 3, 1)).strftime(
        "%Y-%m-%d"
    )
    users_insert_commands.append(
        f"INSERT INTO Users (UserID, UserName, Email, JoinDate) VALUES ({i}, '{username}', '{email}', '{join_date}');"
    )

# Generate insert commands for Posts table
posts_insert_commands = []
for i in range(31, 90):
    user_id = random.randint(15, 25)
    content = fake.sentence()
    post_date = random_date(datetime(2024, 1, 1), datetime(2024, 3, 1)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    posts_insert_commands.append(
        f"INSERT INTO Posts (PostID, UserID, Content, PostDate) VALUES ({i}, {user_id}, '{content}', '{post_date}');"
    )

# Generate insert commands for Likes table
likes_insert_commands = []
for i in range(101, 500):
    user_id = random.randint(1, 25)
    post_id = random.randint(1, 90)
    like_date = random_date(datetime(2024, 1, 1), datetime(2024, 3, 1)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    likes_insert_commands.append(
        f"INSERT INTO Likes (LikeID, UserID, PostID, LikeDate) VALUES ({i}, {user_id}, {post_id}, '{like_date}');"
    )

# Generate insert commands for Comments table
comments_insert_commands = []
for i in range(601, 1000):
    user_id = random.randint(1, 25)
    post_id = random.randint(1, 90)
    comment = fake.text()
    comment_date = random_date(datetime(2024, 1, 1), datetime(2024, 3, 1)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    comments_insert_commands.append(
        f"INSERT INTO Comments (CommentID, UserID, PostID, Comment, CommentDate) VALUES ({i}, {user_id}, {post_id}, '{comment}', '{comment_date}');"
    )

# Generate insert commands for Followers table
followers_insert_commands = []
for i in range(61, 261):
    follower_user_id = random.randint(15, 25)
    following_user_id = random.randint(15, 25)
    while following_user_id == follower_user_id:
        following_user_id = random.randint(15, 25)
    follow_date = random_date(datetime(2024, 1, 1), datetime(2024, 3, 1)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    followers_insert_commands.append(
        f"INSERT INTO Followers (FollowerID, FollowerUserID, FollowingUserID, FollowDate) VALUES ({i}, {follower_user_id}, {following_user_id}, '{follow_date}');"
    )

# Print the generated insert commands
#print("-- Users table insert commands")
#for command in users_insert_commands:
    #print(command)

#print("\n-- Posts table insert commands")
#for command in posts_insert_commands:
#    print(command)

#print("\n-- Likes table insert commands")
#for command in likes_insert_commands:
#    print(command)

print("\n-- Comments table insert commands")
for command in comments_insert_commands:
    print(command)

#print("\n-- Followers table insert commands")
#for command in followers_insert_commands:
#    print(command)
