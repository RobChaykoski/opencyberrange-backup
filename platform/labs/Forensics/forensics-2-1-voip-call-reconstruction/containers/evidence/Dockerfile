FROM nginxinc/nginx-unprivileged:alpine

COPY voip-call.pcap /usr/share/nginx/html/voip-call.pcap
COPY reconstruct.py /usr/share/nginx/html/reconstruct.py
COPY README.txt /usr/share/nginx/html/README.txt
COPY transcript.txt /usr/share/nginx/html/transcript.txt

USER 101

HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
    CMD wget -q -O /dev/null http://127.0.0.1:8080/README.txt || exit 1

EXPOSE 8080
