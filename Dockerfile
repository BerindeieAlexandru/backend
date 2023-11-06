FROM python:3.11.6-alpine


# Create the application directory and set the working directory
WORKDIR /app

# Copy the application code and requirements.txt
COPY requirements.txt app.py /app/

RUN pip install -r requirements.txt

CMD ["python", "app.py"]