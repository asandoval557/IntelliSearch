from tqdm import tk

import UI_ChatInterface
import DataBase
import NLP
import ComplianceSecurity
"""
def initialize_application():
    ""Initialize all components of the application.""
    print("Initializing application...")

    # Initialize database tables
    print("Setting up databases...")
    DataBase.init_db()

    # Populate demo database with sample data
    print("Checking demo database...")
    if DataBase.init_demo_db():
        print("Demo database populated with 200 random books.")
    else:
        print("Demo database already contains data.")

    # Initialize other components as needed
    print("Setting up security...")
    ComplianceSecurity.init()

    print("Application initialization complete!")

def main():
    # Initialize NLP module
    NLP.init_nlp()
    # Launch chat interface (blocks until exit)
    UI_ChatInterface.run_chat()

if __name__ == "__main__":
    main() """


def test_nlp_module():
    """Test the NLP module functionality"""
    print("=" * 50)
    print("TESTING NLP MODULE")
    print("=" * 50)

    try:
        from NLP import init_nlp, parse_query, process_natural_language_query

        # Initialize NLP
        print("Initializing NLP...")
        init_nlp()
        print("✓ NLP initialized successfully")

        # Test queries
        test_queries = [
            "Show me Fantasy books from 2020",
            "I want Horror novels from the last 5 years",
            "Find Science Fiction books published in 1995",
            "Recent Mystery books"
        ]

        for query in test_queries:
            print(f"\n--- Testing Query: '{query}' ---")

            # Test parsing
            parse_result = parse_query(query)
            print(f"Parse result: {parse_result}")

            # Test database filter creation
            db_filter = process_natural_language_query(query)
            print(f"DB filter: {db_filter}")

        return True

    except Exception as e:
        print(f"❌ NLP Module Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_module():
    """Test the database module functionality"""
    print("\n" + "=" * 50)
    print("TESTING DATABASE MODULE")
    print("=" * 50)

    try:
        import sqlite3
        from DataBase import init_demo_db, query_books

        # Initialize database
        print("Initializing database...")
        init_demo_db()
        print("✓ Database initialized")

        # Check if database exists and has data
        print("Checking database contents...")
        conn = sqlite3.connect('demo_books.db')
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM books")
        count = cursor.fetchone()[0]
        print(f"✓ Books in database: {count}")

        if count == 0:
            print("⚠️  Database is empty! Running populate_demo_books...")
            from DataBase import populate_demo_books
            populate_demo_books(50)  # Add 50 test books
            cursor.execute("SELECT COUNT(*) FROM books")
            count = cursor.fetchone()[0]
            print(f"✓ Books after population: {count}")

        # Show sample records
        cursor.execute("SELECT title, genre, publication_year FROM books LIMIT 5")
        samples = cursor.fetchall()
        print("\nSample books:")
        for i, book in enumerate(samples, 1):
            print(f"  {i}. {book[0]} ({book[1]}, {book[2]})")

        # Test unique genres
        cursor.execute("SELECT DISTINCT genre FROM books ORDER BY genre")
        genres = [row[0] for row in cursor.fetchall()]
        print(f"\nGenres in database: {genres}")

        conn.close()

        # Test query_books function
        print("\n--- Testing query_books function ---")

        # Test with empty filter (should return all books)
        results = query_books({})
        print(f"✓ query_books({{}}) returned {len(results)} results")

        return True

    except Exception as e:
        print(f"❌ Database Module Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """Test the integration between NLP and Database"""
    print("\n" + "=" * 50)
    print("TESTING INTEGRATION")
    print("=" * 50)

    try:
        from NLP import process_natural_language_query
        from DataBase import query_books

        test_queries = [
            "Show me Fantasy books",
            "Find books from 2020",
            "Horror novels"
        ]

        for query in test_queries:
            print(f"\n--- Full Integration Test: '{query}' ---")

            # Process with NLP
            db_filter = process_natural_language_query(query)
            print(f"NLP Filter: {db_filter}")

            # Query database
            results = query_books(db_filter)
            print(f"Database Results: {len(results)} books found")

            # Show first few results
            for i, book in enumerate(results[:3]):
                print(f"  {i + 1}. {book}")

        return True

    except Exception as e:
        print(f"❌ Integration Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("TROUBLESHOOTING NLP + DATABASE INTEGRATION")
    print("=" * 60)

    # Run tests in order
    nlp_success = test_nlp_module()
    db_success = test_database_module()

    if nlp_success and db_success:
        integration_success = test_integration()

        if integration_success:
            print("\n" + "=" * 60)
            print("🎉 ALL TESTS PASSED! Integration is working!")
        else:
            print("\n" + "=" * 60)
            print("❌ Integration failed - check the integration function")
    else:
        print("\n" + "=" * 60)
        print("❌ Basic modules failed - fix individual components first")


if __name__ == "__main__":
    main()