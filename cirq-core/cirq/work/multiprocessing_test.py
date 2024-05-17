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


import contextlib
import multiprocessing
import concurrent.futures
import pytest

from cirq.work.multiprocessing import execute_with_progress_bar, starmap_with_progress_bar


def _sinle_arg_func(x: int) -> str:
    return f'{x=}'


def _multi_arg_func(x: int, y: int) -> str:
    return f'{x=}-{y=}'


@pytest.mark.parametrize(
    'pool_creator', [None, multiprocessing.Pool, concurrent.futures.ThreadPoolExecutor]
)
def test_execute_with_progress_bar(pool_creator):
    desired = set(f'{x=}' for x in range(10))
    with contextlib.ExitStack() as stack:
        pool = stack.enter_context(pool_creator(2)) if pool_creator else None
        actual = set(execute_with_progress_bar(_sinle_arg_func, range(10), pool=pool))
    assert actual == desired


@pytest.mark.parametrize(
    'pool_creator', [None, multiprocessing.Pool, concurrent.futures.ThreadPoolExecutor]
)
def test_starmap_with_progress_bar(pool_creator):
    xy_sequence = [(i, i + 1000) for i in range(10)]
    desired = set(f'{x=}-{y=}' for x, y in xy_sequence)
    with contextlib.ExitStack() as stack:
        pool = stack.enter_context(pool_creator(2)) if pool_creator else None
        actual = set(starmap_with_progress_bar(_multi_arg_func, xy_sequence, pool=pool))
    assert actual == desired
