# Ruby on Rails Development Environment Bootstrap

Automatically sets up a complete Ruby on Rails development environment on Ubuntu using mise as the runtime manager.

## What Gets Installed

- **System packages**: build-essential, curl, git, PostgreSQL server
- **Ruby**: Latest stable (via mise)
- **Node.js**: Latest LTS (via mise)
- **Yarn**: Latest (via mise)
- **Rails**: Latest version globally
- **PostgreSQL**: Configured with postgres/postgres user

## Usage

### SSH into your Ubuntu server and run:

```bash
# Download the script
wget https://raw.githubusercontent.com/everes-sh/rails-bootstrap/main/setup.py

# Run with sudo
sudo python3 setup.py
```

### After completion:

```bash
# Load the environment
source ~/.bashrc

# Create a Rails app
rails new myapp -d postgresql
cd myapp
rails db:create
rails server
```

## Requirements

- Ubuntu 20.04+ (tested on 22.04 LTS)
- Root/sudo access
- Internet connection

The script is idempotent - safe to run multiple times.