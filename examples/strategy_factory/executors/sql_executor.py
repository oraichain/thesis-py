from typing import Any, Dict, List
from datetime import datetime, timedelta
import random


async def execute_sql(query: str, input_data: Any = None) -> List[Dict[str, Any]]:
    """
    Mock SQL execution for demo purposes.
    Returns mock data based on the query pattern.

    Args:
        query: SQL query string (used to determine what type of data to return)
        input_data: Optional input data (not used in mock)

    Returns:
        List of dictionaries representing mock query results
    """
    try:
        # Simple pattern matching to determine what data to return
        query_lower = query.lower()

        # Check if this is a crypto_prices query
        if 'crypto_prices' in query_lower or 'price' in query_lower:
            mock_data = []
            base_date = datetime.now()
            for i in range(30):
                date = base_date - timedelta(days=29 - i)
                mock_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'symbol': 'SOL',
                    'price': round(100 + random.uniform(-20, 30), 2),
                    'volume': round(random.uniform(1000000, 5000000), 2),
                    'market_cap': round(random.uniform(40000000000, 60000000000), 2)
                })
            return mock_data

        # Check if this is a twitter_sentiment query
        elif 'twitter_sentiment' in query_lower or 'sentiment' in query_lower:
            mock_data = []
            sentiments = ['bullish', 'bearish', 'neutral']
            themes = ['staking', 'DeFi', 'NFTs', 'scalability', 'ecosystem growth']
            base_date = datetime.now()
            for i in range(30):
                timestamp = base_date - timedelta(days=29 - i)
                mock_data.append({
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'symbol': 'SOL',
                    'sentiment': random.choice(sentiments),
                    'sentiment_score': round(random.uniform(-1, 1), 2),
                    'key_theme': random.choice(themes),
                    'discussion_volume': random.choice(['high', 'medium', 'low']),
                    'influencer_count': random.randint(5, 50)
                })
            return mock_data

        # Default: return empty result
        else:
            return []

    except Exception as e:
        raise Exception(f"SQL execution error: {str(e)}")
