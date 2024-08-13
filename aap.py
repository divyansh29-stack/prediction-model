import pandas as pd

# Load the Excel file (consider using environment variables or configuration files)
DATA_PATH = r'c:\ai ml\Jan2023 to May2024 Data for Analysis 1.xlsx'


def load_data():
    """Loads and preprocesses data efficiently, ensuring reusability.

    Handles potential file path issues and returns None if data cannot be loaded.
    """
    try:
        df = pd.read_excel(r'c:\ai ml\Jan2023 to May2024 Data for Analysis 1.xlsx', sheet_name='Tabular Reports')
        df = df.fillna('Unknown')  # Handle missing values
        requester_category_counts = df.groupby(['Requester', 'Category']).size().unstack(fill_value=0)
        return requester_category_counts
    except FileNotFoundError:
        print("Error: Data file not found.")
        return None


def predict_fail_category(requester_name, data):
    """Predicts the category with the most likely failure for a requester.

    Checks if the requester exists in the data and returns appropriate messages.
    Returns a dictionary containing prediction details.
    """

    if requester_name not in data.index:
        return {
            'Requester': requester_name,
            'Complaint Counts': None,
            'Most Likely to Fail First': None,
            'Number of Complaints': 0
        }

    requester_data = data.loc[requester_name]
    sorted_categories = requester_data.sort_values(ascending=False)
    most_failed_category = sorted_categories.idxmax()
    max_complaints = sorted_categories.max()

    return {
        'Requester': requester_name,
        'Complaint Counts': requester_data.to_dict(),
        'Most Likely to Fail First': most_failed_category,
        'Number of Complaints': max_complaints
    }


from flask import Flask, request, jsonify
from waitress import serve

app = Flask(__name__)

# Load data outside of the route for efficiency (consider caching)
requester_category_counts = load_data()


@app.route('/predict', methods=['GET'])
def predict():
    requester_name = request.args.get('requester')

    if not requester_name:
        return jsonify({'error': 'Please provide a requester name.'}), 400  # Bad Request

    if requester_category_counts is None:
        return jsonify({'error': 'Failed to load data.'}), 500  # Internal Server Error

    prediction = predict_fail_category(requester_name, requester_category_counts)
    return jsonify(prediction)


if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8080, threads=4) # Corrected typo: threads (not thread)

