from tqdm import tk

import UI_ChatInterface
import DataBase
import NLP
import ComplianceSecurity

def initialize_application():
    """Initialize all components of the application."""
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
    main()