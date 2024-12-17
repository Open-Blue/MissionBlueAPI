"""
This module conatins the BlueSky Web Scrapper
"""

import os
import sys
import shutil
from dotenv import load_dotenv
import requests
import pandas as pd

# Load environment variables from the .env file
load_dotenv()

# Access credentials from the environment variables
BLUESKY_HANDLE = os.getenv("BLUESKY_HANDLE")
BLUESKY_APP_PASSWORD = os.getenv("BLUESKY_APP_PASSWORD")

DIRECTORY_NAME = "Scrapped Posts"

# Generates Directory where scrapped post will reside in
if not os.path.isdir(DIRECTORY_NAME):
    try:
        os.mkdir(DIRECTORY_NAME)
        print(f"Directory '{DIRECTORY_NAME}' created successfully.")
    except FileExistsError:
        print(f"Directory '{DIRECTORY_NAME}' already exists.")
    except PermissionError:
        print(f"Permission denied: Unable to create '{DIRECTORY_NAME}'.")


# Base URL
BASE_URL = "https://bsky.social/xrpc"


def create_session():
    """
    Authenticate and create a session to get the access token.

    :return: Access token (accessJwt) for authentication.
    """
    url = f"{BASE_URL}/com.atproto.server.createSession"
    payload = {"identifier": BLUESKY_HANDLE, "password": BLUESKY_APP_PASSWORD}

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        session = response.json()
        return session["accessJwt"]
    except requests.exceptions.RequestException as err:
        print("Error during authentication:", err)
        print("Response:", response.text if "response" in locals() else "No response")
        sys.exit(1)


def resolve_handle_to_did(handle: str, token: str) -> str:
    """
    Resolve a Bluesky handle to DID
    """

    url = f"{BASE_URL}/com.atproto.identity.resolveHandle"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(url, headers=headers, params={"handle": handle}, timeout=10)
        response.raise_for_status()
        return response.json().get("did", handle)
    except requests.exceptions.RequestException as err:
        print(f"Error resolving handle: {err}")
        return handle


def generate_query_params(
    token: str, query="", sort="", since="", until="",
    mentions="", author="", lang="", domain="", url="",
    tags=None, limit=25, cursor=""
):
    # pylint: disable=R0917
    # pylint: disable=R0913
    """This functions

    Args:
        query (str): The search term for the BlueSky Posts
        since (str): The start date for posts
        until (str): The end date for posts
        limit (int, optional): Number of posts queried. Max is 100.
        sort (str): Query for top posts or latest post
        cursor (str, optional): _description_. Defaults to "".

    Returns:
        _type_: _description_
    """
    if mentions:
        mentions = resolve_handle_to_did(mentions, token)
    if author:
        author = resolve_handle_to_did(author, token)

    print(f"Generated query parameters: {locals()}")
    return {
        "q": query,
        "sort": sort,
        "since": since,
        "until": until,
        "mentions": mentions,
        "author": author,
        "lang": lang,
        "domain": domain,
        "url": url,
        "tag": tags,
        "limit": limit,
        "cursor": cursor
    }


def search_posts(params, token):
    """
    Search for posts using the BlueSky API.

    :param query: The search query string.
    :param access_token: Access token for authentication.
    :param limit: Number of posts to fetch, can change in main.
    :param sort: Sorting order ('latest' or 'top').
    :return: List of posts.
    """
    posts = []
    url = f"{BASE_URL}/app.bsky.feed.searchPosts"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    counter = 0
    while True:
        counter += 1
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            # print(response)
            response.raise_for_status()
            posts = response.json().get("posts", []) + posts
            data = response.json()

            next_cursor = data.get("cursor")
            if not next_cursor:
                return posts

            params["cursor"] = next_cursor
        except requests.exceptions.RequestException as err:
            print(f"Error fetching posts: {err}")
            print(
                "Response:", response.text if "response" in locals() else "No response"
            )
            return posts


def extract_post_data(posts):
    """
    Extract relevant data from posts and filter by date range.

    :param posts: List of raw posts.
    :param START_DATE: Start date for filtering (YYYY-MM-DD).
    :param END_DATE: End date for filtering (YYYY-MM-DD).
    :return: List of dictionaries containing post data.
    """
    extracted_data = []

    for post in posts:
        try:
            post_content = post["record"].get("text", "")  # Extract the text content
            author_handle = post["author"]["handle"]  # Extract the author's handle
            created_at = post["indexedAt"]  # Extract the indexed timestamp
            post_id = post["uri"].split("/")[-1]
            post_link = f"https://bsky.app/profile/{author_handle}/post/{post_id}"

            extracted_data.append(
                {
                    "author": author_handle,
                    "content": post_content,
                    "created_at": created_at,
                    "post_link": post_link,
                }
            )
        except KeyError as err:
            print(f"Missing data in post: {err}")
    return extracted_data


def save_to_csv(data, filename):
    """
    Save post data to a CSV file.

    :param post_data: List of post data dictionaries.
    :param filename: Output CSV filename.
    """
    if data:
        if os.path.isfile(filename):
            os.remove(filename)
        data_frame = pd.DataFrame(data)
        data_frame.to_csv(filename, index=False)
        shutil.move(f"{filename}", DIRECTORY_NAME)
        print(f"Data saved to {DIRECTORY_NAME}/{filename}")
        print(f"Data saved to {filename}")
    else:
        print("No posts to save.")


if __name__ == "__main__":
    # Authenticate and create a session
    print("Authenticating...")
    access_token = create_session()
    print("Authentication successful.")

    # Get user input for the search query and date range
    search_query = input("Enter your Query: ")

    # Authenticate and create a session
    print("Authenticating...")
    access_token = create_session()
    print("Authentication successful.")

    query_param = generate_query_params(
        token=access_token, query=search_query)


    # Fetch posts
    print("Fetching posts...")
    raw_posts = search_posts(query_param, access_token)

    # Extract post data
    print("Extracting post data...")
    post_data = extract_post_data(raw_posts)

    # print("Here is the data:", post_data)

    # Save posts to CSV
    print("Saving posts to CSV...")
    save_to_csv(post_data, f"{search_query}.csv")
