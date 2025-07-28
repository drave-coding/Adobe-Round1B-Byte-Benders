# part-1b/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Step 1: Install the CPU-only torch version first and separately
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

# Step 2: Copy and install the rest of the requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 3: Copy the entire project source into the container
COPY . .

# Set environment variables for the input and output directories
ENV INPUT_DIR=/app/input
ENV OUTPUT_DIR=/app/output

# The command to execute when the container starts
CMD ["python3", "src/main.py"]