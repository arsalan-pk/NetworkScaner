# Network Scanner

A professional network security assessment tool built with modular architecture principles.

## Features

### Core Functionality
- **Network Discovery**: Comprehensive host and service discovery
- **Port Scanning**: Multiple scan profiles with customizable options
- **OS Detection**: Advanced operating system fingerprinting
- **Service Detection**: Version detection and service enumeration
- **Professional Reports**: HTML reports with security recommendations

### Professional Features
- **Modular Architecture**: Clean separation of concerns
- **Configuration Management**: YAML-based configuration with environment support
- **Professional Logging**: Structured logging with rotation
- **Input Validation**: Comprehensive validation and sanitization
- **Error Handling**: Robust exception handling hierarchy
- **Type Safety**: Full type hints and documentation

### Security Features
- **Input Validation**: IP, domain, and port range validation
- **Sanitization**: Protection against injection attacks
- **Audit Trail**: Complete logging of all operations
- **Secure Defaults**: Security-first configuration

## Installation

### Prerequisites
- Python 3.8 or higher
- Nmap installed and in PATH
- Tkinter (usually included with Python)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Install Nmap
- **Windows**: Download from [nmap.org](https://nmap.org/download.html)
- **Linux**: `sudo apt-get install nmap` or `sudo yum install nmap`
- **macOS**: `brew install nmap`

## Usage

### Run the Application
```bash
python src/network_scanner/main.py
```

### Configuration
Configuration files are located in the `config/` directory:

- `base_config.yaml` - Default settings
- `development_config.yaml` - Development overrides
- `production_config.yaml` - Production overrides

### Environment Variables
- `NETWORK_SCANNER_ENV` - Environment (development/production)
- `NETWORK_SCANNER_CONFIG_DIR` - Custom config directory path

## Architecture

### Project Structure
```
network_scanner/
├── src/
│   └── network_scanner/
│       ├── core/           # Business logic
│       ├── ui/             # User interface
│       ├── reports/        # Report generation
│       └── config/         # Configuration management
├── config/                # Configuration files
├── tests/                 # Unit tests
└── requirements.txt       # Dependencies
```

### Key Components

#### Core (`src/network_scanner/core/`)
- `scanner.py` - Main scanning engine
- `validator.py` - Input validation and sanitization
- `exceptions.py` - Custom exception hierarchy
- `logging_config.py` - Logging configuration

#### UI (`src/network_scanner/ui/`)
- `main_window.py` - Main application window
- `styles.py` - UI styling and theming

#### Reports (`src/network_scanner/reports/`)
- `html_generator.py` - HTML report generation

#### Config (`src/network_scanner/config/`)
- `settings.py` - Configuration management

## Scan Profiles

The application includes several predefined scan profiles:

- **Intense Scan**: Comprehensive scan with OS detection, version detection, and scripts
- **Quick Scan**: Fast scan of common ports
- **Ping Scan**: Host discovery only
- **SYN Scan**: Stealthy TCP SYN scan
- **UDP Scan**: UDP port scanning
- **Version Scan**: Service version detection
- **OS Scan**: Operating system detection
- **Aggressive Scan**: Intense scan with verbose output

## Development

### Setup Development Environment
```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Code formatting
black src/

# Type checking
mypy src/

# Linting
flake8 src/
```

### Project Structure Guidelines
- **Separation of Concerns**: Each module has a single responsibility
- **Dependency Injection**: Configuration and dependencies are injected
- **Error Handling**: Comprehensive exception handling throughout
- **Type Safety**: Full type hints for better code quality
- **Documentation**: Complete docstrings and comments

### Adding New Features
1. Follow the existing architecture patterns
2. Add proper type hints and documentation
3. Include comprehensive error handling
4. Add unit tests
5. Update configuration if needed

## Security Considerations

### Input Validation
- All user inputs are validated before processing
- IP addresses, domains, and port ranges are thoroughly checked
- Malicious input is rejected with clear error messages

### Logging
- All operations are logged for audit purposes
- Sensitive information is not logged
- Log files are rotated to prevent disk space issues

### Error Handling
- No sensitive information is exposed in error messages
- Graceful degradation on errors
- Comprehensive error reporting for debugging

## Troubleshooting

### Common Issues

#### Nmap Not Found
```
Error: Nmap is not installed or not in your PATH
```
**Solution**: Install nmap and ensure it's in your system PATH

#### Permission Denied
```
Error: Permission denied
```
**Solution**: Run with appropriate privileges (sudo on Linux/macOS)

#### Configuration Errors
```
Error: Failed to load configuration
```
**Solution**: Check config files and environment variables

### Debug Mode
Enable debug mode by setting:
```yaml
app:
  debug: true
logging:
  level: "DEBUG"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the documentation

## Changelog

### Version 1.0.0
- Initial professional release
- Modular architecture implementation
- Professional UI with theming
- Comprehensive reporting system
- Full configuration management
- Professional-grade error handling and logging