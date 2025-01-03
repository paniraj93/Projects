# streamlit run E:/pavithra/social_media_analysis.py
import streamlit as st
import pandas as pd
import mysql.connector

# Create a connection to the MySQL database
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='652727533266',
    database='social'
)
cursor = conn.cursor()

# Sidebar with buttons
selected_page = st.sidebar.selectbox('Navigation', ['Dashboard', 'Posts and their like counts',
                                                 'Users who have not posted anything',
                                                 'Posts by a specific user and their comment count',
                                                 'Popular posts with the most comments',
                                                 'Users who liked a specific post',
                                                 'Popular posts with the most likes'])

# Functions to execute queries
def dashboard():
    # Number of users
    cursor.execute("SELECT COUNT(*) FROM Users")
    num_users = cursor.fetchone()[0]

    # Number of posts
    cursor.execute("SELECT COUNT(*) FROM Posts")
    num_posts = cursor.fetchone()[0]

    # Number of likes
    cursor.execute("SELECT COUNT(*) FROM Likes")
    num_likes = cursor.fetchone()[0]

    # Number of comments
    cursor.execute("SELECT COUNT(*) FROM Comments")
    num_comments = cursor.fetchone()[0]
    st.title("Welcome To DASHBOARD")
    st.write("## Key Performance Indicators")
    st.write(f"#### Number of Users: {num_users}")
    st.write(f"#### Number of Posts: {num_posts}")
    st.write(f"#### Number of Likes: {num_likes}")
    st.write(f"#### Number of Comments: {num_comments}")

    # Bar graphs
    st.write("## Bar Graphs")
    
    # User vs Likes
    st.write("#### User vs Likes")
    cursor.execute('''SELECT Users.UserName, COUNT(Likes.LikeID) AS LikeCount
                      FROM Users
                      LEFT JOIN Likes ON Users.UserID = Likes.UserID
                      GROUP BY Users.UserName''')
    data = cursor.fetchall()
    df_likes = pd.DataFrame(data, columns=['UserName', 'LikeCount'])
    st.bar_chart(df_likes.set_index('UserName'))

    # User vs Comments
    st.write("#### User vs Comments")
    cursor.execute('''SELECT Users.UserName, COUNT(Comments.CommentID) AS CommentCount
                      FROM Users
                      LEFT JOIN Comments ON Users.UserID = Comments.UserID
                      GROUP BY Users.UserName''')
    data = cursor.fetchall()
    df_comments = pd.DataFrame(data, columns=['UserName', 'CommentCount'])
    st.bar_chart(df_comments.set_index('UserName'))

    # User vs Posts
    st.write("####  User vs Posts")
    cursor.execute('''SELECT Users.UserName, COUNT(Posts.PostID) AS PostCount
                      FROM Users
                      LEFT JOIN Posts ON Users.UserID = Posts.UserID
                      GROUP BY Users.UserName''')
    data = cursor.fetchall()
    df_posts = pd.DataFrame(data, columns=['UserName', 'PostCount'])
    st.bar_chart(df_posts.set_index('UserName'))


def posts_and_like_counts():
    st.write("## Number of Posts and Likes per Post")
    cursor.execute('''SELECT Posts.PostID, Posts.Content, COUNT(Likes.LikeID) AS LikeCount
                      FROM Posts
                      LEFT JOIN Likes ON Posts.PostID = Likes.PostID
                      GROUP BY Posts.PostID, Posts.Content''')
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['PostID', 'Content', 'LikeCount'])
    st.write(df)

def users_not_posted():
    st.write("## Users who have not posted any content yet")
    cursor.execute('''SELECT Users.UserName
                      FROM Users
                      LEFT JOIN Posts ON Users.UserID = Posts.UserID
                      WHERE Posts.PostID IS NULL''')
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['UserName'])
    st.write(df)

def posts_by_user():
    st.write("## Posts by a specific user and their comment count")
    user_id = st.text_input("Enter user ID:")
    if  st.button("Submit"):
        cursor.execute(f'''SELECT Posts.PostID, Posts.Content, COUNT(Comments.CommentID) AS CommentCount
                            FROM Posts
                            LEFT JOIN Comments ON Posts.PostID = Comments.PostID
                            WHERE Posts.UserID = {user_id}
                            GROUP BY Posts.PostID, Posts.Content''')
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=['PostID', 'POST DETAILS', 'CommentCount'])
        st.write(df)

def popular_posts_comments():
    st.write("## Popular posts with the most comments")
    cursor.execute('''SELECT Posts.PostID, Posts.Content, COUNT(Comments.CommentID) AS CommentCount
                      FROM Posts
                      LEFT JOIN Comments ON Posts.PostID = Comments.PostID
                      GROUP BY Posts.PostID, Posts.Content
                      ORDER BY CommentCount DESC''')
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['PostID', 'Content', 'CommentCount'])
    st.write(df)

def users_liked_post():
    st.write("## Users that liked a specific post")
    post_id = st.text_input("Enter post ID:")
    if  st.button("Submit"):
        cursor.execute(f'''SELECT Users.UserName
                            FROM Users
                            JOIN Likes ON Users.UserID = Likes.UserID
                            WHERE Likes.PostID = {post_id}''')
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=['UserName'])
        st.write(df)

def popular_posts_likes():
    st.write("## Most liked posts")
    cursor.execute('''SELECT Posts.PostID, Posts.Content, COUNT(Likes.LikeID) AS LikeCount
                      FROM Posts
                      LEFT JOIN Likes ON Posts.PostID = Likes.PostID
                      GROUP BY Posts.PostID, Posts.Content
                      ORDER BY LikeCount DESC''')
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['PostID', 'Content', 'LikeCount'])
    st.write(df)

# Display selected page
if selected_page == 'Dashboard':
    dashboard()
elif selected_page == 'Posts and their like counts':
    posts_and_like_counts()
elif selected_page == 'Users who have not posted anything':
    users_not_posted()
elif selected_page == 'Posts by a specific user and their comment count':
    posts_by_user()
elif selected_page == 'Popular posts with the most comments':
    popular_posts_comments()
elif selected_page == 'Users who liked a specific post':
    users_liked_post()
elif selected_page == 'Popular posts with the most likes':
    popular_posts_likes()

# Close the connection to the MySQL database
conn.close()
