# Use an official Python runtime as a parent image
FROM python:3

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for pyodbc
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gnupg \
        g++ \
        unixodbc-dev \
        curl \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . .

# Install any needed packages specified in requirements.txt 
RUN pip install --no-cache-dir -r requirements.txt

# Run app.py when the container launches
CMD ["python", "./src/CityMood.py"]
