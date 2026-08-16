import pandas as pd
from pathlib import Path
from scripts.extraction import extraction

CLEANED_DATA_DIR = Path(__file__).resolve().parent.parent / "dataset" / "cleaned_data"

def transformation():

    # Extract the raw data into a DataFrame
    data = extraction()

    # Remove duplicates
    data.drop_duplicates(inplace=True)

    # Handling missing values (Example: fill missing numeric values with the mean or median)
    numeric_columns = data.select_dtypes(include=['float64', 'int64']).columns
    for col in numeric_columns:
        # data[col].fillna(data[col].mean(), inplace=True)
        data.fillna({col: data[col].mean()}, inplace=True)

    # Handling missing values (Example: fill missing string values with 'Unknown')
    string_columns = data.select_dtypes(include=['object']).columns
    for col in string_columns:
        # data[col].fillna('Unknown', inplace=True)
        data.fillna({col: 'Unknown'}, inplace=True)

    # Create Products Table
    products = data[['ProductName', 'UnitPrice']].drop_duplicates().reset_index(drop=True)
    products.index.name = 'ProductID'
    products = products.reset_index()

    # Create Customers Table
    customers = data[['CustomerName', 'CustomerAddress', 'Customer_PhoneNumber', 'CustomerEmail']].drop_duplicates().reset_index(drop=True)
    customers.index.name = 'CustomerID'
    customers = customers.reset_index()

    # Create Staff Table
    staff = data[['Staff_Name', 'Staff_Email']].drop_duplicates().reset_index(drop=True)
    staff.index.name = 'StaffID'
    staff = staff.reset_index()

    # Create Transaction Table
    transactions = data.merge(products, on = ['ProductName', 'UnitPrice'], how='left') \
                    .merge(customers, on = ['CustomerName', 'CustomerAddress', 'Customer_PhoneNumber', 'CustomerEmail'], how='left') \
                    .merge(staff, on= ['Staff_Name', 'Staff_Email'], how='left')
    transactions.index.name = 'TransactionID'
    transactions = transactions.reset_index() \
                            [['TransactionID', 'Date', 'ProductID', 'CustomerID', 'StaffID', 'Quantity', 'StoreLocation', 'PaymentType', \
                                    'PromotionApplied', 'Weather', 'Temperature', 'StaffPerformanceRating', 'CustomerFeedback', \
                                    'DeliveryTime_min', 'OrderType', 'DayOfWeek', 'TotalSales']]

    # Ensure the output directory exists
    CLEANED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Save normalized tables to new CSV files
    data.to_csv(CLEANED_DATA_DIR / "clean_data.csv", index=False)
    products.to_csv(CLEANED_DATA_DIR / "products.csv", index=False)
    customers.to_csv(CLEANED_DATA_DIR / "customers.csv", index=False)
    staff.to_csv(CLEANED_DATA_DIR / "staff.csv", index=False)
    transactions.to_csv(CLEANED_DATA_DIR / "transactions.csv", index=False)


def read_clean_data():
    try:
            products = pd.read_csv(CLEANED_DATA_DIR/'products.csv')
            customers = pd.read_csv(CLEANED_DATA_DIR/'customers.csv')
            staff = pd.read_csv(CLEANED_DATA_DIR/'staff.csv')
            transactions = pd.read_csv(CLEANED_DATA_DIR/'transactions.csv')
            print("Data read successfully!")
            return products, customers, staff, transactions
    except Exception as e:
            print(f"An error occurred: {e}")
            raise


if __name__ == "__main__":
    transformation()
    read_clean_data()
