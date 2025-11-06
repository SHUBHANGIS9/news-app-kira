import sqlite3

# Connect to the database
conn = sqlite3.connect('app_data.db')
cursor = conn.cursor()

# Fetch and display all users
print("Users Table:")
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()
for user in users:
    print(f"Username: {user[0]}, Password: {user[1]}")

print("\nArticle History Table:")
# Fetch and display article history
cursor.execute("SELECT * FROM article_history")
articles = cursor.fetchall()
for article in articles:
    print(f"Username: {article[0]}, Title: {article[1]}, Date: {article[2]}, Summary: {article[3]}")

# Close the connection
conn.close()
