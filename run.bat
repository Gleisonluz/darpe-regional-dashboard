@echo off
cd /d "C:\Users\Gleison Luz\darpe-regional-dashboard"
uvicorn backend.server:app --reload
pause