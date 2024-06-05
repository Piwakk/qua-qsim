import numpy as np
from .operators import N, ident, a, adag, a0dag, a1, a1dag, a0, N1, full_ident
from .transmon_settings import TransmonSettings


class Transmon:
    def __init__(self, settings: TransmonSettings):
        if settings.resonator is not None and settings.coupling_rate is None:
            raise ValueError(
                "If resonator is specified, coupling_rate must be specified as well."
            )

        self.settings = settings
        self.resonant_frequency = settings.resonant_frequency
        self.rabi_frequency = settings.rabi_frequency
        self.anharmonicity = settings.anharmonicity
        self.resonator = settings.resonator
        self.coupling_rate = settings.coupling_rate

    def system_hamiltonian(self) -> np.ndarray:
        if self.resonator is None:
            return 2 * np.pi * self.resonant_frequency * N + np.pi * self.anharmonicity * N * (N - ident)

        # 1 is the transmon, 0 is the resonator.
        h_transmon = 2 * np.pi * self.resonant_frequency * N1 + np.pi * self.anharmonicity * N1 * (N1 - full_ident)
        h_resonator = np.kron(ident, self.resonator.system_hamiltonian())
        h_coupling = self.coupling_rate * (a0dag @ a1 + a1dag @ a0)
        return h_transmon + h_resonator + h_coupling


    def drive_operator(self, quadrature="I") -> np.ndarray:
        if quadrature == "I":
            operator = 2 * np.pi * self.rabi_frequency * (a + adag)
            return operator if self.resonator is None else np.kron(operator, ident)
        elif quadrature == "Q":
            operator = 2 * 1j * np.pi * self.rabi_frequency * (a - adag)
            return operator if self.resonator is None else np.kron(operator, ident)
        else:
            raise NotImplementedError(f"Expected quadrature to be I or Q, got {quadrature}")
