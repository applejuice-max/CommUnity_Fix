@echo off
echo Starting CommUnityFix - Barangay Union
echo.
echo Installing dependencies...
python3.13 -m pip install -r requirements.txt
echo.
echo Starting Streamlit application...
python3.13 -m streamlit run communityfix_app.py
pause
