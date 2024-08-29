# Use a Python 3 image as the base
FROM ubuntu:24.04

# Set a working directory for the application
WORKDIR /app

RUN apt-get update && apt-get install -y wget
RUN wget -q https://repo.anaconda.com/archive/Anaconda3-2024.06-1-Linux-x86_64.sh -O install-conda.sh
RUN bash install-conda.sh -b -p /root/miniconda
RUN eval "$(/root/miniconda/bin/conda shell.bash hook)"
RUN /root/miniconda/bin/conda init
SHELL ["/root/miniconda/bin/conda", "run", "/bin/bash", "-c"]
RUN conda config --append channels conda-forge
RUN conda install -y conda-libmamba-solver
RUN conda config --set solver libmamba
RUN conda install -y python=3.11 pip

COPY requirements.txt .
# Install dependencies listed in requirements.txt
RUN pip install -r requirements.txt

RUN conda clean -a

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
