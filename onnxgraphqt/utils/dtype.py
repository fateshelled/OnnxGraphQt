import onnx
import numpy as np

AVAILABLE_DTYPES = [
    'float32',
    'float64',
    'int32',
    'int64',
    'str',
]

DTYPES_TO_ONNX_DTYPES = {
    float: onnx.TensorProto.FLOAT,
    int: onnx.TensorProto.INT64,
    str: onnx.TensorProto.STRING,
}

DTYPES_TO_NUMPY_TYPES = {
    'float32': np.float32,
    'float64': np.float64,
    'int32': np.int32,
    'int64': np.int64,
}

NUMPY_TYPES_TO_ONNX_DTYPES = {
    np.dtype('float32'): onnx.TensorProto.FLOAT,
    np.dtype('float64'): onnx.TensorProto.DOUBLE,
    np.dtype('int32'): onnx.TensorProto.INT32,
    np.dtype('int64'): onnx.TensorProto.INT64,
    np.float32: onnx.TensorProto.FLOAT,
    np.float64: onnx.TensorProto.DOUBLE,
    np.int32: onnx.TensorProto.INT32,
    np.int64: onnx.TensorProto.INT64,
}

NUMPY_TYPES_TO_CLASSES = {
    np.dtype('float32'): np.float32,
    np.dtype('float64'): np.float64,
    np.dtype('int32'): np.int32,
    np.dtype('int64'): np.int64,
}
