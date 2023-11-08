FROM python:3.11.6-alpine


# Create the application directory and set the working directory
WORKDIR /app

# Install SQLite
RUN apk add --no-cache sqlite

# Copy the application code and requirements.txt
COPY requirements.txt app.py /app/

COPY data/database.db /app/.data/database.db

RUN pip install -r requirements.txt

CMD ["python", "app.py"]