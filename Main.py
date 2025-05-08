import UI_ChatInterface
import DataBase
import NLP
import ComplianceSecurity


def main():
    # Initialize database connection
    DataBase.init_db()
    # Initialize NLP module
    NLP.init_nlp()
    # Initialize compliance module
    ComplianceSecurity.init()
    # Launch chat interface (blocks until exit)
    UI_ChatInterface.run_chat()

if __name__ == "__main__":
    main()