# Weather backgrounds

One dark, royalty-free image per WMO condition category, committed to the repo
and served statically. The dashboard layers the matching image behind the main
panel with a dark scrim. If an image file is missing, the UI falls back to a
per-category gradient automatically, so the app works before these are added.

Expected files (each ~1600x1200 or larger, dark, landscape):

- `clear.jpg`
- `cloudy.jpg`
- `fog.jpg`
- `drizzle.jpg`
- `rain.jpg`
- `snow.jpg`
- `thunderstorm.jpg`

Filenames must match the condition category values exactly (lowercase).
