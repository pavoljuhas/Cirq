# Copyright 2020 The Cirq Developers
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

"""An immutable version of the Circuit data structure."""

from __future__ import annotations

from functools import cached_property
from types import NotImplementedType
from typing import AbstractSet, Hashable, Iterable, Iterator, Sequence, TYPE_CHECKING

from cirq import _compat, protocols
from cirq.circuits import AbstractCircuit, Alignment, Circuit
from cirq.circuits.insert_strategy import InsertStrategy

if TYPE_CHECKING:
    import numpy as np

    import cirq


class FrozenCircuit(AbstractCircuit, protocols.SerializableByKey):
    """An immutable version of the Circuit data structure.

    FrozenCircuits are immutable (and therefore hashable), but otherwise behave
    identically to regular Circuits. Conversion between the two is handled with
    the `freeze` and `unfreeze` methods from AbstractCircuit.
    """

    def __init__(
        self,
        *contents: cirq.OP_TREE,
        strategy: cirq.InsertStrategy = InsertStrategy.EARLIEST,
        tags: Sequence[Hashable] = (),
    ) -> None:
        """Initializes a frozen circuit.

        Args:
            contents: The initial list of moments and operations defining the
                circuit. You can also pass in operations, lists of operations,
                or generally anything meeting the `cirq.OP_TREE` contract.
                Non-moment entries will be inserted according to the specified
                insertion strategy.
            strategy: When initializing the circuit with operations and moments
                from `contents`, this determines how the operations are packed
                together.
            tags: A sequence of any type of object that is useful to attach metadata
                to this circuit as long as the type is hashable.  If you wish the
                resulting circuit to be eventually serialized into JSON, you should
                also restrict the tags to be JSON serializable.
        """
        base = Circuit(contents, strategy=strategy)
        self._moments = tuple(base.moments)
        self._tags = tuple(tags)

    @classmethod
    def _from_moments(
        cls, moments: Iterable[cirq.Moment], tags: Sequence[Hashable]
    ) -> FrozenCircuit:
        new_circuit = FrozenCircuit()
        new_circuit._moments = tuple(moments)
        new_circuit._tags = tuple(tags)
        return new_circuit

    @property
    def moments(self) -> Sequence[cirq.Moment]:
        return self._moments

    def freeze(self) -> cirq.FrozenCircuit:
        return self

    def unfreeze(self, copy: bool = True) -> cirq.Circuit:
        return Circuit._from_moments(self._moments, tags=self.tags)

    @property
    def tags(self) -> tuple[Hashable, ...]:
        """Returns a tuple of the Circuit's tags."""
        return self._tags

    @cached_property
    def untagged(self) -> cirq.FrozenCircuit:
        return super().untagged

    def with_tags(self, *new_tags: Hashable) -> cirq.FrozenCircuit:
        """Creates a new tagged `FrozenCircuit` with `self.tags` and `new_tags` combined."""
        if not new_tags:
            return self
        new_circuit = FrozenCircuit(tags=self.tags + new_tags)
        new_circuit._moments = self._moments
        return new_circuit

    @_compat.cached_method
    def __hash__(self) -> int:
        # Explicitly cached for performance
        return hash((self.moments, self.tags))

    def __getstate__(self):
        # Don't save hash when pickling; see #3777.
        state = self.__dict__
        hash_attr = _compat._method_cache_name(self.__hash__)
        if hash_attr in state:
            state = state.copy()
            del state[hash_attr]
        return state

    @_compat.cached_method
    def _num_qubits_(self) -> int:
        return len(self.all_qubits())

    @_compat.cached_method
    def _qid_shape_(self) -> tuple[int, ...]:
        return super()._qid_shape_()

    @_compat.cached_method
    def _has_unitary_(self) -> bool:
        return super()._has_unitary_()

    @_compat.cached_method
    def _unitary_(self) -> np.ndarray | NotImplementedType:
        return super()._unitary_()

    @_compat.cached_method
    def _is_measurement_(self) -> bool:
        return protocols.is_measurement(self.unfreeze())

    @_compat.cached_method
    def all_qubits(self) -> frozenset[cirq.Qid]:
        return super().all_qubits()

    @cached_property
    def _all_operations(self) -> tuple[cirq.Operation, ...]:
        return tuple(super().all_operations())

    def all_operations(self) -> Iterator[cirq.Operation]:
        return iter(self._all_operations)

    def has_measurements(self) -> bool:
        return self._is_measurement_()

    @_compat.cached_method
    def all_measurement_key_objs(self) -> frozenset[cirq.MeasurementKey]:
        return super().all_measurement_key_objs()

    def _measurement_key_objs_(self) -> frozenset[cirq.MeasurementKey]:
        return self.all_measurement_key_objs()

    @_compat.cached_method
    def _control_keys_(self) -> frozenset[cirq.MeasurementKey]:
        return super()._control_keys_()

    @_compat.cached_method
    def are_all_measurements_terminal(self) -> bool:
        return super().are_all_measurements_terminal()

    @_compat.cached_method
    def all_measurement_key_names(self) -> frozenset[str]:
        return frozenset(str(key) for key in self.all_measurement_key_objs())

    @_compat.cached_method
    def _is_parameterized_(self) -> bool:
        return super()._is_parameterized_()

    @_compat.cached_method
    def _parameter_names_(self) -> AbstractSet[str]:
        return super()._parameter_names_()

    def _measurement_key_names_(self) -> frozenset[str]:
        return self.all_measurement_key_names()

    def __add__(self, other) -> cirq.FrozenCircuit:
        return (self.unfreeze() + other).freeze()

    def __radd__(self, other) -> cirq.FrozenCircuit:
        return (other + self.unfreeze()).freeze()

    # Needed for numpy to handle multiplication by np.int64 correctly.
    __array_priority__ = 10000

    # TODO: handle multiplication / powers differently?
    def __mul__(self, other) -> cirq.FrozenCircuit:
        return (self.unfreeze() * other).freeze()

    def __rmul__(self, other) -> cirq.FrozenCircuit:
        return (other * self.unfreeze()).freeze()

    def __pow__(self, other) -> cirq.FrozenCircuit:
        try:
            return (self.unfreeze() ** other).freeze()
        except:
            return NotImplemented

    @classmethod
    def _from_json_dict_(cls, moments, *, tags=(), **kwargs):
        return cls(moments, strategy=InsertStrategy.EARLIEST, tags=tags)

    def concat_ragged(
        *circuits: cirq.AbstractCircuit, align: cirq.Alignment | str = Alignment.LEFT
    ) -> cirq.FrozenCircuit:
        return AbstractCircuit.concat_ragged(*circuits, align=align).freeze()

    concat_ragged.__doc__ = AbstractCircuit.concat_ragged.__doc__

    def zip(
        *circuits: cirq.AbstractCircuit, align: cirq.Alignment | str = Alignment.LEFT
    ) -> cirq.FrozenCircuit:
        return AbstractCircuit.zip(*circuits, align=align).freeze()

    zip.__doc__ = AbstractCircuit.zip.__doc__

    def to_op(self) -> cirq.CircuitOperation:
        """Creates a CircuitOperation wrapping this circuit."""
        from cirq.circuits import CircuitOperation

        return CircuitOperation(self)
