"""Testing suite for the mission_blue module."""

import tempfile
import unittest
import typing

from file import (
    extract_post_data,
    extract_post_data_from_csv,
    remove_duplicates,
    save_to_csv,
    validate_url,
)


class TestCase:
    """Class used to store test data and expected results for the TestMissionBlue function."""

    def __init__(self, data: typing.Any, expected_result: typing.Any) -> None:
        self.data = data
        self.expected_result = expected_result

    def get_data(self) -> typing.Any:
        # pylint: disable=missing-function-docstring
        return self.data

    def get_expected_result(self) -> typing.Any:
        # pylint: disable=missing-function-docstring
        return self.expected_result


class TestValidateUrl(unittest.TestCase):
    """_summary_.

    Args:
        unittest (_type_): _description_

    """

    def test_validate_url(self) -> None:
        """Test case for the validate_url function.
        This test verifies that the given url contains the correct post data.
        Test data:
        - Post Links with valid and invalid post urls.
        - An expected result boolean.
        Assertions:
        - The result of validate_url(data) should match the expected_result.
        """
        # If any of the test cases fail, try looking at the no_content_template variable
        # within the validate_url function.
        cases = {
            "Post Exists": TestCase(
                data="https://bsky.app/profile/witheringtales.bsky.social/post/3legkyuzjs22m",
                expected_result=True,
            ),
            # If the test case fails, look at the validate_url function logic for guidance
            # on how to fix the test case.
            "Post Doesn't Exist": TestCase(
                data="https://bsky.app/profile/witheringtales.bsky.social/post/3legkyuzjs22",
                expected_result=False,
            ),
        }

        for case_name, case in cases.items():
            with self.subTest(case_name):
                result = validate_url(case.get_data())
                self.assertEqual(result, case.get_expected_result())


class TestExtractPostData(unittest.TestCase):
    """_summary_.

    Args:
        unittest (_type_): _description_

    """

    def test_extract_post_data(self) -> None:
        """Test case for the extract_post_data function.
        This test verifies that the remove_duplicates function correctly removes
        duplicate entries from a list of dictionaries. Each dictionary represents
        a post with the following keys: 'author', 'content', 'created_at', and 'post_link'.
        Test data:
        - A list of dictionaries with some duplicate entries.
        - An expected result list with duplicates removed.
        Assertions:
        - The result of remove_duplicates(data) should match the expected_result.
        """
        cases = {
            "No Post Data": TestCase(
                data=[],
                expected_result=[],
            ),
            "Contains Post Data": TestCase(
                data=[
                    {
                        "record": {"text": "contentABC"},
                        "author": {"handle": "witheringtales.bsky.social"},
                        "indexedAt": "2023-01-01",
                        "uri": "3legkyuzjs22m",
                    }
                ],
                expected_result=[
                    {
                        "author": "witheringtales.bsky.social",
                        "content": "contentABC",
                        "created_at": "2023-01-01",
                        # pylint: disable=line-too-long
                        "post_link": "https://bsky.app/profile/witheringtales.bsky.social/post/3legkyuzjs22m",
                    },
                ],
            ),
        }

        for case_name, case in cases.items():
            with self.subTest(case_name):
                result = extract_post_data(case.get_data())
                self.assertEqual(result, case.get_expected_result())


class TestExtractPostDataFromCsv(unittest.TestCase):
    """_summary_.

    Args:
        unittest (_type_): _description_

    """

    def test_extract_post_data_from_csv(self) -> None:
        """Test case for the extract_post_data_from_csv function."""
        cases = {
            "No Path": TestCase(data="", expected_result=[]),
            "File Contains Content": TestCase(
                # pylint: disable=line-too-long
                data="""author,content,created_at,post_link\nuser1,"post1",2023-01-01,link1\nuser2,"post2",2023-01-02,link2\nuser3,"post3",2023-01-03,link3""",
                expected_result=[
                    {
                        "author": "user1",
                        "content": "post1",
                        "created_at": "2023-01-01",
                        "post_link": "link1",
                    },
                    {
                        "author": "user2",
                        "content": "post2",
                        "created_at": "2023-01-02",
                        "post_link": "link2",
                    },
                    {
                        "author": "user3",
                        "content": "post3",
                        "created_at": "2023-01-03",
                        "post_link": "link3",
                    },
                ],
            ),
        }

        for case_name, case in cases.items():
            with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp:
                with self.subTest(case_name):
                    content = case.get_data()
                    # pylint: disable=line-too-long
                    if temp.write(content):
                        # If this line is commented, the test will fail. I believe that
                        # it is because the temp file is deleted once it is writen to
                        # causing the file to be empty when the extract_post_data_from_csv
                        # function is called in the next line.
                        print(f"file: {temp.read()}")
                        result = extract_post_data_from_csv(temp.name)
                        self.assertListEqual(result, case.get_expected_result())


class TestRemoveDuplicates(unittest.TestCase):
    """_summary_.

    Args:
        unittest (_type_): _description_

    """

    def test_remove_duplicates(self) -> None:
        """Test case for the remove_duplicates function.
        This test verifies that the remove_duplicates function correctly removes
        duplicate entries from a list of dictionaries. Each dictionary represents
        a post with the following keys: 'author', 'content', 'created_at', and 'post_link'.
        Test data:
        - A list of dictionaries with some duplicate entries.
        - An expected result list with duplicates removed.
        Assertions:
        - The result of remove_duplicates(data) should match the expected_result.
        """
        cases = {
            "Contains Duplicates": TestCase(
                data=[
                    {
                        "author": "user1",
                        "content": "post1",
                        "created_at": "2023-01-01",
                        "post_link": "link1",
                    },
                    {
                        "author": "user2",
                        "content": "post2",
                        "created_at": "2023-01-02",
                        "post_link": "link2",
                    },
                    {
                        "author": "user1",
                        "content": "post1",
                        "created_at": "2023-01-01",
                        "post_link": "link1",
                    },
                ],
                expected_result=[
                    {
                        "author": "user1",
                        "content": "post1",
                        "created_at": "2023-01-01",
                        "post_link": "link1",
                    },
                    {
                        "author": "user2",
                        "content": "post2",
                        "created_at": "2023-01-02",
                        "post_link": "link2",
                    },
                ],
            ),
            "Doesn't Contains Duplicates": TestCase(
                data=[
                    {
                        "author": "user1",
                        "content": "post1",
                        "created_at": "2023-01-01",
                        "post_link": "link1",
                    },
                    {
                        "author": "user2",
                        "content": "post2",
                        "created_at": "2023-01-02",
                        "post_link": "link2",
                    },
                    {
                        "author": "user1",
                        "content": "post1",
                        "created_at": "2023-01-01",
                        "post_link": "link3",
                    },
                ],
                expected_result=[
                    {
                        "author": "user1",
                        "content": "post1",
                        "created_at": "2023-01-01",
                        "post_link": "link1",
                    },
                    {
                        "author": "user2",
                        "content": "post2",
                        "created_at": "2023-01-02",
                        "post_link": "link2",
                    },
                    {
                        "author": "user1",
                        "content": "post1",
                        "created_at": "2023-01-01",
                        "post_link": "link3",
                    },
                ],
            ),
        }

        for case_name, case in cases.items():
            with self.subTest(case_name):
                result = remove_duplicates(case.get_data())
                self.assertEqual(result, case.get_expected_result())


class TestSaveToCsv(unittest.TestCase):
    """_summary_.

    Args:
        unittest (_type_): _description_

    """

    def test_save_to_csv(self) -> None:
        """Test case for the save_to_csv function."""
        cases = {
            "Write Data to new File": TestCase(
                data=(
                    [
                        {
                            "author": "userA",
                            "content": "postA",
                            "created_at": "2023-01-01",
                            "post_link": "linkA",
                        },
                        {
                            "author": "userB",
                            "content": "postB",
                            "created_at": "2023-01-02",
                            "post_link": "linkB",
                        },
                        {
                            "author": "userC",
                            "content": "postC",
                            "created_at": "2023-01-03",
                            "post_link": "linkC",
                        },
                    ],
                    "",
                ),
                # pylint: disable=line-too-long
                expected_result=""""author,content,created_at,post_link\nuserA,"postA",2023-01-01,linkA\nuserB,"postB",2023-01-02,linkB\nuserC,"postC",2023-01-03,linkC""",
            ),
            "Write Data to empty File": TestCase(data=([{}], ""), expected_result=""),
            "File Contains Content": TestCase(
                data=(
                    [
                        {
                            "author": "userA",
                            "content": "postA",
                            "created_at": "2023-01-01",
                            "post_link": "linkA",
                        },
                    ],
                    # pylint: disable=line-too-long
                    """author,content,created_at,post_link\nuser1,"post1",2023-01-01,link1\nuser2,"post2",2023-01-02,link2\nuser3,"post3",2023-01-03,link3""",
                ),
                # pylint: disable=line-too-long
                expected_result="""author,content,created_at,post_link\nuser1,post1,2023-01-01,link1\nuser2,post2,2023-01-02,link2\nuser3,post3,2023-01-03,link3\nuserA,postA,2023-01-01,linkA""",
            ),
        }

        for case_name, case in cases.items():
            # pylint: disable=line-too-long
            with self.subTest(case_name):
                with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp:
                    new_data, existing_data = case.get_data()
                    if temp.write(existing_data):
                        # If this line is commented, the test will fail. I believe
                        # that it is because the temp file is deleted once it is
                        # writen to causing the file to be empty when the
                        # extract_post_data_from_csv function is called in the
                        # next line.
                        print(f"file: {temp.read()}")
                        save_to_csv(new_data, temp.name)
                        # temp.flush()
                        temp.seek(0)
                        file_content = temp.read()
                        print(f"file_content: {file_content}")
                        # Compare file content regardless of line order
                        file_lines = sorted(file_content.strip().split("\n"))
                        expected_lines = sorted(
                            case.get_expected_result().strip().split("\n")
                        )
                        print(f"file_lines: {file_lines}")
                        print(f"expected_lines: {expected_lines}")
                        self.assertEqual(file_lines, expected_lines)


if __name__ == "__main__":
    unittest.main()
