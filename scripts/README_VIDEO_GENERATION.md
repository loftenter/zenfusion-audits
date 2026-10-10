# HeyGen Video Generation via OpenRouter

Generate professional videos using HeyGen Video 1.0 API through OpenRouter.

## Quick Start

### Option 1: Direct CLI (fastest for one-off videos)

```bash
cd ~/.hermes/scripts
python3 generate_video.py "A 10-second product demo of PEX fittings rotating with soft lighting" --output ~/Desktop/pex_demo.mp4
```

### Option 2: Prompt Hermes (easiest, fully automated)

Just say:
```
"Generate a video: 15-second water softener installation demo with voiceover"
```

Hermes will automatically detect video requests and:
1. Call the HeyGen API
2. Poll until rendering completes
3. Download to your Desktop (or upload to Google Drive if requested)

**No keyword needed** - natural language works. Examples:
- "Make a video showing PEX installation"
- "Create a 30-second brand video for SoftPro"
- "Generate product showcase: rotating water filter, 10 seconds"

## Pricing

**$0.015 per second** (50% launch discount)
- 5-second clip: $0.075
- 10-second demo: $0.15
- 30-second tutorial: $0.45
- 60-second full video: $0.90

## CLI Reference

```bash
python3 generate_video.py "<prompt>" [OPTIONS]

Required:
  prompt              Text description of the desired video

Options:
  --duration N        Video length in seconds (5-15, default 10)
  --output PATH       Output file path (default: heygen_video_<timestamp>.mp4)
  --seed N            Random seed for reproducibility
  --quiet, -q         Suppress progress messages (just print path)

Examples:
  python3 generate_video.py "A 10-second PEX fitting product showcase"
  python3 generate_video.py "30-second install tutorial" --duration 10 --output demo.mp4
  python3 generate_video.py "Rotating water softener" --seed 42 --quiet
```

## Video Capabilities

HeyGen Video 1.0 is a **general-purpose video generation model** (NOT an avatar/talking-head product).

**What it does well:**
- Product demos with motion (rotating equipment, installation steps)
- Equipment showcases (close-ups, 3D-style rotation)
- Brand moments (lifestyle, workspace, tools in action)
- Training/onboarding content (process visuals, step-by-step)
- Short-form business video (5-15 seconds)

**Synthesized audio included:**
- Dialogue (if you describe it in the prompt)
- Ambient sound effects (workshop noise, water running, etc.)
- Background music (if specified)

**Input options:**
- Text prompt alone (most common)
- First-frame image (to control starting composition)
- Image/video/audio references (advanced)

## Prompt Tips

**Good prompts are specific about:**
1. **Duration**: "A 10-second..." or "15-second..."
2. **Subject**: "PEX pipe fittings" not "products"
3. **Motion**: "rotating slowly" / "hands installing" / "camera pans across"
4. **Setting**: "white background, soft studio lighting" / "workshop setting"
5. **Audio** (optional): "with upbeat background music" / "narrator explaining steps"

**Examples:**

✅ **Good:**
```
"A 10-second clip: chrome PEX pipe fittings rotating slowly on a white background 
with soft studio lighting and close-up detail shots"
```

❌ **Too vague:**
```
"Show PEX products"
```

✅ **Good with audio:**
```
"15-second installation demo: hands connecting PEX fittings with crimp tool, 
workshop setting, narrator voice explaining 'crimp the fitting until you hear a click'"
```

## Requirements

- **OpenRouter API key** in `~/.hermes/.env`:
  ```bash
  OPENROUTER_API_KEY=sk-or-v1-...
  ```
- Python 3.7+
- `requests` library (usually pre-installed)

## Technical Details

- **Model:** `heygen/heygen-video-1`
- **Endpoint:** `POST https://openrouter.ai/api/v1/videos`
- **Polling:** Job-based async (submit → poll → download)
- **Latency:** P50 ~14.6 seconds end-to-end
- **Uptime:** 94% availability (3-day average)
- **Output format:** MP4 video file

## VPS / Team Usage

The script is in the **shared `loftenter/zenfusion-audits` repo** under `scripts/`:

```bash
# On VPS (Raj's Hermes instance)
cd ~/zenfusion-audits/scripts
python3 generate_video.py "Your prompt here" --output video.mp4
```

Or just prompt Hermes naturally - it will detect video requests and use this wrapper automatically.

## Troubleshooting

**"Missing Authentication header"**
- Ensure `OPENROUTER_API_KEY` is set in `~/.hermes/.env`

**"Video generation failed"**
- Check prompt length (keep under 500 chars)
- Ensure duration is 5-15 seconds
- Try again (occasional provider errors)

**Timeout after 5 minutes**
- Video took too long to render (rare)
- Job might still complete - check OpenRouter dashboard

**"Download failed"**
- Network issue - retry the same job ID manually:
  ```bash
  curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
    https://openrouter.ai/api/v1/videos/<JOB_ID>/content \
    -o video.mp4
  ```

## Cost Tracking

Every generation prints the cost:
```
✓ Video saved: demo.mp4
   Size: 703.4 KB
   Cost: $0.150
```

Check OpenRouter dashboard for monthly usage: https://openrouter.ai/activity

## Support

- OpenRouter docs: https://openrouter.ai/docs/guides/overview/multimodal/video-generation
- HeyGen model page: https://openrouter.ai/heygen/heygen-video-1
- Hermes support: Ask in chat or check ~/.hermes/scripts/generate_video.py source

---

**Last updated:** Oct 10, 2026  
**Author:** Hermes Agent (Nous Research)  
**License:** MIT
