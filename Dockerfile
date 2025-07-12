# Use the Python 3.9 image as a base
FROM python:3.9 AS docs

# Set the working directory in the container to /usr/src
WORKDIR /usr/src

# Update the package lists and install the required packages.
# - `sassc`: For compiling SASS to CSS
# - `npm`: Node Package Manager, for managing JavaScript packages
# - `bash`: Bourne Again SHell, a shell for running commands
# - `gosu`: A tool for running commands as another user
# - `ansible`: Automation platform for configuration management
# - `less`: A terminal paginator for viewing text content
# - `rsync`: A tool for fast file transfer and synchronization
# - `git`: Version control system for tracking changes
RUN apt-get update && apt-get install -y sassc npm bash gosu ansible less rsync git ca-certificates && update-ca-certificates

# Install global npm packages
# - `autoprefixer`: PostCSS plugin to parse CSS and add vendor prefixes
# - `cssnano`: A modular minifier for CSS
# - `postcss`: A tool for transforming CSS with JavaScript plugins
# - `postcss-cli`: Command line interface for PostCSS
RUN npm install -g autoprefixer cssnano postcss postcss-cli

# Clone the necessary repositories
# - `antsibull-core`, `antsibull-docs-parser`, `antsibull-docs`: Repositories related to Ansible documentation tools
RUN git clone https://github.com/ansible-community/antsibull-core.git \
    && git clone https://github.com/ansible-community/antsibull-docs-parser.git \
    && git clone https://github.com/ansible-community/antsibull-docs.git

# Set up the virtual environment and install dependencies
# - The virtual environment is created and activated
# - Dependencies are installed using pip in editable mode (with `-e`)
# - The `[dev]` extra means that additional packages necessary for development will be installed
# - The last part of the command ensures that the local copies of `antsibull-core` and `antsibull-docs-parser` are used.
WORKDIR /usr/src/antsibull-docs
RUN python3 -m venv venv \
    && . ./venv/bin/activate \
    && pip install -e '.[dev]' -e ../antsibull-core -e ../antsibull-docs-parser
