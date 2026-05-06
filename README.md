# Setup and Run Guide

This project is an Adversarial EDA proof of concept. It accepts a CSV dataset, runs an AI-assisted exploratory data analysis pipeline, and returns a PDF report.

## Prerequisites

- Git
- Conda or Miniconda
- A Google Generative AI API key
- Python 3.12, provided by the conda environment in `environment.yml`

## 1. Clone and Enter the Project

```powershell
git clone https://github.com/VishalReddy2011/adversarial-eda
cd adversarial-eda
```

## 2. Create the Conda Environment

Create the environment from the checked-in `environment.yml` file:

```powershell
conda env create -f environment.yml
```

Activate it:

```powershell
conda activate dap
```

## 3. Configure Environment Variables

Create a `.env` file in the project root if it does not already exist:

Add the required Google API configuration:

```env
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_MODEL=gemini-3-flash-preview
GOOGLE_TEMPERATURE=0.2
```

`GOOGLE_API_KEY` is required. The app will fail at runtime without it.

## 4. Install Streamlit if Needed

The main UI entry point is `streamlit_app.py`. If `streamlit` is not available after activating the environment, install it:

```powershell
pip install streamlit
```

You can check whether Streamlit is installed with:

```powershell
streamlit --version
```

## 5. Run the Streamlit App

Start the user interface:

```powershell
streamlit run streamlit_app.py
```

Then open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

Upload a CSV file, optionally enable execution order in the report, and click `Run Analysis`. The app will generate a downloadable PDF report.
