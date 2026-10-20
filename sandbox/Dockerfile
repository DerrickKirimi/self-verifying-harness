FROM python@sha256:401f6e1a67dad31a1bd78e9ad22d0ee0a3b52154e6bd30e90be696bb6a3d7461
COPY requirements.txt /opt/requirements.txt
RUN pip install --no-cache-dir -r /opt/requirements.txt
COPY run_check.py /opt/run_check.py
USER 65534:65534
ENTRYPOINT ["python", "-I", "/opt/run_check.py"]
