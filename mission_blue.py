"""This module contains the BlueSky Web Scrapper."""

import click
import requests
import auth
import scraper
import file
from typing import Optional, List, Dict, Any

# pylint: disable=C0301

lang_dict = {
    "Afar": "aa",
    "Abkhazian": "ab",
    "Afrikaans": "af",
    "Akan": "ak",
    "Albanian": "sq",
    "Amharic": "am",
    "Arabic": "ar",
    "Aragonese": "an",
    "Armenian": "hy",
    "Assamese": "as",
    "Avaric": "av",
    "Avestan": "ae",
    "Aymara": "ay",
    "Azerbaijani": "az",
    "Bashkir": "ba",
    "Bambara": "bm",
    "Basque": "eu",
    "Belarusian": "be",
    "Bengali": "bn",
    "Bihari languages": "bh",
    "Bislama": "bi",
    "Tibetan": "bo",
    "Bosnian": "bs",
    "Breton": "br",
    "Bulgarian": "bg",
    "Burmese": "my",
    "Catalan": "ca",
    "Czech": "cs",
    "Chamorro": "ch",
    "Chechen": "ce",
    "Chinese": "zh",
    "Church Slavic": "cu",
    "Chuvash": "cv",
    "Cornish": "kw",
    "Corsican": "co",
    "Cree": "cr",
    "Welsh": "cy",
    "Danish": "da",
    "German": "de",
    "Divehi": "dv",
    "Dzongkha": "dz",
    "Greek, Modern (1453-)": "el",
    "English": "en",
    "Esperanto": "eo",
    "Estonian": "et",
    "Ewe": "ee",
    "Faroese": "fo",
    "Persian": "fa",
    "Fijian": "fj",
    "Finnish": "fi",
    "French": "fr",
    "Western Frisian": "fy",
    "Fulah": "ff",
    "Georgian": "ka",
    "Gaelic": "gd",
    "Irish": "ga",
    "Galician": "gl",
    "Manx": "gv",
    "Guarani": "gn",
    "Pushto": "ps",
    "Quechua": "qu",
    "Romansh": "rm",
    "Romanian": "ro",
    "Russian": "ru",
    "Sango": "sg",
    "Sanskrit": "sa",
    "Sinhala": "si",
    "Slovak": "sk",
    "Slovenian": "sl",
    "Northern Sami": "se",
    "Samoan": "sm",
    "Shona": "sn",
    "Sindhi": "sd",
    "Somali": "so",
    "Sotho, Southern": "st",
    "Spanish": "es",
    "Sardinian": "sc",
    "Serbian": "sr",
    "Swati": "ss",
    "Sundanese": "su",
    "Swahili": "sw",
    "Swedish": "sv",
    "Tahitian": "ty",
    "Tamil": "ta",
    "Tatar": "tt",
    "Telugu": "te",
    "Tajik": "tg",
    "Tagalog": "tl",
    "Thai": "th",
    "Tigrinya": "ti",
    "Tonga (Tonga Islands)": "to",
    "Tswana": "tn",
    "Tsonga": "ts",
    "Turkmen": "tk",
    "Turkish": "tr",
    "Twi": "tw",
    "Uighur": "ug",
    "Ukrainian": "uk",
    "Urdu": "ur",
    "Uzbek": "uz",
    "Venda": "ve",
    "Vietnamese": "vi",
    "Volapük": "vo",
    "Walloon": "wa",
    "Wolof": "wo",
    "Xhosa": "xh",
    "Yiddish": "yi",
    "Yoruba": "yo",
    "Zhuang": "za",
    "Zulu": "zu",
    "": "",
}


def resolve_handle_to_did(handle: str, token: str) -> str:
    """Resolve a Bluesky handle to DID."""
    url = "https://bsky.social/xrpc/com.atproto.identity.resolveHandle"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(
            url, headers=headers, params={"handle": handle}, timeout=10
        )
        response.raise_for_status()
        return str(response.json().get("did", handle))
    except requests.exceptions.RequestException as err:
        print(f"Error resolving handle: {err}")
        return handle


def generate_query_params(
    token: str,
    query: str = "",
    sort: str = "",
    since: str = "",
    until: str = "",
    mentions: str = "",
    author: str = "",
    lang: str = "",
    domain: str = "",
    url: str = "",
    tags: Optional[List[str]] = None,
    limit: int = 25,
    cursor: str = "",
    posts_limit: int = 500,
) -> Dict[str, Any]:
    # pylint: disable=R0917
    # pylint: disable=R0913
    # pylint: disable=C0301
    """Generates query parameters for the BlueSky search API.

    Args:
        token (str): The authorization token required to resolve handles.
        query (str, required): The search term for the BlueSky posts.
        sort (str, optional): The sorting criteria for results.
            - Options include "top" for top posts or "latest" for the latest posts.
        since (str, optional): The start date for posts (ISO 8601 format).
        until (str, optional): The end date for posts (ISO 8601 format).
        mentions (str, optional): Mentions to filter posts by.
            - Handles will be resolved to DIDs using the provided token.
        author (str, optional): The author of the posts (handle or DID).
            - Handles will be resolved to DIDs using the provided token.
        lang (str, optional): The language of the posts.
        domain (str, optional): A domain URL included in the posts.
        url (str, optional): A specific URL included in the posts.
        tags (list, optional): Tags to filter posts by (each tag <= 640 characters).
        limit (int, optional): The maximum number of posts to retrieve in a single response.
            - Defaults to 25.
        cursor (str, optional): A pagination token to fetch a specific set of results.
            - Use the `cursor` value returned in the previous API response to navigate through paginated results.
            - If `cursor` is an empty string, the API fetches the first page of results.
            - Cursors are opaque strings generated by the API and should not be modified manually.
        posts_limit (int, optional): The maximum number of posts to retrieve across all responses.
            - Defaults to 500.

    Returns:
        dict: A dictionary containing the query parameters for the API request.

    """
    if mentions:
        mentions = resolve_handle_to_did(mentions, token)
    if author:
        author = resolve_handle_to_did(author, token)

    # print(f"Generated query parameters: {locals()}")
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
        "cursor": cursor,
        "posts_limit": posts_limit,
    }


# Begin Click CLI


@click.command()
@click.option(
    "-q", "--query", type=str, required=True, help="Search query string. Required"
)
@click.option(
    "-s",
    "--sort",
    type=click.Choice(["top", "latest"], case_sensitive=False),
    required=False,
    help='Rank results by "top" or "latest',
)
@click.option(
    "--since",
    type=str,
    required=False,
    help=(
        "Filter results for posts after the specified datetime (inclusive). "
        'Use ISO 8601 format: "YYYY-MM-DD" or full datetime. Uses "sortAt" timestamp.'
    ),
)
@click.option(
    "--until",
    type=str,
    required=False,
    help=(
        "Filter results for posts before the specified datetime (not inclusive). "
        'Use ISO 8601 format: "YYYY-MM-DD" or full datetime. Uses "sortAt" timestamp.'
    ),
)
@click.option(
    "-m",
    "--mentions",
    type=str,
    help="Filter posts mentioning the specified account (omit the @ symbol).",
)
@click.option(
    "-a",
    "--author",
    type=str,
    required=False,
    help="Filter posts by the specified account (omit the @ symbol).",
)
@click.option(
    "-l",
    "--lang",
    type=str,
    required=False,
    help=f"Filter posts by language.\n\nLanguage Options:\n\n {', '.join(list(lang_dict.keys()))}\n\n",
)
@click.option(
    "-d",
    "--domain",
    type=str,
    required=False,
    help="Filter posts containing links to the specified domain.",
)
@click.option(
    "-u",
    "--url",
    type=str,
    required=False,
    help="Filter posts containing links to the specified url.",
)
@click.option(
    "-t",
    "--tags",
    type=str,
    multiple=True,
    required=False,
    help=(
        "Filter posts by hashtag (omit the # symbol). "
        'Multiple tags can be specified: -t tag1 -t tag2. OR -t "tag1, tag2"'
    ),
)
@click.option(
    "--limit",
    type=click.IntRange(1, 100),
    required=False,
    default=25,
    help=(
        "Set the maximum number of posts to retrieve in a single API response. This controls the page size for requests. "
        "Pagination is always enabled, and this option determines how many posts each request retrieves, up to a maximum of 100. "
        "The default value is 25 if not specified."
    ),
)
@click.option(
    "--posts_limit",
    type=click.IntRange(1, None),
    required=False,
    default=1000,
    help=(
        "Set the total number of posts to fetch from the API across all paginated responses. This value limits the total data retrieved "
        "even if multiple API calls are required. If not specified, 1000 posts will be recieved."
    ),
)
def main(
    query: str = "",
    sort: str = "",
    since: str = "",
    until: str = "",
    mentions: str = "",
    author: str = "",
    lang: str = "",
    domain: str = "",
    url: str = "",
    tags: tuple = (),
    limit: int = 25,
    posts_limit: int = 1000,
) -> None:
    """Method that tests if each click param flag is being passed in correctly."""
    # pylint: disable=R0913
    # pylint: disable=R0914
    # pylint: disable=R0917
    print("Loading Credentials...")
    bluesky_handle, bluesky_app_password = auth.load_credentials()

    if bluesky_handle is None or bluesky_app_password is None:
        raise ValueError("Bluesky handle and app password must not be None.")

    # Authenticate and create a session
    print("Authenticating...")
    access_token = auth.create_session(bluesky_handle, bluesky_app_password)
    print("Authentication successful.")

    query_param = generate_query_params(
        access_token,
        query,
        sort,
        since,
        until,
        mentions,
        author,
        lang,
        domain,
        url,
        list(tags) if tags else None,
        limit,
        posts_limit=posts_limit,
        cursor="",
    )

    # Fetch posts
    print("Fetching posts...")
    raw_posts = scraper.search_posts(query_param, access_token)

    # Extract post data
    print("Extracting post data...")
    post_data = file.extract_post_data(raw_posts)

    # Save posts to CSV
    print("Saving posts to CSV...")
    file.save_to_csv(post_data, f"Scraped Posts/{query}.csv")


if __name__ == "__main__":
    main()
