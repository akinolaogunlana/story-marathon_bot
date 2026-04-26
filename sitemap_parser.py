import xml.etree.ElementTree as ET
import aiohttp
from urllib.parse import urlparse
from typing import List
import logging

logger = logging.getLogger(__name__)

async def fetch_sitemap_stories(sitemap_url: str, target_domain: str) -> List[str]:
    """Fetch and parse story URLs from Supabase sitemap"""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(sitemap_url, timeout=30) as response:
                if response.status == 200:
                    content = await response.text()
                    root = ET.fromstring(content)
                    ns = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
                    
                    stories = []
                    for loc in root.findall('.//sitemap:loc', ns):
                        url = loc.text
                        if url and 'story' in url.lower() and target_domain in url:
                            stories.append(url)
                    
                    logger.info(f"Found {len(stories)} stories")
                    return list(set(stories))  # Remove duplicates
        except Exception as e:
            logger.error(f"Sitemap fetch failed: {e}")
    return []