#!/usr/bin/python3
seed = __import__('seed')

def paginate_users(page_size, offset):
    """
    Fetches a single page of users from user_data table.

    Args:
        page_size (int): Number of rows per page.
        offset (int): Offset from where to start fetching rows.

    Returns:
        list: A list of user dictionaries from the database.
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    connection.close()
    return rows


def lazy_pagination(page_size):
    """
    Generator that lazily fetches paginated user data.
    Fetches the next page only when requested.

    Args:
        page_size (int): Number of users to fetch per page.

    Yields:
        list: The next page of users as a list of dictionaries.
    """
    offset = 0

    # Single loop — keeps fetching pages until no more data
    while True:
        page = paginate_users(page_size, offset)
        if not page:  # no more users left
            break
        yield page
        offset += page_size
