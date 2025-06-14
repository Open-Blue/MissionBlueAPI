"""Mission Blue Module that holds file handling functions for saving and loading data."""

import csv
import os
from difflib import unified_diff

import pandas as pd
import requests

DIRECTORY_NAME = "Scraped Posts"

# Generates Directory where Scraped post will reside in
if not os.path.isdir(DIRECTORY_NAME):
    try:
        os.mkdir(DIRECTORY_NAME)
        print(f"Directory '{DIRECTORY_NAME}' created successfully.")
    except FileExistsError:
        print(f"Directory '{DIRECTORY_NAME}' already exists.")
    except PermissionError:
        print(f"Permission denied: Unable to create '{DIRECTORY_NAME}'.")


def validate_url(url: str) -> bool:
    """Validate URL to ensure it returns expected content.

    Returns:
        bool: True if URL returns expected content, False otherwise.
    """
    try:
        page = requests.get(url, timeout=10)
        content_string = page.text

        try:
            with open("tests/no_content_template.golden", "r", encoding="utf-8") as nct:
                no_content_template = nct.read()
        except (FileNotFoundError, PermissionError, OSError) as e:
            # Don't use sys.exit in functions - raise exceptions instead
            raise FileNotFoundError(f"Cannot read golden file: {e}") from e

        # Return True if content matches template (no differences)
        diff = unified_diff(
            content_string.splitlines(), no_content_template.splitlines()
        )
        diff_list = list(diff)
        return len(diff_list) != 0  # True if differences found

    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        raise requests.exceptions.RequestException(f"URL validation failed: {e}") from e


def extract_post_data(posts: list[dict]) -> list[dict]:
    """Extract relevant data from posts and filter by date range.

    :param posts: List of raw posts.
    :param START_DATE: Start date for filtering (YYYY-MM-DD).
    :param END_DATE: End date for filtering (YYYY-MM-DD).
    :return: List of dictionaries containing post data.
    """
    extracted_data = []

    for post in posts:
        try:
            post_content = post["record"].get("text", "")  # Extract the text content
            author_handle = post["author"].get(
                "handle", ""
            )  # Extract the author's handle
            created_at = post["indexedAt"]  # Extract the indexed timestamp
            post_id = post["uri"].split("/")[-1]
            post_link = f"https://bsky.app/profile/{author_handle}/post/{post_id}"

            if not validate_url(post_link):
                continue

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


def extract_post_data_from_csv(path: str) -> list[dict]:
    """Extract data from existing csv file.
    :param path: Path to file.
    :return: List of dictionaries containing post data from file.
    """
    post_from_csv: list[dict] = []
    if not os.path.isfile(path):
        print(f"File {path} not found.")
        return post_from_csv

    with open(path, encoding="utf-8") as file:
        csv_file = csv.DictReader(file)
        for lines in csv_file:
            post_from_csv.append(lines)
    return post_from_csv


def remove_duplicates(data: list[dict]) -> list[dict]:
    """This function removes duplicate entries from a list of dictionaries using the post_link key.

    Args:
        data list(dict): List of dictionaries with some duplicate entries.

    Returns:
        list(dict): List of dictionaries with duplicates removed.

    """
    post_links = set()
    unique_data = []
    for post in data:
        if post["post_link"] not in post_links:
            post_links.add(post["post_link"])
            unique_data.append(post)
    return unique_data


def save_to_csv(data: list[dict], path_to_file: str) -> None:
    """Save post data to a CSV file.
    :param data: List of post data dictionaries.
    :param filename: Output CSV filename.
    """
    if data:
        if os.path.isfile(path_to_file):
            data += extract_post_data_from_csv(path_to_file)
            data = remove_duplicates(data)
        data_frame = pd.DataFrame(data)
        data_frame.to_csv(path_to_file, index=False)
        print(f"Data saved to {path_to_file}")
    else:
        print("No posts to save.")
