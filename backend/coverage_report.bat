@echo off
echo === Models Coverage === > coverage_summary.txt
coverage run --include="app/models.py,app/schemas/*.py" -m pytest tests/
coverage report -m >> coverage_summary.txt

echo === API Endpoints Coverage === >> coverage_summary.txt
coverage run --include="app/routers/*.py" -m pytest tests/
coverage report -m >> coverage_summary.txt

echo === RBAC Logic Coverage === >> coverage_summary.txt
coverage run --include="app/core/dependencies.py,app/routers/auth.py" -m pytest tests/
coverage report -m >> coverage_summary.txt

echo === Search & Pagination Logic Coverage === >> coverage_summary.txt
coverage run --include="app/routers/projects.py" -m pytest tests/
coverage report -m >> coverage_summary.txt

echo === Overall Backend Coverage === >> coverage_summary.txt
coverage run -m pytest tests/
coverage report -m >> coverage_summary.txt

pause