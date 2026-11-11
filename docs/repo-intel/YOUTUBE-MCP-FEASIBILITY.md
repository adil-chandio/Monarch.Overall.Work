# YouTube MCP feasibility

## What MCP can and cannot do
MCP is a protocol connecting an agent to tools, not a video host or independent permission grant. Capabilities come from the specific server and its providers. A tool name that mentions YouTube or video does not prove it returns actual frames, or that it will play in this environment.

## Specific candidates reviewed
- [ytlens](https://github.com/Makkov-design/ytlens/tree/a25c43c3e4db3a8ff9dfc352bde4ccf97868a490): uses Google's Gemini API with public YouTube URLs to obtain model-generated analysis of visual samples and audio. Supports start/end windows. This is a provider-produced description, not raw frame export or independently verified every-frame viewing. API access/quota required.
- [mcp-video-analyzer](https://github.com/guimatheus92/mcp-video-analyzer/tree/099f602b393fdb6e39798b2624305f64fdf6b074): advertises frame bursts, timestamps, transcript and OCR, and accepts local files; README says YouTube input routes through yt-dlp. Not tested here; it is not evidence the earlier runner verification challenge is resolved. Review source, dependencies and rights before use.
- [youtube-hybrid-mcp](https://github.com/jackc1111/youtube-hybrid-mcp/tree/c29a07ce77d77088516069f1ed08660e8dc22db7): README documents YouTube Data API for metadata/comments and yt-dlp for captions; no evidence of frame-by-frame extraction. Useful for discovery, not visual forensic coverage.

## Local MCP protocol check performed
Installed published `ytlens@1.1.0` temporarily with `npm --ignore-scripts`; actual `initialize` and `tools/list` JSON-RPC requests succeeded on Node 22 with a **synthetic placeholder used locally only**. Server listed `summarize_youtube_video`, `ask_about_youtube_video`, `extract_key_moments`, `get_video_transcript` and `list_supported_models`. The same installed version exited at startup when no key was set. No video-analysis tool was called and no data was sent to Google. This proves protocol startup/tool discovery, **not actual footage access**. Server is not registered as an Arena connected tool merely because it can run as a local process.

## Blocker and next check
Our existing authenticated GitHub Action's Google endpoint diagnostic is in `yt-official-video-probe.json`. Most recent recorded result returned HTTP 403 PERMISSION_DENIED with reason ACCESS_DENIED; an earlier run returned SERVICE_DISABLED. The actual configured project/API access needs administrator review; do not paste or request credentials in chat. After authorized access is configured, run one short target with visual timestamped queries and compare responses with independently accessible evidence, recording cost and sampling settings. Google documents default 1 fps sampling, not original-frame exports. The exact frame-coverage route remains authorized source file + decoded frame/PTS verification. Respect YouTube terms and media rights for downloading, retention and reuse.
