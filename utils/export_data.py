import csv
from datetime import datetime


def export_transactions(transactions, file_path=None):
    """
    Export transaction data to a CSV file.
    
    Args:
        transactions (list): List of transaction dictionaries to export
        file_path (str, optional): Path where the CSV will be saved. If None, a timestamped filename will be generated.
                                   
    Returns:
        tuple: (success, message)
            - success (bool): True if export was successful, False otherwise
            - message (str): File path if successful, error message if failed
    """
    if not file_path:
        # Generate timestamped filename if none provided
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"transactions_export_{timestamp}.csv"

    try:
        with open(file_path, "w", newline="") as file:
            if not transactions:
                return False, "No transactions to export"

            # Write transactions to CSV
            fieldnames = transactions[0].keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(transactions)

            return True, file_path
    except FileNotFoundError:
        return False, f"Error: The directory for '{file_path}' does not exist."

    except PermissionError:
        return False, f"Error: Permission denied to write to '{file_path}'."

    except Exception as e:
        return False, f"Error exporting transactions: {e.__class__.__name__}: {str(e)}"
