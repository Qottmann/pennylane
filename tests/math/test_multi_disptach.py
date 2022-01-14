# Copyright 2018-2020 Xanadu Quantum Technologies Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
""" Assertion test for multi_dispatch function/decorator
"""
import autoray
import numpy as onp
import pytest
from autoray import numpy as anp
from pennylane import numpy as np
from pennylane import math as fn


tf = pytest.importorskip("tensorflow", minversion="2.1")
torch = pytest.importorskip("torch")
jax = pytest.importorskip("jax")

test_multi_dispatch_stack_data = [
    [[1.0, 0.0], [2.0, 3.0]],
    ([1.0, 0.0], [2.0, 3.0]),
    onp.array([[1.0, 0.0], [2.0, 3.0]]),
    anp.array([[1.0, 0.0], [2.0, 3.0]]),
    np.array([[1.0, 0.0], [2.0, 3.0]]),
    jax.numpy.array([[1.0, 0.0], [2.0, 3.0]]),
    tf.constant([[1.0, 0.0], [2.0, 3.0]]),
]


@pytest.mark.parametrize("x", test_multi_dispatch_stack_data)
def test_multi_dispatch_stack(x):
    """Test that the decorated autoray function stack can handle all inputs"""
    stack = fn.multi_dispatch(argnum=0, tensor_list=0)(autoray.numpy.stack)
    res = stack(x)
    assert fn.allequal(res, [[1.0, 0.0], [2.0, 3.0]])


@pytest.mark.parametrize("x", test_multi_dispatch_stack_data)
def test_multi_dispatch_decorate(x):
    """Test decorating a standard numpy function for PennyLane"""

    @fn.multi_dispatch(argnum=[0], tensor_list=[0])
    def tensordot(x, like, axes=None):
        return np.tensordot(x[0], x[1], axes=axes)

    assert fn.allequal(tensordot(x, axes=(0, 0)).numpy(), 2)


test_data0 = [
    (1, 2, 3),
    [1, 2, 3],
    onp.array([1, 2, 3]),
    anp.array([1, 2, 3]),
    np.array([1, 2, 3]),
    torch.tensor([1, 2, 3]),
    jax.numpy.array([1, 2, 3]),
    tf.constant([1, 2, 3]),
]

test_data = [(x, x) for x in test_data0]


@pytest.mark.parametrize("t1,t2", test_data)
def test_multi_dispatch_decorate2(t1, t2):
    """Test decorating a standard numpy function for PennyLane, automatically dispatching all inputs by choosing argnum=None"""

    @fn.multi_dispatch(argnum=None, tensor_list=None)
    def tensordot(tensor1, tensor2, like, axes=None):
        return np.tensordot(tensor1, tensor2, axes=axes)

    assert fn.allequal(tensordot(t1, t2, axes=(0, 0)).numpy(), 14)

test_data_values = [
    [[1,2,3] for _ in range(5)],
    [(1,2,3) for _ in range(5)],
    [np.array([1,2,3]) for _ in range(5)],
    [onp.array([1,2,3]) for _ in range(5)],
    [anp.array([1,2,3]) for _ in range(5)],
    [torch.tensor([1,2,3]) for _ in range(5)],
    [jax.numpy.array([1,2,3]) for _ in range(5)],
    [tf.constant([1,2,3]) for _ in range(5)]
]

@pytest.mark.parametrize("values", test_data_values)
def test_multi_dispatch_decorate3(values):
    """Test decorating a custom function for PennyLane including a non-dispatchable parameter """
    @fn.multi_dispatch(argnum=0,tensor_list=0)
    def custom_function(values, like, coefficient=10):
        """
        A dummy custom function that computes coeff :math:`c \\sum_i (v_i)^T v_i` where :math:`v_i` are vectors in ``values``
        and :math:`c` is a fixed ``coefficient``.
        values is a list of vectors
        like can force the interface (optional)
        """
        return coefficient * np.sum([fn.dot(v,v) for v in values])
    assert fn.allequal(custom_function(values),700)
