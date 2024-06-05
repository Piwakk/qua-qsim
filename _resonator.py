import numpy as np
from qm.qua import program, declare, for_, measure, wait
from qualang_tools.units import unit

from quaqsim import simulate_program
from quaqsim.architectures.from_qua_channels import (
    ChannelType,
    TransmonPairBackendChannelIQ,
    TransmonPairBackendChannelReadout,
)
from quaqsim.architectures.resonator import Resonator
from quaqsim.architectures.resonator_settings import ResonatorSettings
from quaqsim.architectures.transmon import Transmon
from quaqsim.architectures.transmon_pair_backend_from_qua import (
    TransmonPairBackendFromQUA,
)
from quaqsim.architectures.transmon_settings import TransmonSettings

u = unit(coerce_to_integer=True)

###########
# PROGRAM #
###########

depletion_time = 2 * u.us
n_avg = 10

with program() as prog:
    n = declare(int)
    with for_(n, 0, n < n_avg, n + 1):
        measure("readout", "resonator", None)
        wait(depletion_time * u.ns, "resonator")

##########
# CONFIG #
##########


def build_config(resonator_LO, resonator_IF):
    readout_len = 5000
    readout_amp = 0.2
    time_of_flight = 24

    return {
        "version": 1,
        "controllers": {
            "con1": {
                "analog_outputs": {
                    1: {"offset": 0.0},  # I resonator
                    2: {"offset": 0.0},  # Q resonator
                },
                "digital_outputs": {},
                "analog_inputs": {
                    1: {"offset": 0.0, "gain_db": 0},  # I from down-conversion
                    2: {"offset": 0.0, "gain_db": 0},  # Q from down-conversion
                },
            },
        },
        "elements": {
            "resonator": {
                "RF_inputs": {"port": ("octave1", 1)},
                "RF_outputs": {"port": ("octave1", 1)},
                "intermediate_frequency": resonator_IF,
                "operations": {
                    "readout": "readout_pulse",
                },
                "time_of_flight": time_of_flight,
                "smearing": 0,
            },
        },
        "octaves": {
            "octave1": {
                "RF_outputs": {
                    1: {
                        "LO_frequency": resonator_LO,
                        "LO_source": "internal",
                        "output_mode": "always_on",
                        "gain": 0,
                    },
                },
                "RF_inputs": {
                    1: {
                        "LO_frequency": resonator_LO,
                        "LO_source": "internal",
                    },
                },
                "connectivity": "con1",
            }
        },
        "pulses": {
            "readout_pulse": {
                "operation": "measurement",
                "length": readout_len,
                "waveforms": {
                    "I": "readout_wf",
                    "Q": "zero_wf",
                },
                "integration_weights": {
                    "cos": "cosine_weights",
                    "sin": "sine_weights",
                    "minus_sin": "minus_sine_weights",
                },
                "digital_marker": "ON",
            },
        },
        "waveforms": {
            "zero_wf": {"type": "constant", "sample": 0.0},
            "readout_wf": {"type": "constant", "sample": readout_amp},
        },
        "digital_waveforms": {
            "ON": {"samples": [(1, 0)]},
        },
    }


###############
# CHANNEL MAP #
###############

resonator_settings = ResonatorSettings(
    resonant_frequency=5860000000.0,
)
resonator = Resonator(resonator_settings)
transmon_settings = TransmonSettings(
    resonant_frequency=4860000000.0,
    anharmonicity=-320000000.0,
    rabi_frequency=3e7,
    resonator=resonator,
    coupling_rate=1,
)
transmon = Transmon(transmon_settings)

channel_map = {
    "qubit": TransmonPairBackendChannelIQ(
        qubit_index=0,
        carrier_frequency=transmon.resonant_frequency,
        operator_i=transmon.drive_operator(quadrature="I"),
        operator_q=transmon.drive_operator(quadrature="Q"),
        type=ChannelType.DRIVE,
    ),
    "resonator": TransmonPairBackendChannelReadout(0),
}


###########
# BACKEND #
###########

backend = TransmonPairBackendFromQUA(transmon, channel_map)

###########
# PROGRAM #
###########

f_min = 30 * u.MHz
f_max = 70 * u.MHz
df = 1.0 * u.MHz

f_LO = 5.5 * u.GHz

for f_IF in np.arange(f_min, f_max + 0.1, df):
    print(f_IF)
    resonator_config = build_config(f_LO, f_IF)

    results = simulate_program(
        qua_program=prog,
        qua_config=resonator_config,
        qua_config_to_backend_map=channel_map,
        backend=backend,
        num_shots=100,
    )
    print(results)
