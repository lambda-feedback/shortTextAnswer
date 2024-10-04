# Base image that bundles AWS Lambda Python 3.8 image with some middleware functions
# FROM base-eval-tmp
FROM rabidsheep55/python-base-eval-layer

WORKDIR /app

RUN mkdir /usr/share/nltk_data
RUN mkdir -p /usr/share/nltk_data/corpora /usr/share/nltk_data/models /usr/share/nltk_data/tokenizers

ARG NLTK_DATA=/usr/share/nltk_data

ENV NLTK_DATA=/usr/share/nltk_data
# Copy and install any packages/modules needed for your evaluation script.
COPY requirements.txt .
# COPY brown_length .
# COPY word_freqs .
# COPY w2v .
RUN yum install -y wget unzip 
# RUN yum install -y tar gzip
# RUN yum groupinstall -y "Development Tools"
RUN pip3 install -r requirements.txt

# Install new version of make
# RUN wget http://ftp.gnu.org/gnu/make/make-4.3.tar.gz && tar -xzf make-4.3.tar.gz
# RUN cd make-4.3 && ./configure --disable-dependency-tracking && ./configure && make && make install
# Upgrade GLIBC to run GPT4All
# RUN wget http://ftp.gnu.org/gnu/libc/glibc-2.32.tar.gz && tar -xzf glibc-2.32.tar.gz
# RUN cd glibc-2.32 && mkdir build && cd build 
# && ../configure --prefix=/opt/glibc-2.32

# Download NLTK data files
RUN wget -O /usr/share/nltk_data/corpora/wordnet.zip https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/wordnet.zip
RUN wget -O /usr/share/nltk_data/models/word2vec_sample.zip https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/models/word2vec_sample.zip
RUN wget -O /usr/share/nltk_data/corpora/brown.zip https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/brown.zip
RUN wget -O /usr/share/nltk_data/corpora/stopwords.zip https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/stopwords.zip
RUN wget -O /usr/share/nltk_data/tokenizers/punkt.zip https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/tokenizers/punkt.zip
RUN wget -O /usr/share/nltk_data/tokenizers/punkt_tab.zip https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/tokenizers/punkt_tab.zip

# Unzip the downloaded files into the correct subfolders corresponsing to NLTK requirements
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

# Warnings: those commands sometimes download corrupted zips, so it is better to wget each package from the main site
# RUN python -m nltk.downloader wordnet
# RUN python -m nltk.downloader word2vec_sample
# RUN python -m nltk.downloader brown
# RUN python -m nltk.downloader stopwords
# RUN python -m nltk.downloader punkt
# RUN python -m nltk.downloader punkt_tab

# Copy the evaluation and testing scripts
COPY *.py ./app/
RUN rm ./app/__init__.py
COPY brown_length ./app/
COPY word_freqs ./app/
COPY w2v ./app/

# Copy Models
COPY models ./app/models

# Copy Documentation
COPY docs/dev.md ./app/docs/dev.md
COPY docs/user.md ./app/docs/user.md

# Set permissions so files and directories can be accessed on AWS
RUN chmod 644 $(find . -type f)
RUN chmod 755 $(find . -type d)

# The entrypoint for AWS is to invoke the handler function within the app package
CMD [ "/app/app.handler" ]