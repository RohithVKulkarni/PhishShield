@echo off
SET PYTHON_EXE="C:\Users\ADMIN\AppData\Local\Programs\Python\Python314\python.exe"

echo Installing dependencies...
%PYTHON_EXE% -m pip install -r requirements.txt

echo Starting Backend...
%PYTHON_EXE% -m uvicorn app.main:app --reload
