FROM python:3.11-slim

# Install system dependencies for Playwright browsers
RUN apt-get update && \
    apt-get install -y wget gnupg libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libasound2 libpangocairo-1.0-0 libpango-1.0-0 libgtk-3-0 libxss1 libxtst6 libxshmfence1 libglu1-mesa && \
    rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install --with-deps

# Copy the rest of the code
COPY . .

# Run the script
CMD ["python", "main.py"]