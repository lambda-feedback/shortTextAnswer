FROM rabidsheep55/python-base-eval-layer 
# NOTE: this is platform "linux/amd64"
# FROM ghcr.io/lambda-feedback/evaluation-function-base/python:3.11 
# NOTE: transformers from huggingface requires platform "linux/arm64"


WORKDIR /app

# Copy and install any packages/modules needed for your evaluation script.
COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY evaluation.py ./app/
COPY evaluation_tests.py ./app/

# Copy Documentation
COPY docs/dev.md ./app/docs/dev.md
COPY docs/user.md ./app/docs/user.md

# Set permissions so files and directories can be accessed on AWS
RUN chmod 644 $(find . -type f)
RUN chmod 755 $(find . -type d)

# The entrypoint for AWS is to invoke the handler function within the app package
CMD [ "/app/app.handler" ]