# Use Python 3.9.13 image as the base image
FROM python:3.9.13

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Upgrade pip to the latest version to avoid the warning
RUN python -m pip install --upgrade pip

# Install virtualenv to create a virtual environment
RUN pip install virtualenv

# Create a virtual environment
RUN virtualenv venv

# Install the dependencies listed in requirements.txt within the virtual environment
RUN ./venv/bin/pip install -r requirements.txt

# Ensure the necessary port (commonly 8501 for Streamlit) is exposed for web traffic
EXPOSE 8501

# Set environment variable for the port, default to 8501 if not set
ENV PORT 8501

# Define the entry point for the container to run your Streamlit app
CMD ["./venv/bin/streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
