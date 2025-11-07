#!/usr/bin/env python3
"""
Concurrent Asynchronous Database Queries
"""

import asyncio
import aiosqlite


DB_FILE = "users.db"


async def async_fetch_users():
    """Fetch all users asynchronously"""
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT * FROM users") as cursor:
            users = await cursor.fetchall()
            print("\nAll Users:")
            for user in users:
                print(user)
            return users


async def async_fetch_older_users():
    """Fetch users older than 40 asynchronously"""
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT * FROM users WHERE age > 40") as cursor:
            older_users = await cursor.fetchall()
            print("\nUsers older than 40:")
            for user in older_users:
                print(user)
            return older_users


async def fetch_concurrently():
    """Run both queries concurrently"""
    # Run both async functions at once
    results = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )

    # Optional: access results if needed
    all_users, older_users = results
    print(f"\nFetched {len(all_users)} total users.")
    print(f"Fetched {len(older_users)} users older than 40.")


if __name__ == "__main__":
    asyncio.run(fetch_concurrently())
