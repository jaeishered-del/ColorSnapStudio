from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import uuid
from .colors import normalize_hex, suggest_name

@dataclass
class ColorEntry:
    hex: str; name: str = ""
    def __post_init__(self):
        self.hex=normalize_hex(self.hex)
        if not self.name: self.name=suggest_name(self.hex)
    def to_dict(self): return {"hex":self.hex,"name":self.name}
    @classmethod
    def from_dict(cls,d):
        if not isinstance(d,dict) or "hex" not in d: raise ValueError("Color entry missing 'hex'")
        return cls(hex=str(d["hex"]), name=str(d.get("name","")))

@dataclass
class Palette:
    name: str = "Untitled Palette"
    colors: list[ColorEntry] = field(default_factory=list)
    source_image: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    def to_dict(self): return {"id":self.id,"name":self.name,"created_at":self.created_at,"source_image":self.source_image,"colors":[c.to_dict() for c in self.colors]}
    @classmethod
    def from_dict(cls,d):
        if not isinstance(d,dict): raise ValueError("Palette must be an object")
        colors=[ColorEntry.from_dict(c) for c in d.get("colors",[])]
        return cls(name=str(d.get("name","Untitled Palette")), colors=colors, source_image=d.get("source_image"), created_at=str(d.get("created_at", datetime.now(timezone.utc).isoformat())), id=str(d.get("id") or uuid.uuid4()))
