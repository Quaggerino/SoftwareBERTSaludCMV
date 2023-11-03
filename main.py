import tkinter as tk
import database as database
import classifier
from tkinter import ttk
from tkcalendar import DateEntry 
from datetime import datetime, timedelta
import re
from openpyxl.utils import get_column_letter
import pandas as pd
from tkinter.filedialog import asksaveasfilename



def open_data_window():
    data_window = tk.Tk()
    data_window.geometry("1000x768")
    data_window.title("Explorar datos")

    # Apply the Azure theme
    data_window.tk.call("source", "azure.tcl")
    data_window.tk.call("set_theme", "dark")

    table_columns = ('ID', 'Edad', 'Género', 'Centro de Salud', 'Frecuencia', 'Satisfacción', 'Recomendación', 'Comentario Abierto', 'Fecha', 'Etiqueta')

    dropdown_columns = ('Edad', 'Género', 'Centro de Salud', 'Frecuencia', 'Satisfacción', 'Recomendación', 'Comentario Abierto', 'Fecha', 'Etiqueta')


    search_label = ttk.Label(data_window, text="Search:")
    search_label.grid(row=0, column=0, padx=5, pady=5)

    column_options = ['All'] + list(dropdown_columns)  # Use dropdown_columns for the dropdown options
    selected_column = tk.StringVar()
    selected_column.set('All')
    column_selector = ttk.Combobox(data_window, textvariable=selected_column, values=column_options, width=20)
    column_selector.grid(row=0, column=1, padx=5, pady=5)

    search_entry = ttk.Entry(data_window, width=60)
    search_entry.grid(row=0, column=2, padx=5, pady=5, sticky='ew')

    search_button = ttk.Button(data_window, text="Search", command=lambda: search_data(search_entry.get(), selected_column.get()))
    search_button.grid(row=0, column=3, padx=5, pady=5)

    result_tree = ttk.Treeview(data_window, columns=table_columns, show='headings', height=15)
    result_tree.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky='nsew')

    for column in table_columns:  # Use table_columns for the table headers
        result_tree.heading(column, text=column)
        result_tree.column(column, width=len(column) * 10)


    detail_text = tk.Text(data_window, wrap='word', height=15)
    detail_text.grid(row=2, column=0, columnspan=4, padx=5, pady=5, sticky='nsew')

    def update_selected_column(event):
        selected_column.set(column_selector.get())
        print(f"Column selected: {selected_column.get()}")  # This line is for debugging, you can remove it later

    # Binding the update_selected_column function to the <<ComboboxSelected>> event
    column_selector.bind('<<ComboboxSelected>>', update_selected_column)


    def on_row_selected(event):
        selected_items = result_tree.selection()
        if selected_items:
            selected_item = selected_items[0]
            details = result_tree.item(selected_item, 'values')
            detail_text.delete('1.0', tk.END)
            for i, detail in enumerate(details):
                detail_text.insert(tk.END, f"{table_columns[i]}: {detail}\n")

    result_tree.bind('<<TreeviewSelect>>', on_row_selected)

    def preprocess_query(query, column):
        column = column.lower()  # Convert the selected column to lowercase
        query = query.lower()  # Convert the query to lowercase for case-insensitive matching

        
        # Now, use the lowercase version of the column name in the comparisons
        if column in ['edad', 'satisfacción', 'recomendación']:
            try:
                return int(query)
            except ValueError:
                return query
            
        elif column == 'etiqueta':
            target_texts = {
                'irrelevante': 0,
                'negativo': 1,
                'positivo': 2,
                'sin clasificar': 3
            }

            # Check if the query matches (even partially) any of the target texts
            matched_key = next((key for key in target_texts if query.lower() in key), None)

            # If there's a match, return the corresponding integer value
            if matched_key:
                return target_texts[matched_key]

            # If no match, return a regex pattern for a partial match
            else:
                regex_pattern = {"$regex": f"{query}", "$options": 'i'}
                return regex_pattern

        elif column == 'ID':
            # If the query is empty, return a match-all pattern
            if not query:
                return {}
            
            # Use a regex pattern for partial match of ObjectId string
            regex_pattern = {"_id": {"$regex": f"{query}", "$options": 'i'}}
            return regex_pattern
        
        elif column == 'fecha':
            month_names_english = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
            month_names_spanish = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
            
            # If the query is empty, return all documents
            if not query:
                return {}
            
            # Try extracting day, month, and year using regex in the format day-month-year or day/month/year
            date_match = re.search(r'(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})', query, re.IGNORECASE)
            if date_match:
                day = int(date_match.group(1))
                month = int(date_match.group(2))
                year = int(date_match.group(3))
                
                # Adjust the year if it is given in a two-digit format
                if year < 100:
                    year += 2000  # Assuming the year is in the 21st century
                
                start_time = datetime(year, month, day)
                end_time = start_time + timedelta(days=1)  # Add one day to get to the end of the day
                
                return {"$gte": start_time, "$lt": end_time}

            # Try to match the query with only a year format, e.g., "2023"
            year_match = re.search(r'^(del\s+)?(\d{4})$', query, re.IGNORECASE)
            if year_match:
                year = int(year_match.group(2))
                start_time = datetime(year, 1, 1)
                end_time = datetime(year+1, 1, 1)
                return {"$gte": start_time, "$lt": end_time}

            month_year_match = re.search(r'^([\w]+)\s+(\d{4})$', query, re.IGNORECASE)
            if month_year_match:
                month_name = month_year_match.group(1).lower()
                year = int(month_year_match.group(2))
                if month_name in month_names_english:
                    month_index = month_names_english.index(month_name)
                elif month_name in month_names_spanish:
                    month_index = month_names_spanish.index(month_name)
                else:
                    return None
                
                start_date = datetime(year, month_index+1, 1)
                end_date = datetime(year, month_index+2, 1) if month_index < 11 else datetime(year+1, 1, 1)
                return {"$gte": start_date, "$lt": end_date}

            # Parse day-month-year format
            # Try extracting day, month, and potentially year using regex
            day_month_year_match = re.search(r'(\d{1,2})\s+(?:de\s+)?([\w]+)(?:\s+(\d{4}))?', query, re.IGNORECASE)
            if day_month_year_match:
                day = int(day_month_year_match.group(1))
                month = day_month_year_match.group(2).lower()
                year = int(day_month_year_match.group(3)) if day_month_year_match.group(3) else datetime.now().year

                if month in month_names_english:
                    month_num = month_names_english.index(month) + 1
                elif month in month_names_spanish:
                    month_num = month_names_spanish.index(month) + 1
                else:
                    return None

                start_time = datetime(year, month_num, day)
                end_time = start_time + timedelta(days=1)  # Add one day to get to the end of the day

                return {"$gte": start_time, "$lt": end_time}
            
            for month_name in month_names_english + month_names_spanish:
                try:
                    # Handling formats like "27 de Octubre 2023" or "27 Octubre 2023"
                    parsed_date = datetime.strptime(query, f"%d de? {month_name} %Y")
                    return {"$eq": parsed_date}
                except ValueError:
                    try:
                        # Handling formats like "27 de Octubre" or "27 Octubre"
                        parsed_date = datetime.strptime(query, f"%d de? {month_name}")
                        return {"$eq": parsed_date}
                    except ValueError:
                        continue
            
            # Try to detect the month from the query
            month_index = None
            if query.lower() in month_names_english:
                month_index = month_names_english.index(query.lower())
            elif query.lower() in month_names_spanish:
                month_index = month_names_spanish.index(query.lower())
            
            if month_index is not None:
                current_year = datetime.now().year
                start_date = datetime(current_year, month_index + 1, 1)
                
                if month_index == 11:  # December
                    end_date = datetime(current_year + 1, 1, 1)  # January of the next year
                else:
                    end_date = datetime(current_year, month_index + 2, 1)  # First day of the next month
                    
                return {"$gte": start_date, "$lt": end_date}

            # If unable to detect the month or any other format, return None
            return None

        else:
            return query



    def search_data(query, column):
        processed_query = preprocess_query(query, column)
        for row in result_tree.get_children():
            result_tree.delete(row)
        
        print(f"Searching for query: '{query}' in column: '{column}' (Processed: '{processed_query}')")  # Debug print
        
        # Check if the search box is empty
        if not query.strip():
            results = database.get_all_documents()  # Retrieve all documents if search box is empty
        else:
            results = database.search_documents(processed_query, column)  # Passing processed_query here
        
        print(f"Results: {results}")  # Debug print
        
        if results:  # Check if results are not None or empty
            for result in results:
                target_text = target_number_to_text(result['target'])
                result_tree.insert('', tk.END, values=(result['_id'], result['edad'], result['genero'], result['cesfam'],
                                                    result['frecuencia'], result['satisfaccion'], result['recomendacion'],
                                                    result['razon'], result['date'], target_text))



    def target_number_to_text(target_number):
        target_texts = {
            0: 'Irrelevante',
            1: 'Negativo',
            2: 'Positivo',
            3: 'Sin clasificar'
        }
        return target_texts.get(target_number, 'Unknown')
    
    def save_to_excel():
        # Retrieve data from the table
        rows = result_tree.get_children()
        data = []
        for row in rows:
            row_data = result_tree.item(row, 'values')
            data.append(row_data)

        # Convert the data to a pandas DataFrame
        df = pd.DataFrame(data, columns=table_columns)

        # Prompt the user for a save location
        file_name = asksaveasfilename(title="Save as", defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        
        if file_name:
            # Save the DataFrame to Excel format
            df.to_excel(file_name, index=False, engine='openpyxl')

        tk.messagebox.showinfo("Information", f"Data saved to {file_name}")

    # Add a button to trigger the save_to_excel function
    save_button = ttk.Button(data_window, text="Exportar Excel", command=save_to_excel)
    save_button.grid(row=3, column=3, padx=5, pady=5)  # Adjust the row and column as needed



    data_window.grid_columnconfigure(2, weight=1)
    data_window.grid_rowconfigure(2, weight=1)

    data_window.mainloop()



app = tk.Tk()  
app.geometry("420x280")
app.title("Clasificador de Datos")
app.iconbitmap('logo.ico')
app.minsize(420, 280)


# Apply the Azure theme
app.tk.call("source", "azure.tcl")
app.tk.call("set_theme", "dark")

total_docs_label = ttk.Label(app)
total_docs_label.grid(row=0, column=0, padx=20, pady=20, sticky='w')

uncategorized_docs_label = ttk.Label(app)
uncategorized_docs_label.grid(row=1, column=0, padx=20, pady=20, sticky='w')

classify_button = ttk.Button(app, text="Clasificar datos", command=lambda: classify_and_update())
classify_button.grid(row=0, column=1, padx=20, pady=20, sticky='ew')

view_data_button = ttk.Button(app, text="Explorar datos", command=open_data_window)
view_data_button.grid(row=1, column=1, padx=20, pady=20, sticky='ew')

reset_targets_button = ttk.Button(app, text="Restaurar etiqueta de los datos", command=lambda: reset_all_targets_to_3())
reset_targets_button.grid(row=2, column=0, columnspan=2, padx=20, pady=20, sticky='ew')

last_updated_label = ttk.Label(app, anchor='center')  # Setting text alignment to center
last_updated_label.grid(row=3, column=0, columnspan=2, padx=20, pady=20, sticky='ew')  # Making the label expand horizontally

# Ensure that the columns expand as the window is resized
app.grid_columnconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=1)

# Adjust the row weights. Rows containing buttons will have a weight of 0.
app.grid_rowconfigure(0, weight=0)  # Rows with buttons get a weight of 0
app.grid_rowconfigure(1, weight=0)  # Rows with buttons get a weight of 0
app.grid_rowconfigure(2, weight=0)  # Rows with buttons get a weight of 0
app.grid_rowconfigure(3, weight=0)  # Adjust as per your design
app.grid_rowconfigure(4, weight=0)  # Adjust as per your design

def reset_all_targets_to_3():
    database.reset_all_targets_to_3()  # Update all targets to 3
    refresh_stats() 


def update_database():
    num_updated = 0  # Initialize the count of updated documents
    documents = database.get_documents()
    for doc in documents:
        razon_text = doc['razon']
        predicted_target = classifier.classify_text(razon_text)
        database.update_target(doc['_id'], predicted_target)
        num_updated += 1  # Increment the count for each updated document

    return num_updated  # Return the count of updated documents

# Declare num_updated_label as a global variable.
num_updated_label = ttk.Label(app, anchor='center')
num_updated_label.grid(row=4, column=0, columnspan=2, padx=20, pady=2, sticky='ew')

# Define the function to update num_updated_label based on the latest data.
def update_num_updated_label():
    last_log = database.get_last_log()  # Get the latest log
    if last_log:
        num_updated_label.configure(text=f"Datos clasificados: {last_log['num_updated']} datos")

def initialize_last_updated_label():
    last_log = database.get_last_log()
    if last_log:
        formatted_date = str(last_log['date']).split('.')[0]  # Convert to string and remove milliseconds
        # Set the last_updated_label text to show the last execution date.
        last_updated_label.configure(text=f"Última ejecución: {formatted_date}")
        last_updated_label.grid(row=3, column=0, columnspan=2, padx=20, pady=2, sticky='ew')
        
        # Call update_num_updated_label to set the text of num_updated_label.
        update_num_updated_label()
    else:
        last_updated_label.configure(text="No hay logs disponibles.")
        last_updated_label.grid(row=3, column=0, columnspan=2, padx=20, pady=2, sticky='ew')

        last_updated_label.grid(row=3, column=0, columnspan=2, padx=20, pady=2, sticky='ew')


# Initialize the last updated label when the app is opened
initialize_last_updated_label()

def classify_and_update():
    num_updated = update_database()
    database.log_update(num_updated)
    last_log = database.get_last_log()
    last_updated_label.configure(text=f"Última ejecución: {str(last_log['date']).split('.')[0]}")
    refresh_stats()
    

def refresh_stats():
    total_docs_label.configure(text=f"Datos totales: {database.get_total_documents()}")
    uncategorized_docs_label.configure(text=f"Datos sin clasificar: {database.get_uncategorized_documents()}")
    initialize_last_updated_label()




# Initialize the stats on the GUI
refresh_stats()


app.mainloop()

