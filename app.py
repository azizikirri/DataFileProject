from flask import Flask, render_template, request, make_response
from pymongo import MongoClient
import pandas as pd
from io import BytesIO
import re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import base64
from matplotlib import pyplot as plt
from jinja2 import Markup, escape

import seaborn as sns
#from tkinter import Tk
#import tkinter as tk 



app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['ExcelDaTa']
collection = db['ExcelDT']

def load_excel_data():
    try:
        # Check if data already exists in the collection
        if collection.count_documents({}) == 0:
            print("test")
            excel_data = pd.read_excel('datafile_soundages.xlsx')  # Use a relative path

            # Replace NaN values with 0 in the entire DataFrame
            excel_data.fillna(0, inplace=True)

            # Convert NaN values to 0 in the dictionary representation
            records = excel_data.where(pd.notna(excel_data), 0).to_dict(orient='records')

            collection.insert_many(records)
            print(excel_data.head())
    except Exception as e:
        print(f"Error reading Excel file: {e}")


load_excel_data()

@app.route('/')
def index():
    print("tt")
    return render_template('index.html')

@app.route('/search', methods=['POST'])

def search():
    try:
        
        place_name = request.form.get('place_name')
        print(f"Received Place Name in search route: {place_name}")

        # Creating a case-insensitive regular expression pattern
        regex_pattern = re.compile(f'^{re.escape(place_name)}$', re.IGNORECASE)

        # Using find to get a cursor and converting it to a list
        results = list(db.ExcelDT.find({'name': {'$regex': regex_pattern}}))

        print(results)

        if results:
            print(f"Results found: {results}")
            return render_template('search_result.html', results=results)
        else:
            print("No results found.")
            return render_template('search_result.html', results=None)
    except Exception as e:
        print(f"Error: {e}")
        return render_template('error.html', error=str(e))
# Add this route to app.py
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/show_all', methods=['GET'])
def show_all():
    try:
        # Retrieve all data from the collection
        all_data = list(collection.find())
        
        if all_data:
            return render_template('show_all.html', all_data=all_data)
        else:
            return render_template('show_all.html', all_data=None)
    except Exception as e:
        print(f"Error: {e}")
        return render_template('error.html', error=str(e))

@app.route('/show_graph', methods=['GET'])
def show_graph():
    try:
        # Retrieve all data from the collection
        all_data = list(collection.find())

        if all_data:
            # Extract data for the graph (assuming 'A' is a key in your MongoDB documents)
            x_values = [row['y'] for row in all_data]
            y_values = [row['x'] for row in all_data]

            # Create a line chart using seaborn with a legend
            plt.figure(figsize=(10, 6))
            sns.lineplot(x=x_values, y=y_values, marker='o', color='b', markersize=8, label='X vs Y')
            plt.xlabel('y', fontsize=14)
            plt.ylabel('x', fontsize=14)
            plt.title('All Data Graph of X in terms of Y', fontsize=16)
            plt.legend()  

            plt.tight_layout()

            # Save the plot to a BytesIO buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            graph_img = base64.b64encode(buffer.getvalue()).decode('utf-8')

            plt.close()  # Close the plot to free up resources

            return render_template('show_graph.html', graph_img=graph_img)
        else:
            return render_template('show_graph.html', graph_img=None)
    except Exception as e:
        print(f"Error: {e}")
        return render_template('error.html', error=str(e))



@app.route('/show_specific_graph/<name>', methods=['GET'])
def show_specific_graph(name):
    try:
        # Search for data by name
        specific_data = list(collection.find({'name': name}))

        if specific_data:
            # Extract data for the graph (assuming 'A' and 'B' are keys in your MongoDB documents)
            x_values = [row['x'] for row in specific_data]
            y_values = [row['y'] for row in specific_data]

            # Create a line chart using seaborn with a legend
            plt.figure(figsize=(10, 6))
            sns.lineplot(x=x_values, y=y_values, marker='o', color='b', markersize=8, label='X vs Y')
            plt.xlabel('x', fontsize=14)
            plt.ylabel('y', fontsize=14)
            plt.title(f'Line Chart for {name}', fontsize=16)
            plt.legend()  # Add legend

            plt.tight_layout()

            # Save the plot to a BytesIO buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            graph_img = base64.b64encode(buffer.getvalue()).decode('utf-8')

            plt.close()  # Close the plot to free up resources

            return render_template('show_graph.html', graph_img=graph_img)
        else:
            return render_template('show_graph.html', graph_img=None)
    except Exception as e:
        print(f"Error: {e}")
        return render_template('error.html', error=str(e))




@app.route('/download_specific_pdf/<name>')
def download_specific_pdf(name):
    try:
        # Search for data by name
        specific_data = list(collection.find({'name': name}))

        if specific_data:
            # Create a BytesIO buffer to store the PDF
            buffer = BytesIO()

            # Create PDF report using reportlab with a table
            pdf = SimpleDocTemplate(buffer, pagesize=letter)
            data = [['Name', 'Localites', 'N° IRE', 'X', 'Y', 'PT SOL', 'Q', 'K']]
            for row in specific_data:
                data.append([row['name'], row['localites'], row['n_ire'], row['x'], row['y'], row['pt_sol'], row['q'], row['k']])

            # Create the table and set style
            table = Table(data)
            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ])
            table.setStyle(style)

            # Build PDF document
            pdf.build([table])

            # Move the buffer position to the beginning
            buffer.seek(0)

            # Create a response to send the PDF file
            response = make_response(buffer.read())
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename={name}_report.pdf'

            return response
        else:
            return render_template('error.html', error=f"No data found for {name}")
    except Exception as e:
        print(f"Error: {e}")
        return render_template('error.html', error=str(e))




@app.route('/download_pdf')
def download_pdf():
    try:
        #search_name = request.args.get('name')
        #search_name = request.args.get('place_name')
        
        
        search_name = request.form.get('place_name')
        print(f"Received Search Name in download_pdf route: {search_name}")

        # Check if 'name' parameter is present in the request
        search_name = request.form.get('place_name')
        if search_name:
            
            # Search for data by name
            specific_data = list(collection.find({'name': search_name}))

            if specific_data:
                # Create a BytesIO buffer to store the PDF
                buffer = BytesIO()

                # Create PDF report using reportlab with a table
                pdf = SimpleDocTemplate(buffer, pagesize=letter)
                data = [['Name', 'Localites', 'N° IRE', 'X', 'Y', 'PT SOL', 'Q', 'K']]
                for row in specific_data:
                    data.append([row['name'], row['localites'], row['n_ire'], row['x'], row['y'], row['pt_sol'], row['q'], row['k']])

                # Create the table and set style
                table = Table(data)
                style = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ])
                table.setStyle(style)

                # Build PDF document
                pdf.build([table])

                # Move the buffer position to the beginning
                buffer.seek(0)

                # Create a response to send the PDF file
                response = make_response(buffer.read())
                response.headers['Content-Type'] = 'application/pdf'
                response.headers['Content-Disposition'] = f'attachment; filename={search_name}_report.pdf'

                return response
            else:
                return render_template('search_result.html', search_name=search_name, specific_data=None)
        else:
            # Download all data
            all_data = list(collection.find())

            if all_data:
                # Create a BytesIO buffer to store the PDF
                buffer = BytesIO()

                # Create PDF report using reportlab with a table
                pdf = SimpleDocTemplate(buffer, pagesize=letter)
                data = [['Name', 'Localites', 'N° IRE', 'X', 'Y', 'PT SOL', 'Q', 'K']]
                for row in all_data:
                    data.append([row['name'], row['localites'], row['n_ire'], row['x'], row['y'], row['pt_sol'], row['q'], row['k']])

                # Create the table and set style
                table = Table(data)
                style = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ])
                table.setStyle(style)

                # Build PDF document
                pdf.build([table])

                # Move the buffer position to the beginning
                buffer.seek(0)

                # Create a response to send the PDF file
                response = make_response(buffer.read())
                response.headers['Content-Type'] = 'application/pdf'
                response.headers['Content-Disposition'] = 'attachment; filename=report.pdf'

                return response
            else:
                return render_template('show_all.html', all_data=None)
    except Exception as e:
        print(f"Error: {e}")
        return render_template('error.html', error=str(e))




if __name__ == '__main__':
    #root = tk.Tk()  # Create an instance of Tk
    #root.mainloop()  # Run the Tkinter main loop

    app.run(debug=True )