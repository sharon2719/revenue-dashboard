# Revenue Recognition Dashboard

A comprehensive web-based dashboard for tracking and visualizing revenue recognition data, built with Flask, Google BigQuery, and Chart.js.

## ✨ Features

* **Real-time Dashboard**: Live updates with automatic refresh capabilities.
* **Interactive Charts**: Visualize data with:
    * Monthly revenue trends (line chart)
    * Payment terms breakdown (doughnut chart)
    * Top clients by revenue (bar chart)
* **Summary Cards**: Key financial metrics at a glance.
* **Contract Details Table**: Detailed view of individual contracts with progress tracking.
* **Responsive Design**: Optimized for both desktop and mobile devices.

## 📊 Key Metrics

The dashboard prominently displays:

* Total Contracts
* Recognized Revenue
* Remaining Revenue
* Recognition Rate

## 💻 Technology Stack

* **Backend**: Flask (Python)
* **Frontend**: HTML5, CSS3, JavaScript (ES6+)
* **Charts**: Chart.js
* **Styling**: Bootstrap 5
* **Icons**: Font Awesome
* **Database**: Google BigQuery

## ☁️ Deployment

This dashboard is deployed on **Google Cloud Run** for serverless scalability and cost-efficiency.

### API Endpoints

The dashboard retrieves data via the following BigQuery-powered Flask API endpoints:

* `GET /api/summary`
* `GET /api/payment_terms`
* `GET /api/top_clients`
* `GET /api/monthly_trend`
* `GET /api/contracts`
* `GET /api/refresh_revenue_table` (to trigger a data refresh in BigQuery)

## ⚙️ Configuration (for Developers)

To run or deploy this application, the following environment variables are typically used:

* `FLASK_ENV`: e.g., `production` or `development`
* `PORT`: The port Flask listens on (e.g., `8080`)
* `GOOGLE_CLOUD_PROJECT`: Your Google Cloud Project ID.
* `GOOGLE_APPLICATION_CREDENTIALS`: (Local development) Path to your BigQuery service account JSON key.
* `BQ_DATASET`: Your BigQuery dataset name (e.g., `revenue_data`).

## 🛠️ Usage

### Dashboard Navigation

* **Overview**: The main view with all charts and metrics.
* **Contracts**: A detailed table of individual contracts.

### Features

* Auto-refresh every 5 minutes ensures data is current.
* Responsive layout adapts to different screen sizes.

## 💡 Future Enhancements

* Implementing robust authentication and authorization.
* Adding data export functionality for charts and tables (e.g., to CSV).
* Enabling drill-down capabilities for client and contract specific data.
* Integrating real-time data synchronization.

## 📄 License

This project is licensed under the MIT License.

## 🙌 Acknowledgments

* Google Cloud BigQuery
* Chart.js
* Flask
* Bootstrap
* Font Awesome
