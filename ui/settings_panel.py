import customtkinter as ctk
from tkinter import messagebox, filedialog
from database.models import Settings
from core.analytics import FinancialAnalytics
from utils.export_data import export_transactions


class SettingsPanel(ctk.CTkFrame):
    """
    A panel for managing application settings and exporting data.
    
    This class provides a user interface for changing application theme
    and exporting transaction data to CSV files.
    
    Attributes:
        settings: The application settings object from the database
        refresh_callback: A callback function to refresh the main UI when settings change
        analytics: An instance of FinancialAnalytics for accessing transaction data
    """

    def __init__(self, parent, refresh_callback=None):
        super().__init__(parent)

        # Load current settings from database
        self.settings = Settings.select().first()
        self.refresh_callback = refresh_callback
        self.analytics = FinancialAnalytics()

        # Configure the frame appearance
        self.configure(fg_color="transparent")

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Set up UI components
        self.setup_settings_panel()

    def setup_settings_panel(self):
        """
        Set up all UI components for the settings panel.
        
        Creates frames for theme settings and data export options.
        """
        # Main container frame
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        # Title label
        title_label = ctk.CTkLabel(main_frame, text="Application Settings", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=(20, 30))

        # Theme selection section
        theme_frame = ctk.CTkFrame(main_frame)
        theme_frame.pack(fill="x", pady=10)

        theme_label = ctk.CTkLabel(theme_frame, text="Application Theme", font=ctk.CTkFont(size=16, weight="bold"))
        theme_label.pack(anchor="w", padx=15, pady=(10, 5))

        theme_hint = ctk.CTkLabel(theme_frame, text="Toggle between Light and Dark theme", text_color="#9E9E9E")
        theme_hint.pack(anchor="w", padx=15, pady=(0, 10))

        self.current_theme_label = ctk.CTkLabel(theme_frame, text=f"Current Theme: {self.settings.theme}")
        self.current_theme_label.pack(anchor="w", padx=15, pady=(0, 10))

        self.theme_var = ctk.StringVar(value=self.settings.theme)

        theme_button = ctk.CTkButton(theme_frame, text="Toggle Theme", command=self.toggle_theme)
        theme_button.pack(fill="x", padx=15, pady=(0, 15))

        # Data export section
        export_frame = ctk.CTkFrame(main_frame)
        export_frame.pack(fill="x", pady=10)

        export_label = ctk.CTkLabel(export_frame, text="Data Export", font=ctk.CTkFont(size=16, weight="bold"))
        export_label.pack(anchor="w", padx=15, pady=(10, 5))

        export_hint = ctk.CTkLabel(export_frame, text="Export all transactions to a CSV file", text_color="#9E9E9E")
        export_hint.pack(anchor="w", padx=15, pady=(0, 10))

        export_button = ctk.CTkButton(export_frame, text="Export Transactions", command=self.export_transactions, fg_color="#4CAF50")
        export_button.pack(fill="x", padx=15, pady=(0, 15))

    def toggle_theme(self):
        """
        Toggle between Light and Dark themes.
        
        Updates the theme setting in the database and refreshes the UI.
        Shows a confirmation message to the user.
        """
        # Toggle theme value
        new_theme = "Dark" if self.theme_var.get() == "Light" else "Light"
        self.theme_var.set(new_theme)
        ctk.set_appearance_mode(new_theme)

        # Save the new theme setting to the database
        self.settings.theme = new_theme
        self.settings.save()

        # Update the UI to reflect the new theme
        self.current_theme_label.configure(text=f"Current Theme: {new_theme}")

        # Call the refresh callback if provided
        if self.refresh_callback:
            self.refresh_callback()

        # Show confirmation message
        messagebox.showinfo("Success", f"Theme changed to {new_theme}")

    def export_transactions(self):
        """
        Export all transactions to a CSV file.
        
        Retrieves transaction data using the analytics module,
        prompts the user for a save location, and exports the data.
        Shows error messages if the export fails.
        """
        try:
            # Get all transactions without limit
            df = self.analytics.get_transaction_history(limit=None) 

            # Check if there are transactions to export
            if df.empty:
                messagebox.showinfo("Export Transactions", "No transactions to export")
                return

            # Format transactions for export
            transactions = []
            for _, row in df.iterrows():
                date_str = row['date'].strftime("%Y-%m-%d")

                transaction = {
                    'Date': date_str,
                    'Category': row['category'],
                    'Description': row['description'] or "",
                    'Amount': f"{row['amount']:.2f}",
                    'Type': "Income" if row['is_income'] else "Expense"
                }
                transactions.append(transaction)

            # Prompt user for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export Transactions"
            )

            # Return if user cancels the dialog
            if not file_path:  
                return

            # Export the transactions to the selected file
            success, result = export_transactions(transactions, file_path)

            # Show appropriate message based on export result
            if success:
                messagebox.showinfo("Export Successful", f"Transactions exported to:\n{result}")
            else:
                messagebox.showerror("Export Failed", result)

        except Exception as e:
            # Show error message if export fails
            messagebox.showerror("Export Error", f"An error occurred while exporting: {str(e)}")
