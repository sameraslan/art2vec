"""By-eye follow-up: does keeping the overall tint (sca) look more like colour than removing it (std)?"""
import importlib.util
import sys

import fz

spec = importlib.util.spec_from_file_location("cp", fz.HERE / "03_colour_pick.py")
cp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cp)
cp.FINALISTS = {
    "B palette, tint removed (sog,std)": (["hist_sog_std", "sw_sog_std"], "frame", 64, True),
    "H palette, tint kept (sog,sca)": (["hist_sog_sca", "sw_sog_sca"], "frame", 64, True),
    "I palette, tint kept, no adaptation (raw,sca)": (["hist_raw_sca", "sw_raw_sca"], "frame", 64, True),
    "J both (std + sca)": (["hist_sog_std", "sw_sog_std", "hist_raw_sca", "sw_raw_sca"], "frame", 64, True),
    "C tone bands + hue families": (["tb8_std", "hue12_cen"], "frame", 32, True),
}
cp.SEEDS = ["Q45585", "Q1044742", "Q151047", "Q2339059", "Q18683017", "Q969377"]
_sheet = cp.blocks.sheet
cp.blocks.sheet = lambda path, rows, **kw: _sheet(str(path).replace("colour_sheet_", "tint_sheet_"), rows, **kw)
_dump = fz.dump
fz.dump = lambda obj, name: _dump(obj, name.replace("colour_sheets", "tint_sheets").replace("colour_source", "tint_source"))
cp.sheets()
cp.source()
