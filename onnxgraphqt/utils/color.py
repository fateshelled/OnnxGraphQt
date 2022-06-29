COLOR_WHITE = [235, 235, 235]
COLOR_PALEGRAY = [230, 230, 230]
COLOR_LIGHTGRAY = [200, 200, 203]
COLOR_GRAY = [127, 135, 143]
COLOR_DARKGRAY = [50, 55, 60]
COLOR_BLACK = [20, 20, 20]

COLOR_RED = [112, 41, 33]
COLOR_GREEN = [51, 85, 51]
COLOR_BLUE = [51, 85, 136]
COLOR_BROWN = [89, 66, 59]
COLOR_YELLOW = [255, 255, 153]

COLOR_BG = COLOR_PALEGRAY
COLOR_FONT = COLOR_BLACK
COLOR_GRID = COLOR_GRAY
INPUT_NODE_COLOR = COLOR_LIGHTGRAY
OUTPUT_NODE_COLOR = COLOR_LIGHTGRAY
DEFAULT_COLOR = COLOR_GRAY

NODE_BG_COLOR = COLOR_WHITE
NODE_BORDER_COLOR = COLOR_DARKGRAY
NODE_SELECTED_BORDER_COLOR = COLOR_YELLOW

NODE_COLORS = {
    # Generic
    'Identity': COLOR_DARKGRAY,
    # Constant
    'Constant': COLOR_DARKGRAY,
    'ConstantOfShape': COLOR_DARKGRAY,
    # Math
    'Add': COLOR_DARKGRAY,
    'Sub': COLOR_DARKGRAY,
    'Mul': COLOR_DARKGRAY,
    'Div': COLOR_DARKGRAY,
    'Sqrt': COLOR_DARKGRAY,
    'Reciprocal': COLOR_DARKGRAY,
    'Pow': COLOR_DARKGRAY,
    'Exp': COLOR_DARKGRAY,
    'Log': COLOR_DARKGRAY,
    'Abs': COLOR_DARKGRAY,
    'Neg': COLOR_DARKGRAY,
    'Ceil': COLOR_DARKGRAY,
    'Floor': COLOR_DARKGRAY,
    'Clip': COLOR_RED,
    'Erf': COLOR_DARKGRAY,
    'IsNan': COLOR_DARKGRAY,
    'IsInf': COLOR_DARKGRAY,
    'Sign': COLOR_DARKGRAY,
    # Logical
    'Greater': COLOR_DARKGRAY,
    'Less': COLOR_DARKGRAY,
    'Equal': COLOR_DARKGRAY,
    'Not': COLOR_DARKGRAY,
    'And': COLOR_DARKGRAY,
    'Or': COLOR_DARKGRAY,
    'Xor': COLOR_DARKGRAY,
    # Trigonometric
    'Sin': COLOR_DARKGRAY,
    'Cos': COLOR_DARKGRAY,
    'Tan': COLOR_DARKGRAY,
    'Asin': COLOR_DARKGRAY,
    'Acos': COLOR_DARKGRAY,
    'Atan': COLOR_DARKGRAY,
    'Sinh': COLOR_DARKGRAY,
    'Cosh': COLOR_DARKGRAY,
    'Tanh': COLOR_DARKGRAY,
    'Acosh': COLOR_DARKGRAY,
    'Asinh': COLOR_DARKGRAY,
    'Atanh': COLOR_DARKGRAY,
    'Max': COLOR_DARKGRAY,
    # Reduction
    'Sum': COLOR_DARKGRAY,
    'Mean': COLOR_DARKGRAY,
    'Max': COLOR_DARKGRAY,
    'Min': COLOR_DARKGRAY,
    # Activation
    'Sigmoid': COLOR_RED,
    'HardSigmoid': COLOR_RED,
    'Tanh': COLOR_RED,
    'ScaledTanh': COLOR_RED,
    'Relu': COLOR_RED,
    'LeakyRelu': COLOR_RED,
    'PRelu': COLOR_RED,
    'ThresholdedRelu': COLOR_RED,
    'Elu': COLOR_RED,
    'Selu': COLOR_RED,
    'Softmax': COLOR_RED,
    'LogSoftmax': COLOR_RED,
    'Hardmax': COLOR_RED,
    'Softsign': COLOR_RED,
    'Softplus': COLOR_RED,
    'Affine': COLOR_RED,
    'Shrink': COLOR_RED,
    # Random
    'RandomNormal': COLOR_DARKGRAY,
    'RandomNormalLike': COLOR_DARKGRAY,
    'RandomUniform': COLOR_DARKGRAY,
    'RandomUniformLike': COLOR_DARKGRAY,
    'Multinomial': COLOR_DARKGRAY,
    # Multiplication
    'EyeLike': COLOR_BLUE,
    'Gemm': COLOR_BLUE,
    'MatMul': COLOR_BLUE,
    'Conv': COLOR_BLUE,
    'ConvTranspose': COLOR_BLUE,
    # Conversion
    'Cast': COLOR_DARKGRAY,
    # Reorganization
    'Transpose': COLOR_GREEN,
    'Expand': COLOR_DARKGRAY,
    'Tile': COLOR_DARKGRAY,
    'Split': COLOR_DARKGRAY,
    'Slice': COLOR_BROWN,
    'DynamicSlice': COLOR_BROWN,
    'Concat': COLOR_BROWN,
    'Gather': COLOR_GREEN,
    'GatherElements': COLOR_GREEN,
    'ScatterElements': COLOR_DARKGRAY,
    'Pad': COLOR_DARKGRAY,
    'SpaceToDepth': COLOR_DARKGRAY,
    'DepthToSpace': COLOR_DARKGRAY,
    'Shape': COLOR_DARKGRAY,
    'Size': COLOR_DARKGRAY,
    'Reshape': COLOR_BROWN,
    'Flatten': COLOR_DARKGRAY,
    'Squeeze': COLOR_DARKGRAY,
    'Unsqueeze': COLOR_GREEN,
    'OneHot': COLOR_DARKGRAY,
    'TopK': COLOR_DARKGRAY,
    'Where': COLOR_DARKGRAY,
    'Compress': COLOR_DARKGRAY,
    'Reverse': COLOR_DARKGRAY,
    # Pooling
    'GlobalAveragePool': COLOR_GREEN,
    'AveragePool': COLOR_GREEN,
    'GlobalMaxPool': COLOR_GREEN,
    'MaxPool': COLOR_GREEN,
    'MaxUnpool': COLOR_GREEN,
    'LpPool': COLOR_GREEN,
    'GlobalLpPool': COLOR_GREEN,
    'MaxRoiPool': COLOR_GREEN,
    # Reduce
    'ReduceSum': COLOR_DARKGRAY,
    'ReduceMean': COLOR_DARKGRAY,
    'ReduceProd': COLOR_DARKGRAY,
    'ReduceLogSum': COLOR_DARKGRAY,
    'ReduceLogSumExp': COLOR_DARKGRAY,
    'ReduceSumSquare': COLOR_DARKGRAY,
    'ReduceL1': COLOR_DARKGRAY,
    'ReduceL2': COLOR_DARKGRAY,
    'ReduceMax': COLOR_DARKGRAY,
    'ReduceMin': COLOR_DARKGRAY,
    'ArgMax': COLOR_DARKGRAY,
    'ArgMin': COLOR_DARKGRAY,
    # Imaging
    'Upsample': COLOR_DARKGRAY,
    # Flow
    'If': COLOR_DARKGRAY,
    'Loop': COLOR_DARKGRAY,
    'Scan': COLOR_DARKGRAY,
    # Normalization
    'InstanceNormalization': COLOR_DARKGRAY,
    'BatchNormalization': COLOR_DARKGRAY,
    'LRN': COLOR_DARKGRAY,
    'MeanVarianceNormalization': COLOR_DARKGRAY,
    'LpNormalization': COLOR_DARKGRAY,
    # collation
    'Nonzero': COLOR_DARKGRAY,
    # NGram
    'TfldfVectorizer': COLOR_DARKGRAY,
    # Aggregate
    'RNN': COLOR_DARKGRAY,
    'GRU': COLOR_DARKGRAY,
    'LSTM': COLOR_DARKGRAY,
    # Training
    'Dropout': COLOR_DARKGRAY,
    # Quantize
    'QuantizeLinear': COLOR_DARKGRAY,
    'QLinearConv': COLOR_BLUE,
    'DequantizeLinear': COLOR_DARKGRAY,
    'QLinearGlobalAveragePool': COLOR_GREEN,
    'QLinearAdd': COLOR_DARKGRAY,
    'QLinearMatMul': COLOR_BLUE,
}

def get_node_color(op_name):
    return NODE_COLORS.get(op_name, DEFAULT_COLOR)

class PrintColor:
    BLACK          = '\033[30m'
    RED            = '\033[31m'
    GREEN          = '\033[32m'
    YELLOW         = '\033[33m'
    BLUE           = '\033[34m'
    MAGENTA        = '\033[35m'
    CYAN           = '\033[36m'
    WHITE          = '\033[37m'
    COLOR_DEFAULT  = '\033[39m'
    BOLD           = '\033[1m'
    UNDERLINE      = '\033[4m'
    INVISIBLE      = '\033[08m'
    REVERCE        = '\033[07m'
    BG_BLACK       = '\033[40m'
    BG_RED         = '\033[41m'
    BG_GREEN       = '\033[42m'
    BG_YELLOW      = '\033[43m'
    BG_BLUE        = '\033[44m'
    BG_MAGENTA     = '\033[45m'
    BG_CYAN        = '\033[46m'
    BG_WHITE       = '\033[47m'
    BG_DEFAULT     = '\033[49m'
    RESET          = '\033[0m'


def removePrintColor(message:str)->str:
    ret = message
    for key, v in vars(PrintColor).items():
        if key[:2] == "__":
            continue
        ret = ret.replace(v, '')
    for i in range(32):
        v = f'\033[38;5;{i}m'
        ret = ret.replace(v, '')
    return ret

if __name__ == "__main__":
    import inspect
    text = "\x1b[38;5;11m[W] Found distinct tensors that share the same name:\n[id: 139661839911328] Variable (transpose_out_input): (shape=[224, 224, 3, 'batch_size'], dtype=float32)\n[id: 139661797372160] Variable (transpose_out_input): (shape=['batch_size', 3, 224, 224], dtype=float32)\nNote: Producer node(s) of first tensor:\n[input_order_convert_transpose_0 (Transpose)\n\tInputs: [\n\t\tVariable (input): (shape=['batch_size', 3, 224, 224], dtype=float32)\n\t]\n\tOutputs: [\n\t\tVariable (transpose_out_input): (shape=[224, 224, 3, 'batch_size'], dtype=float32)\n\t]\nAttributes: {'perm': [3, 2, 1, 0]}]\nProducer node(s) of second tensor:\n[input_order_convert_transpose_0 (Transpose)\n\tInputs: [\n\t\tVariable (transpose_out_input): (shape=[224, 224, 3, 'batch_size'], dtype=float32)\n\t]\n\tOutputs: [\n\t\tVariable (transpose_out_input): (shape=['batch_size', 3, 224, 224], dtype=float32)\n\t]\nAttributes: OrderedDict([('perm', [3, 2, 1, 0])])]\x1b[0m\n\x1b[38;5;11m[W] Found distinct tensors that share the same name:\n[id: 139661797372160] Variable (transpose_out_input): (shape=['batch_size', 3, 224, 224], dtype=float32)\n[id: 139661839911328] Variable (transpose_out_input): (shape=[224, 224, 3, 'batch_size'], dtype=float32)\nNote: Producer node(s) of first tensor:\n[input_order_convert_transpose_0 (Transpose)\n\tInputs: [\n\t\tVariable (transpose_out_input): (shape=[224, 224, 3, 'batch_size'], dtype=float32)\n\t]\n\tOutputs: [\n\t\tVariable (transpose_out_input): (shape=['batch_size', 3, 224, 224], dtype=float32)\n\t]\nAttributes: OrderedDict([('perm', [3, 2, 1, 0])])]\nProducer node(s) of second tensor:\n[input_order_convert_transpose_0 (Transpose)\n\tInputs: [\n\t\tVariable (input): (shape=['batch_size', 3, 224, 224], dtype=float32)\n\t]\n\tOutputs: [\n\t\tVariable (transpose_out_input): (shape=[224, 224, 3, 'batch_size'], dtype=float32)\n\t]\nAttributes: {'perm': [3, 2, 1, 0]}]\x1b[0m\n\x1b[38;5;11m[W] Found distinct tensors that share the same name:\n[id: 139661839911328] Variable (transpose_out_input): (shape=[224, 224, 3, 'batch_size'], dtype=float32)\n[id: 139661797372160] Variable (transpose_out_input): (shape=['batch_size', 3, 224, 224], dtype=float32)\nNote: Producer node(s) of first tensor:\n[]\nProducer node(s) of second tensor:\n[input_order_convert_transpose_0 (Transpose)\n\tInputs: [\n\t\tVariable (transpose_out_input): (shape=[224, 224, 3, 'batch_size'], dtype=float32)\n\t]\n\tOutputs: [\n\t\tVariable (transpose_out_input): (shape=['batch_size', 3, 224, 224], dtype=float32)\n\t]\nAttributes: OrderedDict([('perm', [3, 2, 1, 0])])]\x1b[0m\n\x1b[38;5;11m[W] Found distinct tensors that share the same name:\n[id: 139661839911328] Variable (transpose_out_input): (shape=[224, 224, 3, 'batch_size'], dtype=float32)\n[id: 139661797372160] Variable (transpose_out_input): (shape=['batch_size', 3, 224, 224], dtype=float32)\nNote: Producer node(s) of first tensor:\n[]\nProducer node(s) of second tensor:\n[input_order_convert_transpose_0 (Transpose)\n\tInputs: [\n\t\tVariable (transpose_out_input): (shape=[224, 224, 3, 'batch_size'], dtype=float32)\n\t]\n\tOutputs: [\n\t\tVariable (transpose_out_input): (shape=['batch_size', 3, 224, 224], dtype=float32)\n\t]\nAttributes: OrderedDict([('perm', [3, 2, 1, 0])])]\x1b[0m\n\x1b[33mWARNING:\x1b[0m The input shape of the next OP does not match the output shape. Be sure to open the .onnx file to verify the certainty of the geometry.\n\x1b[33mWARNING:\x1b[0m onnx.onnx_cpp2py_export.shape_inference.InferenceError: [ShapeInferenceError] (op_type:Transpose, node name: input_order_convert_transpose_0): [ShapeInferenceError] Inferred shape and existing shape differ in dimension 1: (224) vs (3)\n\x1b[32mINFO:\x1b[0m Finish!\n"
    print(removePrintColor(text))
    print("------------------------------")
    for key, v in vars(PrintColor).items():
        if key[:2] == "__":
            continue
        print(f"{v}{key}{PrintColor.RESET}")
    print("------------------------------")