"""
Web crawler using Playwright for image acquisition.

This module provides a WebCrawler class that uses Playwright
to search and download images from the web.
"""

from typing import Optional
import asyncio
from pathlib import Path
import hashlib

from playwright.async_api import async_playwright, Browser, Page

from app.core.config import settings
from app.core.logging_config import get_logger
from app.tools.supabase_client import SupabaseClient

logger = get_logger(__name__)


class WebCrawler:
    """
    Web crawler for image acquisition.
    
    Uses Playwright to automate browser interactions and download images
    from search engines based on generated queries.
    """

    def __init__(self, supabase_client: Optional[SupabaseClient] = None) -> None:
        """
        Initialize the web crawler.
        
        Args:
            supabase_client: Optional SupabaseClient instance for file uploads
        """
        self.supabase_client = supabase_client or SupabaseClient()
        logger.info("WebCrawler initialized")

    async def crawl_images(
        self,
        queries: list[str],
        limit: int = 10,
        job_id: Optional[str] = None
    ) -> list[str]:
        """
        Crawl images based on search queries.
        
        This method searches for images using the provided queries,
        downloads them, and uploads to Supabase storage.
        
        Args:
            queries: List of search queries
            limit: Maximum number of images to download per query
            job_id: Optional job ID for organizing files
            
        Returns:
            List of uploaded image URLs
        """
        try:
            logger.info(f"Starting image crawl with {len(queries)} queries")
            
            all_image_urls: list[str] = []
            
            async with async_playwright() as p:
                # Launch browser
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                               "AppleWebKit/537.36 (KHTML, like Gecko) "
                               "Chrome/120.0.0.0 Safari/537.36"
                )
                
                for query in queries:
                    logger.info(f"Searching for: {query}")
                    
                    try:
                        # Search and download images for this query
                        image_urls = await self._search_and_download(
                            context=context,
                            query=query,
                            limit=limit,
                            job_id=job_id
                        )
                        all_image_urls.extend(image_urls)
                        
                        # Add delay to avoid rate limiting
                        await asyncio.sleep(2)
                        
                    except Exception as e:
                        logger.error(f"Failed to crawl for query '{query}': {e}")
                        continue
                
                await browser.close()
            
            logger.info(f"Crawled {len(all_image_urls)} images in total")
            return all_image_urls[:settings.max_crawl_images]
            
        except Exception as e:
            logger.error(f"Failed to crawl images: {e}", exc_info=True)
            raise

    async def _search_and_download(
        self,
        context: any,
        query: str,
        limit: int,
        job_id: Optional[str] = None
    ) -> list[str]:
        """
        Search for images using a search engine and download them.
        
        This is a simplified implementation. In production, you would
        implement specific logic for different search engines or image sources.
        
        Args:
            context: Playwright browser context
            query: Search query
            limit: Maximum number of images
            job_id: Optional job ID
            
        Returns:
            List of uploaded image URLs
        """
        page = await context.new_page()
        uploaded_urls: list[str] = []
        
        try:
            # Example: Using Bing Image Search
            # In production, consider using official APIs or multiple sources
            search_url = f"https://www.bing.com/images/search?q={query}"
            await page.goto(search_url, wait_until="networkidle")
            
            # Wait for images to load
            await page.wait_for_selector("img.mimg", timeout=10000)
            
            # Get image elements
            image_elements = await page.query_selector_all("img.mimg")
            
            for i, img_elem in enumerate(image_elements[:limit]):
                if i >= limit:
                    break
                    
                try:
                    # Get image source URL
                    img_src = await img_elem.get_attribute("src")
                    
                    if not img_src or img_src.startswith("data:"):
                        continue
                    
                    # Download image
                    image_data = await self._download_image(page, img_src)
                    
                    if not image_data:
                        continue
                    
                    # Generate unique filename
                    file_hash = hashlib.md5(image_data).hexdigest()[:12]
                    file_path = f"crawled/{job_id or 'default'}/{query}_{i}_{file_hash}.jpg"
                    
                    # Upload to Supabase
                    url = await self.supabase_client.upload_file(
                        bucket="images",
                        file_path=file_path,
                        file_data=image_data,
                        content_type="image/jpeg"
                    )
                    
                    uploaded_urls.append(url)
                    logger.info(f"Downloaded and uploaded image {i+1}/{limit} for query: {query}")
                    
                    # Small delay between downloads
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.warning(f"Failed to download image {i}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Search and download failed for '{query}': {e}")
            
        finally:
            await page.close()
        
        return uploaded_urls

    async def _download_image(self, page: Page, url: str) -> Optional[bytes]:
        """
        Download image from URL.
        
        Args:
            page: Playwright page instance
            url: Image URL
            
        Returns:
            Image data as bytes or None if failed
        """
        try:
            # Navigate to image URL
            response = await page.goto(url, wait_until="load", timeout=15000)
            
            if not response or response.status != 200:
                return None
            
            # Get image data
            image_data = await response.body()
            
            # Basic validation
            if len(image_data) < 1024:  # Too small, likely not a valid image
                return None
            
            return image_data
            
        except Exception as e:
            logger.warning(f"Failed to download image from {url}: {e}")
            return None


