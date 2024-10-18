# Copyright 2024 The Cirq Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Transformer that sorts commuting operations in increasing order of their `.qubits` tuple."""

from typing import Optional, TYPE_CHECKING, List

from cirq import protocols, circuits
from cirq.transformers import transformer_api

if TYPE_CHECKING:
    import cirq


@transformer_api.transformer(add_deep_support=True)
def insertion_sort_transformer(
    circuit: 'cirq.AbstractCircuit', *, context: Optional['cirq.TransformerContext'] = None
) -> 'cirq.Circuit':
    """Sorts the operations using their `.qubits` property as comparison key.

    Operations are swapped only if they commute.

    Args:
        circuit: input circuit.
        context: optional TransformerContext (not used),
    """
    final_operations: List['cirq.Operation'] = []
    sorted_qubits: Dict[int, List['cirq.Qid']] = {}
    for pos, op in enumerate(circuit.all_operations()):
        op_qubits = sorted_qubits[id(op)] = sorted(op.qubits)
        for tail_op in reversed(final_operations):
            tail_qubits = sorted_qubits[id(tail_op)]
            if op_qubits < tail_qubits and protocols.commutes(tail_op, op, default=False):
                pos -= 1
                continue
            break
        final_operations.insert(pos, op)
    return circuits.Circuit(final_operations)
