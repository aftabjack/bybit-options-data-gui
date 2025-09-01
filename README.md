# Bybit Options Data GUI

Real-time cryptocurrency options tracker with web dashboard for Bybit exchange.

## Features

- **Real-time WebSocket** streaming from Bybit (BTC, ETH, SOL options)
- **Redis storage** with optimized batch processing
- **FastAPI web dashboard** with responsive design
- **Production-ready** with auto-reconnection and health checks

## Quick Start

### Prerequisites
- Python 3.9+
- Redis 7.0+

### Installation

```bash
# Clone repository
git clone https://github.com/aftabjack/bybit-options-data-gui.git
cd bybit-options-data-gui

# Install dependencies
pip install -r requirements.txt

# Install Redis (macOS)
brew install redis
brew services start redis
```

### Usage

1. **Start the tracker:**
```bash
python options_tracker_production.py
```

2. **Start the web dashboard:**
```bash
cd webapp
python app_fastapi.py
```

3. **Access dashboard:** http://localhost:5001

## Configuration

Create `.env` file:
```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

## Project Structure

```
├── options_tracker_production.py   # Main tracker
├── webapp/
│   ├── app_fastapi.py             # Web server
│   └── templates/                 # HTML templates
└── requirements.txt               # Dependencies
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/` | Main dashboard |
| `/api/options/{asset}` | Get options data |
| `/api/assets` | Manage assets |
| `/api/stats` | System statistics |

## Performance

- Memory: ~50MB for 2000+ symbols
- Throughput: 10,000+ messages/second
- Latency: <100ms updates

## License

MIT

---

**Note**: For educational purposes. Follow exchange rate limits and terms of service.