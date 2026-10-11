"""Recover the original WindowManager click effect from read-only Unity assets."""
from pathlib import Path
from extract_slots_dealers import spine
root=Path(__file__).resolve().parents[1]
source=Path.home()/'Downloads/Decomp files/unity/Assets/hotres/spine/touch'
spine(source,root/'web/assets/spine/fx_dianji')
