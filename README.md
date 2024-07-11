# Apple Watch Data Analysis Dashboard

This repository contains a Plotly Dash dashboard for analyzing Apple Watch data exported as XML files. The dashboard provides insights into personal information, heart rate, activity, and sleep patterns. Users can upload their XML files, visualize the data, and download the processed data as CSV.

## Features

- **Upload XML Files**: Upload your Apple Watch XML data file to start the analysis.
- **Personal Information**: View your personal information extracted from the XML file.
- **Heart Rate Analysis**: Visualize your heart rate data with various graphs.
- **Activity Analysis**: See detailed activity data including steps, calories burned, and more.
- **Sleep Analysis**: Analyze your sleep patterns with comprehensive graphs.
- **Download CSV**: Download the processed data as a CSV file for further analysis.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/apple-watch-dashboard.git
    ```
2. Navigate to the project directory:
    ```sh
    cd apple-watch-dashboard
    ```
3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```
4. Run the dashboard:
    ```sh
    python app.py
    ```

## Usage

### Upload XML File

![Upload XML File](images/upload.png)

Navigate to the "Upload" tab to upload your Apple Watch XML file. Once uploaded, the progress bar will update and indicate the upload status.

### Personal Information

![Personal Information](images/personal_info.png)

The "Personal Information" tab displays personal data extracted from the XML file, such as age, weight, height, etc.

### Heart Rate Analysis

![Heart Rate Analysis](images/heart_rate.png)

The "Heart Rate" tab provides various graphs to visualize heart rate data over time.

### Activity Analysis

![Activity Analysis](images/activity.png)

In the "Activity" tab, you can view detailed activity data including steps taken, calories burned, and more.

### Sleep Analysis

![Sleep Analysis](images/sleep.png)

The "Sleep Analysis" tab shows your sleep patterns and provides comprehensive graphs for better understanding.

### Download CSV

![Download CSV](images/download_csv.png)

Finally, the "Download CSV" tab allows you to download the processed data as a CSV file for further analysis.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
