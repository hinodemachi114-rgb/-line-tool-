@echo off
echo Starting Streamlit app on port 8502...
echo Please wait while the server starts...
echo Once you see "You can now view your Streamlit app", open http://localhost:8502 in your browser
echo.
python -m streamlit run main.py --server.port 8502 --server.address 127.0.0.1
pause

