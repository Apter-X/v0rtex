# v0rtex Architecture Documentation

## 🏗️ System Overview

v0rtex is a dynamic, JSON-based web scraping framework designed with modularity, extensibility, and anti-detection capabilities at its core. The architecture follows a layered approach with clear separation of concerns.

## 🎯 Core Design Principles

- **Modularity**: Each component is self-contained with well-defined interfaces
- **Extensibility**: Plugin-based architecture for new features and strategies
- **Resilience**: Robust error handling and recovery mechanisms
- **Performance**: Efficient resource management and concurrent processing
- **Security**: Anti-detection and stealth capabilities built-in

## 🏛️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI Layer                            │
├─────────────────────────────────────────────────────────────┤
│                     Core Scraping Engine                    │
├─────────────────────────────────────────────────────────────┤
│  Pagination  │  Session  │  Config  │  Anti-Detection      │
├─────────────────────────────────────────────────────────────┤
│                    Utility Services                         │
│  CAPTCHA  │  VPN/Proxy  │  Browser  │  Data Processing    │
├─────────────────────────────────────────────────────────────┤
│                    External Services                        │
│  2captcha  │  AntiCaptcha  │  OpenVPN  │  WebDriver        │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Core Components

### 1. Main Scraper (`V0rtexScraper`)
**Location**: `src/v0rtex/core/scraper.py`
**Purpose**: Central orchestrator for all scraping operations

**Key Responsibilities**:
- Browser management and WebDriver coordination
- Configuration validation and application
- Session management and persistence
- Error handling and recovery
- Pagination coordination
- Data extraction and processing

**Architecture Pattern**: Facade pattern - provides simplified interface to complex subsystems

### 2. Configuration Management (`ScrapingConfig`)
**Location**: `src/v0rtex/core/config.py`
**Purpose**: Centralized configuration management using Pydantic

**Key Features**:
- JSON/YAML configuration loading
- Schema validation and type safety
- Environment variable support
- Configuration inheritance and merging
- Runtime configuration updates

**Architecture Pattern**: Builder pattern with validation

### 3. Session Management (`ScrapingSession`)
**Location**: `src/v0rtex/core/session.py`
**Purpose**: Persistent session state and recovery

**Key Features**:
- Session persistence to disk
- State recovery and resumption
- Progress tracking and monitoring
- Error state management
- Cleanup and resource management

**Architecture Pattern**: State machine with persistence

### 4. Pagination System
**Location**: `src/v0rtex/core/pagination/`
**Purpose**: Advanced pagination handling with multiple strategies

**Components**:
- **`PaginationState`**: Manages pagination progress and state
- **`PaginationStrategy`**: Abstract base for different pagination approaches
- **`PaginationDetector`**: Automatic strategy detection
- **`PaginationNavigator`**: Navigation workflow management

**Supported Strategies**:
- URL-based pagination (`?page=2`, `/page/2`)
- JavaScript pagination (button clicks, page numbers)
- Infinite scroll (load-more buttons, scroll-based)
- Auto-detection with confidence scoring

**Architecture Pattern**: Strategy pattern with factory

## 🛡️ Anti-Detection System

### Browser Fingerprinting
**Location**: `src/v0rtex/utils/anti_detection.py`
**Purpose**: Evade detection through browser fingerprinting

**Techniques**:
- User agent rotation and randomization
- Viewport size randomization
- Language preference randomization
- Header management and rotation
- Stealth mode implementation
- Undetected Chrome integration

### CAPTCHA Solving
**Location**: `src/v0rtex/utils/captcha_solver.py`
**Purpose**: Automatic CAPTCHA resolution

**Supported Services**:
- 2captcha integration
- AntiCaptcha integration
- Image CAPTCHA solving
- reCAPTCHA v2 support
- hCaptcha support
- Service fallback system

### VPN/Proxy Management
**Location**: `src/v0rtex/utils/vpn_manager.py`
**Purpose**: IP rotation and proxy management

**Capabilities**:
- OpenVPN integration
- WireGuard support
- SOCKS4/5 proxy support
- HTTP/HTTPS proxy support
- Proxy rotation system
- Connection health monitoring

## 🔄 Data Flow Architecture

### 1. Configuration Loading
```
JSON/YAML Config → Pydantic Validation → ScrapingConfig Object
```

### 2. Scraping Workflow
```
Config → Browser Setup → Page Navigation → Data Extraction → Processing → Output
```

### 3. Pagination Flow
```
Page Detection → Strategy Selection → Navigation → State Update → Repeat
```

### 4. Error Handling Flow
```
Error Detection → Recovery Attempt → Fallback Strategy → Logging → Continue/Abort
```

## 🚀 Performance Considerations

### Resource Management
- **Browser Pooling**: Efficient WebDriver lifecycle management
- **Memory Optimization**: Lazy loading and cleanup of large objects
- **Connection Pooling**: Reuse of VPN/proxy connections
- **Async Operations**: Non-blocking I/O where possible

### Scalability Features
- **Concurrent Scraping**: Multiple browser instances
- **Rate Limiting**: Configurable delays and throttling
- **Resource Limits**: Memory and CPU usage controls
- **Batch Processing**: Efficient data processing pipelines

## 🔒 Security Architecture

### Anti-Detection Measures
- **Browser Fingerprinting**: Evade detection scripts
- **Request Randomization**: Unpredictable request patterns
- **Session Rotation**: Regular session refresh
- **IP Rotation**: VPN/proxy switching

### Data Protection
- **Session Encryption**: Secure storage of sensitive data
- **Credential Management**: Secure handling of login information
- **Log Sanitization**: Removal of sensitive data from logs
- **Access Controls**: Configuration-based permission system

## 🧪 Testing Architecture

### Test Structure
- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **End-to-End Tests**: Full workflow testing
- **Performance Tests**: Load and stress testing

### Test Utilities
- **Mock Services**: Simulated external dependencies
- **Test Data**: Comprehensive test datasets
- **CI/CD Integration**: Automated testing pipeline

## 🔮 Future Architecture Considerations

### Planned Enhancements
- **Plugin System**: Extensible architecture for custom modules
- **Microservices**: Distributed scraping capabilities
- **Cloud Integration**: AWS/Azure deployment support
- **Real-time Processing**: Streaming data processing
- **Machine Learning**: Intelligent CAPTCHA and detection avoidance

### Scalability Improvements
- **Horizontal Scaling**: Multi-instance deployment
- **Load Balancing**: Intelligent request distribution
- **Caching Layer**: Redis-based session and data caching
- **Message Queues**: Asynchronous task processing

## 📚 Related Documentation

- [Contributing Guide](contributing-guide.md) - Development guidelines
- [API Reference](wiki/api-reference.md) - Detailed API documentation
- [Configuration Guide](wiki/configuration.md) - Configuration options
- [Deployment Guide](wiki/deployment.md) - Production deployment
- [Troubleshooting](wiki/troubleshooting.md) - Common issues and solutions
