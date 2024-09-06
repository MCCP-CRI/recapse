# Use a Python 3 image as the base
FROM python:3-alpine

# Set a working directory for the application
WORKDIR /app

RUN apk update && apk upgrade && apk add build-base py3-build py3-scikit-build g++ cmake bzip2-dev zlib-dev xz-dev

COPY requirements.txt .
# Install dependencies listed in requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

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
