# Rebuild commands

```bash
# 1. plates (needs the image tool, 25 remain)
python3 gen_keys.py

# 2. picture  (97 shots, 515.0 s, ~20 min on 2 cores)
rm -rf out/segs2 && python3 build_film2.py

# 3. audio    (VO fit + synthesized bed, ~45 s)
python3 build_audio.py
/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2 \
  -y -i out/mix.wav -c:a aac -b:a 192k out/mix.m4a

# 4. final mux (2.39 picture into a 1080p frame)
FF=/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2
$FF -y -i out/picture_full.mp4 -i out/mix.wav \
  -filter_complex "[0:v]scale=1920:1080:flags=lanczos,pad=1920:1080:0:138:black,eq=contrast=1.04:saturation=1.04,fps=30[v]" \
  -map "[v]" -map 1:a -c:v libx264 -preset veryfast -crf 21 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -movflags +faststart -shortest out/EP01_bear_FINAL.mp4
```
