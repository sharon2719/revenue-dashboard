Revenue Recognition Dashboard
=============================

A comprehensive web-based dashboard for tracking and visualizing revenue recognition data, built with Flask, Google BigQuery, and Chart.js.

Features
--------

*   **Real-time Dashboard**: Live updates with automatic refresh every 5 minutes
    
*   **Interactive Charts**:
    
    *   Monthly revenue trend (line chart)
        
    *   Payment terms breakdown (doughnut chart)
        
    *   Top clients by revenue (bar chart)
        
*   **Summary Cards**: Key metrics at a glance
    
*   **Contract Details Table**: Detailed view of individual contracts with progress tracking
    
*   **Responsive Design**: Works on desktop and mobile devices
    

Screenshots
-----------

### Dashboard Overview

The main dashboard displays key revenue metrics and interactive charts.

### Key Metrics

*   Total Contracts
    
*   Recognized Revenue
    
*   Remaining Revenue
    
*   Recognition Rate
    

Technology Stack
----------------

*   **Backend**: Flask (Python)
    
*   **Frontend**: HTML5, CSS3, JavaScript (ES6+)
    
*   **Charts**: Chart.js
    
*   **Styling**: Bootstrap 5
    
*   **Icons**: Font Awesome
    
*   **Database**: Google BigQuery
    

Installation (Local Dev)
------------------------

### Prerequisites

*   Python 3.8+
    
*   pip
    
*   Google Cloud SDK (optional for local BQ access)
    
*   Service account with BigQuery access
    

### Setup Instructions

1.  **Clone the repository**
    

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   git clone   cd revenue-recognition-dashboard   `

1.  **Create and activate virtual environment**
    

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   python -m venv venv  source venv/bin/activate  # On Windows: venv\Scripts\activate   `

1.  **Install dependencies**
    

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   pip install -r requirements.txt   `

1.  **Set up environment variables**
    

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   cp .env.example .env  # Edit .env with your GCP project and credentials   `

1.  **Run the application**
    

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   python app.py   `

1.  **Open in browser**Navigate to http://localhost:8080
    

Deployment (Google Cloud Run)
-----------------------------

### Steps to Deploy via Console UI:

1.  Zip the project directory:
    

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   zip -r revenue-dashboard.zip .   `

1.  Go to [Google Cloud Run](https://console.cloud.google.com/run)
    
2.  Click **Create Service**
    
3.  Choose **Deploy from source** → Upload your revenue-dashboard.zip
    
4.  Set:
    

*   Runtime: Python
    
*   Entrypoint: gunicorn -b :$PORT app:app
    
*   Region: your preferred GCP region
    
*   Allow unauthenticated access (if public)
    

1.  Click **Deploy**
    
2.  Once deployed, access the dashboard at the provided URL (e.g. https://your-service.a.run.app)
    

Project Structure
-----------------

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   revenue-recognition-dashboard/  ├── app.py                 # Main Flask application  ├── requirements.txt       # Python dependencies  ├── .env.example           # Environment variables template  ├── README.md              # This file  ├── static/  │   ├── css/  │   │   └── dashboard.css  │   └── js/  │       └── dashboard.js  ├── templates/  │   └── dashboard.html  └── data/ (optional)   `

API Endpoints
-------------

The dashboard relies on the following BigQuery-powered endpoints:

### Summary Data

*   **GET** /api/summary
    
*   Returns overall revenue recognition statistics
    

### Chart Data

*   **GET** /api/payment\_terms
    
*   **GET** /api/top\_clients
    
*   **GET** /api/monthly\_trend
    
*   **GET** /api/contracts
    

Example API Response
--------------------

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   {    "total_contracts": 150,    "total_recognized_revenue": 2500000.00,    "total_remaining_revenue": 1200000.00,    "recognition_rate": 67.5  }   `

Configuration
-------------

### Environment Variables

Create a .env file and configure:

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   FLASK_ENV=development  FLASK_DEBUG=True  PORT=8080  GOOGLE_APPLICATION_CREDENTIALS=path/to/service_account.json  GCP_PROJECT_ID=your-gcp-project  BQ_DATASET=revenue_data   `

Usage
-----

### Dashboard Navigation

*   **Overview**: Main view with all charts and metrics
    
*   **Contracts**: Contract table with completion % and revenue breakdown
    

### Features

*   Auto-refresh every 5 minutes
    
*   Ctrl + R to refresh without browser reload
    
*   Responsive layout with chart resizing
    

Development
-----------

### Running Locally

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   export FLASK_ENV=development  python app.py   `

### Updating Charts or Logic

*   JavaScript updates → static/js/dashboard.js
    
*   CSS updates → static/css/dashboard.css
    
*   Backend logic → app.py
    

Debugging
---------

### Common Issues

*   API 500 errors: check BigQuery table existence
    
*   No charts: confirm DOM IDs and Chart.js setup
    
*   Styling issues: confirm Bootstrap and CSS links
    

Testing
-------

### Manual

*   Load http://localhost:8080
    
*   Confirm summary + charts load
    
*   Resize browser to check responsiveness
    

### API

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   curl http://localhost:8080/api/summary  curl http://localhost:8080/api/payment_terms   `

Future Enhancements
-------------------

*   Authentication support
    
*   Export charts/tables to CSV
    
*   Drill-down per client/contract
    
*   Real-time Firestore sync (optional)
    

License
-------

MIT License

Acknowledgments
---------------

*   Google Cloud BigQuery
    
*   Chart.js
    
*   Flask
    
*   Bootstrap
    
*   Font Awesome