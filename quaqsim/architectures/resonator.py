import numpy as np
from .operators import N
from .resonator_settings import ResonatorSettings


class Resonator:
    def __init__(self, settings: ResonatorSettings):
        self.settings = settings
        self.resonant_frequency = settings.resonant_frequency

    def system_hamiltonian(self) -> np.ndarray:
        return 2 * np.pi * self.resonant_frequency * N
