#!/usr/bin/env python3
"""
Modular Options Web App with Dynamic Asset Management
"""

import json
import os
import time
from datetime import datetime
from flask import Flask, render_template, jsonify, request, Response
from flask_cors import CORS
import redis
import requests
from typing import Dict, List, Optional

app = Flask(__name__)
CORS(app)

# Configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))

# Initialize Redis
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)

class AssetManager:
    """Manages dynamic assets with persistence"""
    
    ASSETS_KEY = "config:assets"
    DEFAULT_ASSETS = {
        "BTC": {"name": "Bitcoin", "enabled": True, "order": 1},
        "ETH": {"name": "Ethereum", "enabled": True, "order": 2},
        "SOL": {"name": "Solana", "enabled": True, "order": 3}
    }
    
    @classmethod
    def get_assets(cls) -> Dict:
        """Get all configured assets"""
        assets_json = redis_client.get(cls.ASSETS_KEY)
        if assets_json:
            return json.loads(assets_json)
        else:
            # Initialize with defaults
            cls.save_assets(cls.DEFAULT_ASSETS)
            return cls.DEFAULT_ASSETS
    
    @classmethod
    def save_assets(cls, assets: Dict) -> bool:
        """Save assets configuration"""
        try:
            redis_client.set(cls.ASSETS_KEY, json.dumps(assets))
            return True
        except Exception as e:
            print(f"Error saving assets: {e}")
            return False
    
    @classmethod
    def add_asset(cls, symbol: str, name: str) -> Dict:
        """Add new asset"""
        assets = cls.get_assets()
        
        # Check if already exists
        if symbol.upper() in assets:
            return {"error": f"Asset {symbol} already exists"}
        
        # Test if asset has options on Bybit
        if not cls.test_asset(symbol):
            return {"error": f"No options found for {symbol} on Bybit"}
        
        # Add new asset
        assets[symbol.upper()] = {
            "name": name,
            "enabled": True,
            "order": len(assets) + 1,
            "added_date": datetime.now().isoformat()
        }
        
        cls.save_assets(assets)
        return {"success": True, "message": f"Added {symbol}"}
    
    @classmethod
    def test_asset(cls, symbol: str) -> bool:
        """Test if asset has options on Bybit"""
        try:
            url = "https://api.bybit.com/v5/market/instruments-info"
            params = {
                "category": "option",
                "baseCoin": symbol.upper(),
                "limit": 1
            }
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            if data.get("retCode") == 0:
                items = data.get("result", {}).get("list", [])
                return len(items) > 0
            return False
        except:
            return False
    
    @classmethod
    def toggle_asset(cls, symbol: str) -> bool:
        """Enable/disable asset"""
        assets = cls.get_assets()
        if symbol in assets:
            assets[symbol]["enabled"] = not assets[symbol]["enabled"]
            cls.save_assets(assets)
            return True
        return False
    
    @classmethod
    def remove_asset(cls, symbol: str) -> bool:
        """Remove asset (only if not default)"""
        assets = cls.get_assets()
        if symbol in assets and symbol not in cls.DEFAULT_ASSETS:
            del assets[symbol]
            cls.save_assets(assets)
            return True
        return False


class OptionsDataProvider:
    """Provides options data from Redis"""
    
    @staticmethod
    def get_options_data(asset: str = "BTC", expiry: Optional[str] = None, 
                        option_type: Optional[str] = None) -> List[Dict]:
        """Get filtered options data"""
        
        # Get all option keys for the asset
        pattern = f"option:{asset}-*"
        keys = redis_client.keys(pattern)
        
        options_data = []
        for key in keys[:500]:  # Limit for performance
            try:
                # Get data from Redis
                data = redis_client.hgetall(key)
                if not data:
                    continue
                
                # Parse symbol
                symbol = key.replace("option:", "")
                parts = symbol.split("-")
                
                # Filter by expiry if specified
                if expiry and expiry != "all":
                    if len(parts) > 1 and parts[1] != expiry:
                        continue
                
                # Filter by option type if specified
                if option_type and option_type != "all":
                    if option_type == "call" and not symbol.endswith("-C") and not symbol.endswith("-C-USDT"):
                        continue
                    if option_type == "put" and not symbol.endswith("-P") and not symbol.endswith("-P-USDT"):
                        continue
                
                # Format data for display
                options_data.append({
                    "symbol": symbol,
                    "expiry": parts[1] if len(parts) > 1 else "N/A",
                    "strike": parts[2] if len(parts) > 2 else "N/A",
                    "type": "Call" if "-C" in symbol else "Put",
                    "last_price": float(data.get("last_price", 0) or 0),
                    "mark_price": float(data.get("mark_price", 0) or 0),
                    "volume_24h": float(data.get("volume_24h", 0) or 0),
                    "open_interest": float(data.get("open_interest", 0) or 0),
                    "delta": float(data.get("delta", 0) or 0),
                    "gamma": float(data.get("gamma", 0) or 0),
                    "theta": float(data.get("theta", 0) or 0),
                    "vega": float(data.get("vega", 0) or 0),
                    "iv": float(data.get("mark_iv", 0) or 0),
                    "underlying": float(data.get("underlying_price", 0) or 0),
                    "timestamp": float(data.get("timestamp", 0) or 0)
                })
            except Exception as e:
                continue
        
        # Sort by volume
        options_data.sort(key=lambda x: x["volume_24h"], reverse=True)
        
        return options_data
    
    @staticmethod
    def get_expiries(asset: str) -> List[str]:
        """Get unique expiry dates for an asset"""
        pattern = f"option:{asset}-*"
        keys = redis_client.keys(pattern)
        
        expiries = set()
        for key in keys:
            symbol = key.replace("option:", "")
            parts = symbol.split("-")
            if len(parts) > 1:
                expiries.add(parts[1])
        
        return sorted(list(expiries))
    
    @staticmethod
    def get_stats() -> Dict:
        """Get system statistics"""
        try:
            stats = redis_client.hgetall("stats:global")
            db_size = redis_client.dbsize()
            
            return {
                "total_symbols": db_size // 2,  # Rough estimate
                "messages_processed": int(stats.get("messages", 0)),
                "last_update": stats.get("last_update", "N/A"),
                "redis_memory": redis_client.info('memory').get('used_memory_human', 'N/A')
            }
        except:
            return {}


# ==================== ROUTES ====================

@app.route('/')
def index():
    """Main dashboard"""
    assets = AssetManager.get_assets()
    return render_template('dashboard.html', assets=assets)

@app.route('/api/assets')
def get_assets():
    """Get all configured assets"""
    assets = AssetManager.get_assets()
    return jsonify(assets)

@app.route('/api/assets/add', methods=['POST'])
def add_asset():
    """Add new asset"""
    data = request.json
    symbol = data.get('symbol', '').upper()
    name = data.get('name', symbol)
    
    if not symbol:
        return jsonify({"error": "Symbol required"}), 400
    
    result = AssetManager.add_asset(symbol, name)
    
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)

@app.route('/api/assets/<symbol>/toggle', methods=['POST'])
def toggle_asset(symbol):
    """Enable/disable asset"""
    success = AssetManager.toggle_asset(symbol)
    return jsonify({"success": success})

@app.route('/api/assets/<symbol>/remove', methods=['DELETE'])
def remove_asset(symbol):
    """Remove asset"""
    success = AssetManager.remove_asset(symbol)
    if success:
        return jsonify({"success": True})
    return jsonify({"error": "Cannot remove default asset"}), 400

@app.route('/api/options/<asset>')
def get_options(asset):
    """Get options data for specific asset"""
    expiry = request.args.get('expiry', 'all')
    option_type = request.args.get('type', 'all')
    
    data = OptionsDataProvider.get_options_data(asset, expiry, option_type)
    return jsonify(data)

@app.route('/api/expiries/<asset>')
def get_expiries(asset):
    """Get available expiries for an asset"""
    expiries = OptionsDataProvider.get_expiries(asset)
    return jsonify(expiries)

@app.route('/api/stats')
def get_stats():
    """Get system statistics"""
    stats = OptionsDataProvider.get_stats()
    return jsonify(stats)

@app.route('/api/stream')
def stream():
    """Server-sent events for real-time updates"""
    def generate():
        while True:
            # Get current stats
            stats = OptionsDataProvider.get_stats()
            yield f"data: {json.dumps(stats)}\n\n"
            time.sleep(2)  # Update every 2 seconds
    
    return Response(generate(), mimetype="text/event-stream")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)