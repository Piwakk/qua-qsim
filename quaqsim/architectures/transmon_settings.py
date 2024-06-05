from dataclasses import dataclass
from dataclasses_json import dataclass_json

from typing import Optional


@dataclass_json
@dataclass
class TransmonSettings:
    resonant_frequency: float
    anharmonicity: float
    rabi_frequency: float
    resonator: Optional[float] = None
    coupling_rate: Optional[float] = None
