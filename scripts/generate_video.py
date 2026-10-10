#!/usr/bin/env python3
"""
HeyGen Video Generator via OpenRouter
Generates videos using HeyGen Video 1.0 API through OpenRouter

Usage:
    python3 generate_video.py "A 10-second product demo of PEX fittings" --output ~/Desktop/demo.mp4
    python3 generate_video.py "30-sec installation tutorial" --duration 30 --output video.mp4

Pricing: $0.015/second (e.g., 60-second video = $0.90)

Requires:
    - OPENROUTER_API_KEY in ~/.hermes/.env
    - Internet connection
"""

import os
import sys
import json
import time
import argparse
import requests
from pathlib import Path
from typing import Optional, Dict, Any


class HeyGenVideoGenerator:
    """HeyGen Video 1.0 API wrapper via OpenRouter"""
    
    BASE_URL = "https://openrouter.ai/api/v1"
    MODEL = "heygen/heygen-video-1"
    DEFAULT_DURATION = 10  # seconds
    POLL_INTERVAL = 3  # seconds
    MAX_WAIT = 300  # 5 minutes
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the video generator
        
        Args:
            api_key: OpenRouter API key (reads from env if not provided)
        """
        self.api_key = api_key or self._load_api_key()
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment or ~/.hermes/.env")
    
    def _load_api_key(self) -> Optional[str]:
        """Load API key from environment or .env file"""
        # Try environment first
        if "OPENROUTER_API_KEY" in os.environ:
            return os.environ["OPENROUTER_API_KEY"]
        
        # Try .env file
        env_path = Path.home() / ".hermes" / ".env"
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("OPENROUTER_API_KEY="):
                        return line.split("=", 1)[1].strip()
        
        return None
    
    def generate(
        self,
        prompt: str,
        duration: Optional[int] = None,
        output_path: Optional[str] = None,
        seed: Optional[int] = None,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a video from a text prompt
        
        Args:
            prompt: Text description of the desired video
            duration: Length in seconds (5-15, default 10)
            output_path: Where to save the video (optional)
            seed: Random seed for reproducibility (optional)
            verbose: Print progress messages
        
        Returns:
            Dict with 'video_path', 'cost', 'duration', 'job_id'
        """
        if verbose:
            print(f"🎬 Generating video with HeyGen Video 1.0...")
            print(f"   Prompt: {prompt}")
            if duration:
                print(f"   Duration: {duration} seconds")
        
        # Submit generation request
        job_id = self._submit_generation(prompt, duration, seed)
        
        if verbose:
            print(f"   Job ID: {job_id}")
            print(f"   Status: Rendering...")
        
        # Poll until complete
        result = self._poll_until_complete(job_id, verbose)
        
        # Download video
        video_bytes = self._download_video(job_id)
        
        # Save to file
        if not output_path:
            timestamp = int(time.time())
            output_path = f"heygen_video_{timestamp}.mp4"
        
        output_path = Path(output_path).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            f.write(video_bytes)
        
        if verbose:
            print(f"✓ Video saved: {output_path}")
            print(f"   Size: {len(video_bytes) / 1024:.1f} KB")
            print(f"   Cost: ${result.get('usage', {}).get('cost', 0):.3f}")
        
        return {
            'video_path': str(output_path),
            'cost': result.get('usage', {}).get('cost', 0),
            'duration': duration or self.DEFAULT_DURATION,
            'job_id': job_id,
            'size_bytes': len(video_bytes)
        }
    
    def _submit_generation(
        self,
        prompt: str,
        duration: Optional[int] = None,
        seed: Optional[int] = None
    ) -> str:
        """Submit video generation request"""
        payload = {
            "model": self.MODEL,
            "prompt": prompt
        }
        
        if duration:
            if not 5 <= duration <= 15:
                raise ValueError(f"Duration must be 5-15 seconds, got {duration}")
            payload["duration"] = duration
        
        if seed is not None:
            payload["seed"] = seed
        
        response = requests.post(
            f"{self.BASE_URL}/videos",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://loftenter.github.io"
            },
            json=payload,
            timeout=30
        )
        
        if response.status_code != 202:
            raise RuntimeError(f"Generation failed: {response.status_code} {response.text}")
        
        data = response.json()
        return data["id"]
    
    def _poll_until_complete(self, job_id: str, verbose: bool = True) -> Dict[str, Any]:
        """Poll job status until complete or failed"""
        start_time = time.time()
        
        while time.time() - start_time < self.MAX_WAIT:
            response = requests.get(
                f"{self.BASE_URL}/videos/{job_id}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=30
            )
            
            if response.status_code != 200:
                raise RuntimeError(f"Polling failed: {response.status_code} {response.text}")
            
            data = response.json()
            status = data.get("status", "unknown")
            
            if status == "completed":
                return data
            elif status in ("failed", "cancelled", "expired"):
                raise RuntimeError(f"Video generation {status}: {data.get('error', 'Unknown error')}")
            
            if verbose:
                elapsed = int(time.time() - start_time)
                print(f"   Status: {status} (elapsed: {elapsed}s)", end='\r')
            
            time.sleep(self.POLL_INTERVAL)
        
        raise TimeoutError(f"Video generation timed out after {self.MAX_WAIT}s")
    
    def _download_video(self, job_id: str) -> bytes:
        """Download the generated video"""
        response = requests.get(
            f"{self.BASE_URL}/videos/{job_id}/content",
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=60
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"Download failed: {response.status_code}")
        
        return response.content


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(
        description="Generate videos using HeyGen Video 1.0 via OpenRouter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 generate_video.py "A 10-second product demo of PEX fittings"
  python3 generate_video.py "30-sec install tutorial" --duration 10 --output demo.mp4
  python3 generate_video.py "Rotating water softener" --seed 42 --output softener.mp4

Pricing: $0.015/second (10-second video = $0.15, 60-second = $0.90)
        """
    )
    
    parser.add_argument(
        "prompt",
        help="Text description of the desired video"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=None,
        help="Video length in seconds (5-15, default 10)"
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Output file path (default: heygen_video_<timestamp>.mp4)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility"
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress progress messages"
    )
    
    args = parser.parse_args()
    
    try:
        generator = HeyGenVideoGenerator()
        result = generator.generate(
            prompt=args.prompt,
            duration=args.duration,
            output_path=args.output,
            seed=args.seed,
            verbose=not args.quiet
        )
        
        if args.quiet:
            print(result['video_path'])
        
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
