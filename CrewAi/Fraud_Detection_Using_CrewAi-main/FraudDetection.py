import os
from crewai import Agent, Task, Crew
from crewai.tools import tool
from dotenv import load_dotenv

# Set up the environment variables for OpenAI API
load_dotenv()
os.environ["OPENAI_MODEL_NAME"] = os.getenv("OPENAI_MODEL_NAME")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

bank_transactions = {
    # Fraudulent transactions with sudden jumps in location
    101: [
        # San Francisco transactions
        {"timestamp": "2025-05-30T06:45:00Z", "amount": -50, "latitude": 37.7749, "longitude": -122.4194},
        {"timestamp": "2025-05-30T07:00:00Z", "amount": 150, "latitude": 37.7750, "longitude": -122.4195},
        {"timestamp": "2025-05-30T07:15:00Z", "amount": -25, "latitude": 37.7751, "longitude": -122.4196},
        {"timestamp": "2025-05-30T07:30:00Z", "amount": 75, "latitude": 37.7752, "longitude": -122.4197},
        {"timestamp": "2025-05-30T07:45:00Z", "amount": -30, "latitude": 37.7753, "longitude": -122.4198},

        # Sudden move to New York
        {"timestamp": "2025-05-30T08:00:00Z", "amount": 200, "latitude": 40.7128, "longitude": -74.0060},
        {"timestamp": "2025-05-30T08:15:00Z", "amount": -10, "latitude": 40.7130, "longitude": -74.0062},
        {"timestamp": "2025-05-30T08:30:00Z", "amount": 50, "latitude": 40.7131, "longitude": -74.0063},

        # 🚨 Suspicious jump to India (Delhi) — 3 transactions
        {"timestamp": "2025-05-30T08:45:00Z", "amount": -20, "latitude": 28.6139, "longitude": 77.2090},  # Delhi
        {"timestamp": "2025-05-30T09:00:00Z", "amount": 100, "latitude": 28.6140, "longitude": 77.2092},
        {"timestamp": "2025-05-30T09:15:00Z", "amount": -60, "latitude": 28.6141, "longitude": 77.2094},
    ],
    # Fraudulent transactions with jumps , but possible in real time
    202: [
        {"timestamp": "2025-05-30T06:45:00Z", "amount": -50, "latitude": 37.7749, "longitude": -122.4194},  # San Francisco
        {"timestamp": "2025-05-30T07:00:00Z", "amount": 150, "latitude": 37.7750, "longitude": -122.4195},
        {"timestamp": "2025-05-30T07:15:00Z", "amount": -25, "latitude": 37.7751, "longitude": -122.4196},
        {"timestamp": "2025-05-30T07:30:00Z", "amount": 75, "latitude": 37.7752, "longitude": -122.4197},
        {"timestamp": "2025-05-30T07:45:00Z", "amount": -30, "latitude": 37.7753, "longitude": -122.4198},
        
        # 🚨 Suspicious jump to New York just 15 minutes later
        {"timestamp": "2025-05-30T08:00:00Z", "amount": 200, "latitude": 40.7128, "longitude": -74.0060},  # New York
        {"timestamp": "2025-05-30T08:15:00Z", "amount": -10, "latitude": 40.7130, "longitude": -74.0062},
        {"timestamp": "2025-05-30T08:30:00Z", "amount": 50, "latitude": 40.7131, "longitude": -74.0063},
        {"timestamp": "2025-05-30T08:45:00Z", "amount": -20, "latitude": 40.7132, "longitude": -74.0064},
        {"timestamp": "2025-05-30T09:00:00Z", "amount": 100, "latitude": 40.7133, "longitude": -74.0065},
    ],
    # Fraudulent transactions with sudden spending of large ammount, but still possible
    303: [
        {"timestamp": "2025-05-30T06:45:00Z", "amount": -50, "latitude": 37.7749, "longitude": -122.4194}, 
        {"timestamp": "2025-05-30T07:00:00Z", "amount": 150, "latitude": 37.7750, "longitude": -122.4195},
        {"timestamp": "2025-05-30T07:15:00Z", "amount": -25, "latitude": 37.7751, "longitude": -122.4196},
        {"timestamp": "2025-05-30T07:30:00Z", "amount": 75, "latitude": 37.7752, "longitude": -122.4197},
        {"timestamp": "2025-05-30T07:45:00Z", "amount": -30, "latitude": 37.7753, "longitude": -122.4198},
        # 🚨 Sudden overspending
        {"timestamp": "2025-05-30T08:00:00Z", "amount": 5000, "latitude": 37.7754, "longitude": -122.4199},
        {"timestamp": "2025-05-30T08:15:00Z", "amount": -10, "latitude": 37.7755, "longitude": -122.4200},
        {"timestamp": "2025-05-30T08:30:00Z", "amount": 50, "latitude": 37.7756, "longitude": -122.4201},
        {"timestamp": "2025-05-30T08:45:00Z", "amount": -20, "latitude": 37.7757, "longitude": -122.4202},
        {"timestamp": "2025-05-30T09:00:00Z", "amount": 100, "latitude": 37.7758, "longitude": -122.4203},
    ],
    # Fraudlent transactions with a sudden large spending clearly indicating a fraud
    404: [
        {"timestamp": "2025-05-30T06:45:00Z", "amount": -50, "latitude": 37.7749, "longitude": -122.4194},
        {"timestamp": "2025-05-30T07:00:00Z", "amount": 150, "latitude": 37.7750, "longitude": -122.4195},
        {"timestamp": "2025-05-30T07:15:00Z", "amount": -25, "latitude": 37.7751, "longitude": -122.4196},
        {"timestamp": "2025-05-30T07:30:00Z", "amount": 75, "latitude": 37.7752, "longitude": -122.4197},
        {"timestamp": "2025-05-30T07:45:00Z", "amount": -30, "latitude": 37.7753, "longitude": -122.4198},
        # 🚨 Sudden large spending
        {"timestamp": "2025-05-30T08:00:00Z", "amount": 100000, "latitude": 37.7754, "longitude": -122.4199},  # Clearly fraudulent
        {"timestamp": "2025-05-30T08:15:00Z", "amount": -10, "latitude": 37.7755, "longitude": -122.4200},
        {"timestamp": "2025-05-30T08:30:00Z", "amount": 50, "latitude": 37.7756, "longitude": -122.4201},
        {"timestamp": "2025-05-30T08:45:00Z", "amount": -20, "latitude": 37.7757, "longitude": -122.4202},
        {"timestamp": "2025-05-30T09:00:00Z", "amount": 100, "latitude": 37.7758, "longitude": -122.4203},
    ],
    # transactions are consistent with a pattern of spending and location hence not a fraud
    505: [
        {"timestamp": "2025-05-29T09:00:00Z", "amount": 300, "latitude": 40.7128, "longitude": -74.0060},
        {"timestamp": "2025-05-29T10:00:00Z", "amount": -40, "latitude": 40.7129, "longitude": -74.0061},
        {"timestamp": "2025-05-29T11:00:00Z", "amount": 20, "latitude": 40.7130, "longitude": -74.0062},
        {"timestamp": "2025-05-29T12:00:00Z", "amount": -60, "latitude": 40.7131, "longitude": -74.0063},
        {"timestamp": "2025-05-29T13:00:00Z", "amount": 150, "latitude": 40.7132, "longitude": -74.0064},
        {"timestamp": "2025-05-29T14:00:00Z", "amount": -30, "latitude": 40.7133, "longitude": -74.0065},
        {"timestamp": "2025-05-29T15:00:00Z", "amount": 90, "latitude": 40.7134, "longitude": -74.0066},
        {"timestamp": "2025-05-29T16:00:00Z", "amount": -10, "latitude": 40.7135, "longitude": -74.0067},
        {"timestamp": "2025-05-29T17:00:00Z", "amount": 110, "latitude": 40.7136, "longitude": -74.0068},
        {"timestamp": "2025-05-29T18:00:00Z", "amount": -50, "latitude": 40.7137, "longitude": -74.0069},
    ]
}


# Define the tool that feches the last 10 transactions from a bank account
@tool("FetchLastTenTransactionsWIthLatAndLon")
def FetchLastTenTransactionsWithLatAndLon(bankNumber: int) -> list:
    """Fetches the last 10 transaction timestamps along with latitude and longitude 
    from the given bank account."""
    
    transactions = bank_transactions.get(bankNumber)
    
    if not transactions:
        return [f"No transactions found for bank number {bankNumber}."]
    
    # Return list of (timestamp, latitude, longitude)
    transaction_data = [
        (txn["timestamp"], txn["latitude"], txn["longitude"])
        for txn in transactions
    ]
    
    return transaction_data

# Define the tool that fetches the last 10 transactions with amount
@tool("FetchLastTenTransactionsWIthAmmount")
def FetchLastTenTransactionsWIthAmmount(bankNumber: int) -> list:
    """Fetches the last 10 transaction timestamps along with amounts 
    from the given bank account."""
    
    transactions = bank_transactions.get(bankNumber)
    
    if not transactions:
        return [f"No transactions found for bank number {bankNumber}."]
    
    # Return list of (timestamp, amount)
    transaction_data = [
        (txn["timestamp"], txn["amount"])
        for txn in transactions
    ]
    
    return transaction_data

# Define the Agent
fraud_detection_agent = Agent(
    role="fraud detection agent",
    goal=(
        "Given the last 10 transactions, determine if there is any fraudulent activity. "
        "Use both tools: "
        "`FetchLastTenTransactionsWithLatAndLon` for location-based detection and "
        "`FetchLastTenTransactionsWIthAmmount` for detecting anomalies in spending patterns. "
        "Each tool takes the bank number as input and returns transaction data."
    ),
    backstory=(
        "You are a skilled fraud detection agent. You identify unusual behavior by analyzing the "
        "time and geographic movement of transactions, and also identify unusual patterns in the transaction amounts. "
        "You can spot sudden jumps across cities or countries, or erratic spending patterns that deviate from the norm. "
        "If the bank number is incorrect or missing, simply state that the bank number is wrong."
    ),
    verbose=True,
    tools=[FetchLastTenTransactionsWithLatAndLon, FetchLastTenTransactionsWIthAmmount],
)

# Define the function that detects fraud by creating the task dynamically and running the agent
def DetectFraudOnBankNumber(bankNumber: int) -> float:
    # Define the Task
    task1 = Task(
        description=(
            f"Analyze the last 10 transactions for bank account {bankNumber}. "
            "Use both location and amount information. "
            "Use `FetchLastTenTransactionsWithLatAndLon` to analyze time and geographic location for suspicious movement "
            "(e.g., jumps between distant cities in a short time). "
            "Use `FetchLastTenTransactionsWIthAmmount` to detect abnormal spending behavior or irregular transaction amounts. "
            "Combine both analyses to determine fraud probability. "
            "Return only a probability value between 0 and 1, 0 is not fraud and 1 is fraud."
            "If bank number is invalid, respond with 'bank number is wrong'."
        ),
        expected_output="Just return the fraud probability value from 0 to 1. if bank number does not exist, simply say `bank number is wrong`'.",
        agent=fraud_detection_agent,
    )

    # Define the Crew
    crew = Crew(
        agents=[fraud_detection_agent],
        tasks=[task1],
        verbose=True
    )

    # Run the crew
    result = crew.kickoff()

    return result


# Example usage
if __name__ == "__main__":
    bank_number_input = input("Enter the bank number you want to check for fraud: ")
    try:
        bank_number = int(bank_number_input)
        result = DetectFraudOnBankNumber(bank_number)
        print(f"Fraud probability for bank number {bank_number}: {result}")
    except ValueError:
        print("something went wrong")