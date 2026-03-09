# Installation Guide

## Quick Start (Recommended)

### macOS & Linux

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/dynamiR.git
cd dynamiR

# 2. Run installation script
bash install.sh

# 3. Run the application
source venv/bin/activate
python3 projet.py
```

### Windows

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/dynamiR.git
cd dynamiR

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application
python projet.py
```

## Manual Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)
- git (for cloning the repository)

### Step-by-Step

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/dynamiR.git
   cd dynamiR
   ```

2. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   ```

3. **Activate Virtual Environment**
   
   **macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```
   
   **Windows:**
   ```bash
   venv\Scripts\activate
   ```

4. **Upgrade pip**
   ```bash
   pip install --upgrade pip
   ```

5. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

6. **Verify Installation**
   ```bash
   python3 -c "import Bio; print(f'BioPython {Bio.__version__} installed successfully')"
   ```

7. **Run the Application**
   ```bash
   python3 projet.py
   ```

## Installation Verification

After installation, verify everything works:

```bash
# Test import of main module
python3 -c "from gui_frontend import MicroApp; print('GUI module loaded successfully')"

# Test backend import
python3 -c "from backend.stub_backend import backend_match_micro_to_mrna; print('Backend module loaded successfully')"

# Run the application
python3 projet.py
```

## Development Installation

For contributing or development:

```bash
# Install with development dependencies (optional)
pip install -e .
pip install pytest pytest-cov black flake8
```

## Troubleshooting

### "Python 3 not found"
- Install Python 3.7+ from [python.org](https://www.python.org/)
- Verify installation: `python3 --version`

### "Module not found: Bio"
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Reinstall BioPython
pip install --force-reinstall biopython
```

### "Permission denied" on Linux/macOS
```bash
# Make install script executable
chmod +x install.sh

# Run again
bash install.sh
```

### Application won't start
1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Check Python version: `python3 --version` (should be 3.7+)
3. Verify Tkinter is available: `python3 -m tkinter` (should open test window)

### "No module named 'tkinter'" (Linux)
Install Tkinter:
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# macOS (Homebrew)
brew install python-tk
```

## Uninstallation

To remove DynamiR and its virtual environment:

```bash
# Remove virtual environment
rm -rf venv

# Remove project directory (if desired)
rm -rf dynamiR
```

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.7 | 3.10+ |
| RAM | 512 MB | 2 GB |
| Disk Space | 500 MB | 1 GB |
| Operating System | Any | macOS 10.14+, Ubuntu 18.04+, Windows 10+ |

## Using with PyPI (Future)

Once DynamiR is published to PyPI:

```bash
# Install directly
pip install dynamiR

# Run from command line
dynamiR
```

## Docker (Future)

```bash
# Build Docker image
docker build -t dynamir .

# Run in Docker container
docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix dynamir
```

## Getting Help

- Check [README.md](README.md) for overview
- Read [DEVELOPMENT.md](DEVELOPMENT.md) for development setup
- Open an issue on GitHub for problems
- Review [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines
