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

from __future__ import annotations

import cirq
import cirq.transformers


def test_insertion_sort() -> None:
    c = cirq.Circuit(
        cirq.CZ(cirq.q(2), cirq.q(1)),
        cirq.CZ(cirq.q(2), cirq.q(4)),
        cirq.CZ(cirq.q(0), cirq.q(1)),
        cirq.CZ(cirq.q(2), cirq.q(1)),
        cirq.GlobalPhaseGate(1j).on(),
    )
    sorted_circuit = cirq.transformers.insertion_sort_transformer(c)
    assert sorted_circuit == cirq.Circuit(
        cirq.GlobalPhaseGate(1j).on(),
        cirq.CZ(cirq.q(0), cirq.q(1)),
        cirq.CZ(cirq.q(2), cirq.q(1)),
        cirq.CZ(cirq.q(2), cirq.q(1)),
        cirq.CZ(cirq.q(2), cirq.q(4)),
    )
