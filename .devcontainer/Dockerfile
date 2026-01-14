# ABOUTME: Base Python dev container for use with DevPod
# ABOUTME: Includes Python 3.11, common dev tools, and Claude Code CLI

FROM python:3.11-slim

# Avoid prompts during package installation
ARG DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    zsh \
    sudo \
    git \
    curl \
    openssh-client \
    ca-certificates \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (required for Claude Code)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code globally
RUN npm install -g @anthropic-ai/claude-code

# Create non-root user
ARG USERNAME=dev
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m -s /usr/bin/zsh $USERNAME \
    && mkdir -p /home/$USERNAME/.local/bin \
    && chown -R $USERNAME:$USERNAME /home/$USERNAME \
    && echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Set up Python environment
ENV PATH="/home/$USERNAME/.local/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

USER $USERNAME
WORKDIR /workspace

# Upgrade pip
RUN pip install --user --upgrade pip

# Default command
CMD ["bash"]
