# Emoji font vendoring

## Task
Vendor the color-emoji font, mirroring exactly how MaterialIcons-Regular.ttf was
vendored in `render/kivy_kit.py`.

## Finding: code already wired, files were missing
`kivy_kit.py` (lines 164-166) already used the `_first_existing(vendored, os_path)`
pattern for the emoji font, identical in shape to `_ICON_TTF` (lines 46-48):

```python
_EMOJI_TTF = _first_existing(
    os.path.join(_ASSETS, "NotoColorEmoji.ttf"),
    "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf")
```

So **no kivy_kit.py edit was needed** — `git diff` on the file is empty. The gap was
that `render/assets/NotoColorEmoji.ttf` and its license simply didn't exist yet, so
`_first_existing` was always falling through to the OS path.

## Files copied
- `render/assets/NotoColorEmoji.ttf` (11,020,136 bytes)
  - copied from `/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf`
- `render/assets/NotoColorEmoji-LICENSE.txt`
  - provenance: `dpkg -S /usr/share/fonts/truetype/noto/NotoColorEmoji.ttf` →
    owning package `fonts-noto-color-emoji`
  - copied from `/usr/share/doc/fonts-noto-color-emoji/copyright` (5,087 bytes)
  - same pattern as `MaterialIcons-LICENSE.txt` (also a copied Debian `copyright` file)

## Verification
- `xvfb-run python3 run_app.py WorkoutWarmupScreen` →
  `layout_inspect/shots/emoji_vendored0001.png`. Visual check: dancer, sun,
  gymnast/dynamic-movement figure, boxing glove, cyclist, walker, and runner all
  render as full-color emoji glyphs (not tofu/boxes, not monochrome) — confirms
  the vendored NotoColorEmoji.ttf is being loaded and rasterized correctly via the
  PIL fallback path (`_emoji_pil_font` / `_draw_emoji`).
- `python3 interact.py`:
  `INTERACT: 515 fired, 515 ok, 0 failures across 27 screens` — 0 failures, no
  regressions (re-run 2026-07-05 after re-verification).

## Files touched
- New: `render/assets/NotoColorEmoji.ttf`, `render/assets/NotoColorEmoji-LICENSE.txt`
- `render/kivy_kit.py`: no change (pattern was already correct)
- New: `layout_inspect/shots/emoji_vendored0001.png` (verification screenshot)
