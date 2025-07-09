# ChessTutorAI Scripts Directory

This directory contains utility scripts for maintaining, developing, and managing the ChessTutorAI system.

## Available Scripts

### 🗄️ [`database_manager.py`](database_manager.py) - Database Management
Comprehensive database management utilities for the tactical positions database.

**Usage:**
```bash
# Show database statistics
python scripts/database_manager.py stats

# Clean up low-quality positions (quality < 0.5)
python scripts/database_manager.py cleanup --min-quality 0.5

# Create database backup
python scripts/database_manager.py backup

# Export high-quality positions to JSON
python scripts/database_manager.py export --min-quality 0.8 --output tactical_export.json
```

**Features:**
- 📊 Database statistics and analytics
- 🧹 Cleanup low-quality tactical positions
- 💾 Database backup and restore
- 📤 Export positions to JSON format
- 📈 Quality score distribution analysis
- 📅 Recent activity tracking

---

### 🔧 [`system_maintenance.py`](system_maintenance.py) - System Maintenance
System maintenance and monitoring utilities for optimal performance.

**Usage:**
```bash
# Run full system maintenance
python scripts/system_maintenance.py full

# Clean position cache (remove entries older than 30 days)
python scripts/system_maintenance.py cache --max-age 30

# Rotate log files (if larger than 50MB)
python scripts/system_maintenance.py logs --max-size 50

# Validate configuration
python scripts/system_maintenance.py config

# Check dependencies
python scripts/system_maintenance.py deps

# Show system information
python scripts/system_maintenance.py info
```

**Features:**
- 🧹 Cache cleanup and optimization
- 📋 Log file rotation and management
- 🔧 Configuration validation
- 📦 Dependency checking
- 🖥️ System information display
- 🔑 Environment variable validation

---

### 🛠️ [`dev_tools.py`](dev_tools.py) - Development Tools
Development utilities for testing, code quality, and performance monitoring.

**Usage:**
```bash
# Run all development checks
python scripts/dev_tools.py all

# Run tests with coverage
python scripts/dev_tools.py test --coverage --verbose

# Check code quality
python scripts/dev_tools.py quality

# Profile system performance
python scripts/dev_tools.py profile

# Format code with black and isort
python scripts/dev_tools.py format

# Setup development environment
python scripts/dev_tools.py setup
```

**Features:**
- 🧪 Test runner with coverage reports
- 🔍 Code quality checks (flake8)
- ⚡ Performance profiling
- 🎨 Code formatting (black, isort)
- 🛠️ Development environment setup
- 🪝 Git pre-commit hooks

## Quick Reference

### Daily Development Workflow
```bash
# 1. Run all checks before committing
python scripts/dev_tools.py all

# 2. Check system health
python scripts/system_maintenance.py full

# 3. Monitor database growth
python scripts/database_manager.py stats
```

### Maintenance Tasks

#### Weekly Maintenance
```bash
# Clean old cache entries
python scripts/system_maintenance.py cache

# Check log file sizes
python scripts/system_maintenance.py logs

# Backup database
python scripts/database_manager.py backup
```

#### Monthly Maintenance
```bash
# Clean low-quality positions
python scripts/database_manager.py cleanup --min-quality 0.6

# Export high-quality positions
python scripts/database_manager.py export --min-quality 0.8

# Full system check
python scripts/system_maintenance.py full
```

### Troubleshooting

#### System Issues
```bash
# Check all dependencies
python scripts/system_maintenance.py deps

# Validate configuration
python scripts/system_maintenance.py config

# Show system information
python scripts/system_maintenance.py info
```

#### Performance Issues
```bash
# Profile system performance
python scripts/dev_tools.py profile

# Clean cache
python scripts/system_maintenance.py cache

# Check database size
python scripts/database_manager.py stats
```

#### Development Issues
```bash
# Run tests
python scripts/dev_tools.py test --verbose

# Check code quality
python scripts/dev_tools.py quality

# Setup development environment
python scripts/dev_tools.py setup
```

## Script Features Summary

| Script | Database | Cache | Logs | Tests | Config | Performance |
|--------|----------|-------|------|-------|--------|-------------|
| `database_manager.py` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `system_maintenance.py` | ❌ | ✅ | ✅ | ❌ | ✅ | ✅ |
| `dev_tools.py` | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ |

## Requirements

All scripts require Python 3.8+ and the ChessTutorAI package to be properly installed.

### Optional Dependencies for Enhanced Features:
- **pytest** - For running tests (`pip install pytest pytest-cov`)
- **flake8** - For code quality checks (`pip install flake8`)
- **black** - For code formatting (`pip install black`)
- **isort** - For import sorting (`pip install isort`)

## Getting Help

Each script provides detailed help information:
```bash
python scripts/database_manager.py --help
python scripts/system_maintenance.py --help
python scripts/dev_tools.py --help
```

For specific command help:
```bash
python scripts/database_manager.py stats --help
python scripts/system_maintenance.py cache --help
python scripts/dev_tools.py test --help