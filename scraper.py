"""
This module contains a function to search for posts using the BlueSky API.
"""

import requests
from alive_progress import alive_bar
from alive_progress.animations.bars import bar_factory


def search_posts(params, token):
    # pylint: disable=E1102
    # pylint: disable=C0301

    """
    Search for posts using the BlueSky API.

    Args:
        params (dict): The query parameters for the API request.
            - query (str, required): The search term for the BlueSky posts.
            - sort (str, optional): The sorting criteria for results.
               Options include "top" for top posts or "latest" for the latest posts.
            - since (str, optional): The start date for posts (ISO 8601 format).
            - until (str, optional): The end date for posts (ISO 8601 format).
            - mentions (str, optional): Mentions to filter posts by.
            - Handles will be resolved to DIDs using the provided token.
            - author (str, optional): The author of the posts (handle or DID).
            - lang (str, optional): The language of the posts.
            - domain (str, optional): A domain URL included in the posts.
            - url (str, optional): A specific URL included in the posts.
            - tags (list, optional): Tags to filter posts by (each tag <= 640 characters).
            - limit (int, optional): The maximum number of posts to retrieve in a single response.
                Defaults to 25.
            - cursor (str, optional): Pagination token for continuing from a previous request.
            - posts_limit (int, optional): The maximum number of posts to retrieve across all responses.
                Defaults to 500.

    Returns:
        list: A list of posts matching the search criteria.

    Notes:
        - Progress is displayed using a progress bar indicating the number of posts fetched.
        - Handles pagination automatically until `posts_limit` is reached or no further results are available.
        - Logs and returns partial results if an error occurs during fetching.
    """
    # Validate input parameters
    if "q" not in params:
        raise ValueError("Query parameter is required.")
    if not token:
        raise ValueError("Token is required.")

    posts = []
    url = "https://bsky.social/xrpc/app.bsky.feed.searchPosts"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    total_fetched = 0
    posts_limit = params.get("posts_limit", 500)
    butterfly_bar = bar_factory("✨", tip="🦋", errors="🔥🧯👩‍🚒")

    with alive_bar(posts_limit, bar=butterfly_bar, spinner="waves") as progress:
        while True:
            try:
                response = requests.get(url, headers=headers, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                # Check if we have reached our overall posts limit
                new_posts = data.get("posts", [])
                posts.extend(new_posts)
                total_fetched += len(new_posts)

                # Update progress bar
                progress(len(new_posts))

                if posts_limit and total_fetched >= posts_limit:
                    print(
                        f"Fetched {total_fetched} posts, total: {total_fetched}/{posts_limit}"
                    )
                    return posts[:posts_limit]

                # Move to the nextt page if available
                next_cursor = data.get("cursor")
                if not next_cursor:
                    print(f"All posts fetched. Total: {total_fetched}")
                    return posts

                params["cursor"] = next_cursor
            except requests.exceptions.RequestException as err:
                print(f"Error fetching posts: {err}")
                print(
                    "Response:",
                    response.text if "response" in locals() else "No response",
                )
                return posts
