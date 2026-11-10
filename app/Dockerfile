# Base image that bundles the AWS Lambda Python image with the lambda-feedback middleware (app.handler)
FROM ghcr.io/lambda-feedback/baseevalutionfunctionlayer:main-3.12

# The 3.12 image is Amazon Linux 2023: use dnf, and install `find` (used below)
RUN dnf install -y findutils wget unzip && dnf clean all

WORKDIR /app

ENV PYTHONPATH=/app

RUN mkdir /usr/share/nltk_data
RUN mkdir -p /usr/share/nltk_data/corpora /usr/share/nltk_data/models /usr/share/nltk_data/tokenizers

ARG NLTK_DATA=/usr/share/nltk_data

ENV NLTK_DATA=/usr/share/nltk_data
# Copy and install any packages/modules needed for your evaluation script.
COPY requirements.txt .
COPY brown_length .
COPY word_freqs .
COPY w2v .
RUN pip3 install -r requirements.txt

# The healthcheck command runs the pytest suite
RUN pip3 install pytest

# # Download NLTK data files
# RUN wget -O /usr/share/nltk_data/corpora/wordnet.zip https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/wordnet.zip
# RUN wget -O /usr/share/nltk_data/models/word2vec_sample.zip https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/models/word2vec_sample.zip
# RUN wget -O /usr/share/nltk_data/corpora/brown.zip https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/brown.zip
# RUN wget -O /usr/share/nltk_data/corpora/stopwords.zip https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/stopwords.zip
# RUN wget -O /usr/share/nltk_data/tokenizers/punkt.zip https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/tokenizers/punkt.zip
# RUN wget -O /usr/share/nltk_data/tokenizers/punkt_tab.zip https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/tokenizers/punkt_tab.zip

# # Unzip the downloaded files into the correct subfolders corresponsing to NLTK requirements
# RUN unzip /usr/share/nltk_data/corpora/wordnet.zip -d /usr/share/nltk_data/corpora/
# RUN unzip /usr/share/nltk_data/models/word2vec_sample.zip -d /usr/share/nltk_data/models/
# RUN unzip /usr/share/nltk_data/corpora/brown.zip -d /usr/share/nltk_data/corpora/
# RUN unzip /usr/share/nltk_data/corpora/stopwords.zip -d /usr/share/nltk_data/corpora/
# RUN unzip /usr/share/nltk_data/tokenizers/punkt.zip -d /usr/share/nltk_data/tokenizers/
# RUN unzip /usr/share/nltk_data/tokenizers/punkt_tab.zip -d /usr/share/nltk_data/tokenizers/

# # Clean up zip files to reduce image size
# RUN rm /usr/share/nltk_data/corpora/*.zip
# RUN rm /usr/share/nltk_data/models/*.zip
# RUN rm /usr/share/nltk_data/tokenizers/*.zip

# Warnings: those commands sometimes download corrupted zips, so it is better to wget each package from the main site
RUN python3 -m nltk.downloader wordnet
RUN python3 -m nltk.downloader word2vec_sample
RUN python3 -m nltk.downloader brown
RUN python3 -m nltk.downloader stopwords
RUN python3 -m nltk.downloader punkt
RUN python3 -m nltk.downloader punkt_tab

# Copy the evaluation and testing scripts
COPY brown_length ./app/
COPY word_freqs ./app/
COPY w2v ./app/
COPY evaluation.py ./app/
COPY evaluation_tests.py ./app/

# Copy Documentation
COPY docs/dev.md ./app/docs/dev.md
COPY docs/user.md ./app/docs/user.md

# Set permissions so files and directories can be accessed on AWS
RUN chmod 644 $(find . -type f)
RUN chmod 755 $(find . -type d)

# The entrypoint for AWS is to invoke the handler function within the app package.
# Python 3.12's Lambda runtime imports this as a module name, so it can't be a path.
CMD [ "app.handler" ]
