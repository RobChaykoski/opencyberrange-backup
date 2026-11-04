FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=UTC \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server \
    sudo \
    curl \
    ca-certificates \
    p7zip-full \
    python3 \
    python3-pip \
    procps \
    less \
    && rm -rf /var/lib/apt/lists/*

# Volatility 3 and its Python dependencies. The `vol` console script is
# installed in /usr/local/bin and is available to every account.
RUN pip3 install --no-cache-dir volatility3==2.28.2 pycryptodome

# Analyst account. The password is intentionally simple for a training
# container and is documented in the lab metadata.
RUN useradd -m -s /bin/bash analyst && \
    echo 'analyst:M3m0ry_4n4lys1s' | chpasswd && \
    usermod -aG sudo analyst && \
    printf 'analyst ALL=(ALL) NOPASSWD:ALL\n' > /etc/sudoers.d/90-analyst && \
    chmod 0440 /etc/sudoers.d/90-analyst

# Symbol file for the Windows Server 2008 SP1 x86 kernel in the image.
RUN mkdir -p /home/analyst/symbols/windows/ntkrpamp.pdb
COPY symbols/windows/ntkrpamp.pdb/*.json.xz /home/analyst/symbols/windows/ntkrpamp.pdb/

# Download the training memory image, verify its published MD5, and unpack it.
# The image is approximately 512 MB after extraction.
RUN mkdir -p /home/analyst/evidence && \
    curl -fsSL --retry 3 -o /tmp/memdump.7z \
      https://samsclass.info/121/proj/memdump.7z && \
    echo "364fed484bcdd1a1f81a3538a4b1cd9a  /tmp/memdump.7z" | md5sum -c - && \
    7z x -y -o/home/analyst/evidence /tmp/memdump.7z >/dev/null && \
    rm -f /tmp/memdump.7z && \
    test -f /home/analyst/evidence/memdump.mem && \
    chown -R analyst:analyst /home/analyst/evidence /home/analyst/symbols

COPY case_brief.txt /home/analyst/evidence/case_brief.txt
RUN chown analyst:analyst /home/analyst/evidence/case_brief.txt

RUN mkdir -p /run/sshd
COPY start.sh /start.sh
RUN chmod +x /start.sh

USER analyst

HEALTHCHECK --interval=15s --timeout=5s --retries=5 \
    CMD bash -c '</dev/tcp/127.0.0.1/22' || exit 1

CMD ["sudo", "/start.sh"]
