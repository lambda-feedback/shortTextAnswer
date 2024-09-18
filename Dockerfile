# Stage 1: Builder
# ------- FOR DEBIAN
FROM ghcr.io/lambda-feedback/evaluation-function-base/python:3.11 as builder
# ------- FOR AMAZON LINUX 2
# FROM rabidsheep55/python-base-eval-layer as builder

# Install Poetry
RUN pip install poetry==1.8.3

# Set Poetry environment variables
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Set working directory
WORKDIR /app

# Copy Poetry files
COPY pyproject.toml ./

# Generate poetry.lock specific to the container environment
# RUN poetry lock

# Install dependencies via Poetry
RUN --mount=type=cache,target=$POETRY_CACHE_DIR \
    poetry install -vvv --without dev --no-root

# Stage 2: App
# ------- FOR DEBIAN
FROM ghcr.io/lambda-feedback/evaluation-function-base/python:3.11
# ------- FOR AMAZON LINUX 2
# FROM rabidsheep55/python-base-eval-layer

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# Precompile Python files for faster startup
RUN python -m compileall -q .

# Set working directory
WORKDIR /app

# Copy the app evaluation function and other relevant files
COPY app/ .

# Set environment 
# ------- FOR DEBIAN
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    unzip
# ------- FOR AMAZON LINUX 2
# RUN yum -y upgrade && yum install -y wget unzip

# Additional custom setup for NLTK
RUN mkdir -p /usr/share/nltk_data/corpora /usr/share/nltk_data/models /usr/share/nltk_data/tokenizers

# NLTK data downloads
RUN wget -O /usr/share/nltk_data/corpora/wordnet.zip https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/wordnet.zip
RUN wget -O /usr/share/nltk_data/models/word2vec_sample.zip https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/models/word2vec_sample.zip
RUN wget -O /usr/share/nltk_data/corpora/brown.zip https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/brown.zip
RUN wget -O /usr/share/nltk_data/corpora/stopwords.zip https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/stopwords.zip
RUN wget -O /usr/share/nltk_data/tokenizers/punkt.zip https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/tokenizers/punkt.zip
RUN wget -O /usr/share/nltk_data/tokenizers/punkt_tab.zip https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/tokenizers/punkt_tab.zip

# Unzip the downloaded NLTK data
RUN unzip /usr/share/nltk_data/corpora/wordnet.zip -d /usr/share/nltk_data/corpora/
RUN unzip /usr/share/nltk_data/models/word2vec_sample.zip -d /usr/share/nltk_data/models/
RUN unzip /usr/share/nltk_data/corpora/brown.zip -d /usr/share/nltk_data/corpora/
RUN unzip /usr/share/nltk_data/corpora/stopwords.zip -d /usr/share/nltk_data/corpora/
RUN unzip /usr/share/nltk_data/tokenizers/punkt.zip -d /usr/share/nltk_data/tokenizers/
RUN unzip /usr/share/nltk_data/tokenizers/punkt_tab.zip -d /usr/share/nltk_data/tokenizers/

# Clean up zip files to reduce image size
RUN rm /usr/share/nltk_data/corpora/*.zip
RUN rm /usr/share/nltk_data/models/*.zip
RUN rm /usr/share/nltk_data/tokenizers/*.zip

# Set environment variables for running the evaluation function
ENV FUNCTION_COMMAND="python"
ENV FUNCTION_ARGS="-m,app.evaluation,--no-sandbox"
ENV FUNCTION_RPC_TRANSPORT="ipc"
ENV LOG_LEVEL="debug"

# # Command to start the evaluation function
# CMD [ "python", "-m", "app.evaluation" ]
# ------- FOR DEBIAN
# Keep the container running
CMD ["tail", "-f", "/dev/null"]

# ------- FOR AMAZON LINUX 2
# The entrypoint for AWS is to invoke the handler function within the app package
# CMD [ "/app/app.handler" ]
