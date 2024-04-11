FROM python:3.7
ADD main.py .
RUN pip install requests beautifulsoup4 python-dotenv
CMD ["python", "./main.py"] 