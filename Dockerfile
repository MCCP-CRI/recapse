# Use a slim Python 3 image as the base
FROM python:3.10-slim

# Set a working directory for the application
WORKDIR /app

# Copy requirements.txt file
COPY requirements.txt .

# Install dependencies listed in requirements.txt
RUN pip install -r requirements.txt
# if using gunicorn, install it
# RUN pip install gunicorn

# Copy the needed project components
COPY prediction prediction/
COPY preprocess preprocess/
COPY webapp webapp/
COPY app.py ./

# Expose the port where Flask application runs (usually 5000)
EXPOSE 5000

# Run the flask server
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]

# Alternative: Run the Flask app using gunicorn (production-ready WSGI server)
# CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "wsgi:application" ]
