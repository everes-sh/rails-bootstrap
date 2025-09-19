#!/usr/bin/env python3
"""
Ruby on Rails Development Environment Bootstrap Script for Ubuntu
================================================================

This script sets up a complete Ruby on Rails development environment on Ubuntu
using mise as the runtime manager.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class RailsBootstrap:
    """Bootstrap Ruby on Rails development environment on Ubuntu."""

    def __init__(self):
        self.user = os.environ.get('SUDO_USER', 'ubuntu')
        self.user_home = Path(f'/home/{self.user}')
        self.mise_bin = str(self.user_home / '.local' / 'bin' / 'mise')

        self.packages = [
            'build-essential', 'curl', 'git', 'libpq-dev', 'zlib1g-dev',
            'libssl-dev', 'libreadline-dev', 'libyaml-dev', 'libsqlite3-dev',
            'sqlite3', 'libxml2-dev', 'libxslt1-dev', 'libcurl4-openssl-dev',
            'libffi-dev', 'postgresql', 'postgresql-contrib'
        ]

    def run_cmd(self, cmd, user=None, env=None):
        """Execute a command."""
        if user and user != 'root':
            cmd = ['sudo', '-u', user, '-H'] + cmd

        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Command failed: {' '.join(cmd)}")
            raise subprocess.CalledProcessError(result.returncode, cmd)
        return result

    def ensure_user(self):
        """Ensure user exists."""
        try:
            self.run_cmd(['id', self.user])
        except subprocess.CalledProcessError:
            self.run_cmd(['useradd', '-m', '-s', '/bin/bash', self.user])
            self.run_cmd(['usermod', '-aG', 'sudo', self.user])

        self.user_home.mkdir(parents=True, exist_ok=True)
        self.run_cmd(['chown', f'{self.user}:{self.user}', str(self.user_home)])

    def install_packages(self):
        """Install system packages."""
        logger.info("Installing packages...")
        self.run_cmd(['apt-get', 'update'])
        self.run_cmd(['apt-get', 'install', '-y'] + self.packages)

    def install_mise(self):
        """Install mise."""
        if (self.user_home / '.local' / 'bin' / 'mise').exists():
            return

        logger.info("Installing mise...")
        local_bin = self.user_home / '.local' / 'bin'
        local_bin.mkdir(parents=True, exist_ok=True)
        self.run_cmd(['chown', '-R', f'{self.user}:{self.user}', str(self.user_home / '.local')])

        # Install mise
        env = {'HOME': str(self.user_home)}
        self.run_cmd(['bash', '-c', 'curl https://mise.jdx.dev/install.sh | sh'], user=self.user, env=env)

    def setup_shell(self):
        """Configure shell for mise."""
        bashrc = self.user_home / '.bashrc'

        config = '''
# mise configuration
export PATH="$HOME/.local/bin:$PATH"
if command -v mise >/dev/null 2>&1; then
    eval "$(mise activate bash)"
fi
'''

        if bashrc.exists():
            content = bashrc.read_text()
            if 'mise activate' in content:
                return

        with open(bashrc, 'a') as f:
            f.write(config)
        self.run_cmd(['chown', f'{self.user}:{self.user}', str(bashrc)])

    def install_runtimes(self):
        """Install Ruby, Node.js, and Yarn via mise."""
        logger.info("Installing Ruby, Node.js, and Yarn...")

        env = {
            'HOME': str(self.user_home),
            'PATH': f"{self.user_home}/.local/bin:{os.environ.get('PATH', '')}"
        }

        for runtime in ['ruby@latest', 'node@lts', 'yarn@latest']:
            self.run_cmd([self.mise_bin, 'install', runtime], user=self.user, env=env)
            self.run_cmd([self.mise_bin, 'use', '--global', runtime], user=self.user, env=env)

    def setup_postgresql(self):
        """Setup PostgreSQL."""
        logger.info("Setting up PostgreSQL...")
        self.run_cmd(['systemctl', 'enable', 'postgresql'])
        self.run_cmd(['systemctl', 'start', 'postgresql'])

        # Create user if doesn't exist
        try:
            result = self.run_cmd([
                'sudo', '-u', 'postgres', 'psql', '-t', '-c',
                f"SELECT 1 FROM pg_user WHERE usename = '{self.user}';"
            ])
            if '1' not in result.stdout:
                self.run_cmd([
                    'sudo', '-u', 'postgres', 'psql', '-c',
                    f"CREATE USER {self.user} WITH SUPERUSER CREATEDB PASSWORD '{self.user}';"
                ])
        except subprocess.CalledProcessError:
            pass

    def install_rails(self):
        """Install Rails."""
        logger.info("Installing Rails...")

        env = {
            'HOME': str(self.user_home),
            'PATH': f"{self.user_home}/.local/bin:{os.environ.get('PATH', '')}"
        }

        cmd = '''
        export PATH="$HOME/.local/bin:$PATH"
        eval "$(mise activate bash)"
        gem install rails --no-document
        '''

        self.run_cmd(['bash', '-c', cmd], user=self.user, env=env)

    def run(self):
        """Execute the bootstrap process."""
        if os.geteuid() != 0:
            logger.error("Run as root: sudo python3 setup.py")
            sys.exit(1)

        logger.info("Starting Rails environment setup...")

        self.ensure_user()
        self.install_packages()
        self.install_mise()
        self.setup_shell()
        self.install_runtimes()
        self.setup_postgresql()
        self.install_rails()

        logger.info(f"✅ Setup complete! Switch to user: sudo su - {self.user}")

if __name__ == '__main__':
    RailsBootstrap().run()
