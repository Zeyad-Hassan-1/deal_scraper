FROM n8nio/n8n:latest

USER root

# Restore apk from official Alpine image
COPY --from=alpine:latest /sbin/apk /sbin/apk
COPY --from=alpine:latest /lib/apk /lib/apk
COPY --from=alpine:latest /etc/apk /etc/apk
COPY --from=alpine:latest /usr/share/apk /usr/share/apk

# Now we can use apk to install Python and build dependencies
RUN apk add --no-cache python3 py3-pip build-base python3-dev libxml2-dev libxslt-dev gcc musl-dev libffi-dev openssl-dev

# Create a virtual environment for Python packages
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install scrapy, impersonate, and pandas
RUN pip install --no-cache-dir scrapy scrapy-impersonate curl_cffi pandas

USER node
