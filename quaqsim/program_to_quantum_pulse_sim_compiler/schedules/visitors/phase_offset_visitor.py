from qiskit import pulse

from quaqsim.program_to_quantum_pulse_sim_compiler.schedules.context import Context
from quaqsim.program_to_quantum_pulse_sim_compiler.schedules.phase_offset import PhaseOffset
from quaqsim.program_to_quantum_pulse_sim_compiler.schedules.visitors.visitor import Visitor


class PhaseOffsetVisitor(Visitor):
    def visit(self, instruction: PhaseOffset, instruction_context: Context):
        pulse.shift_phase(instruction.phase, instruction_context.timeline.pulse_channel)
