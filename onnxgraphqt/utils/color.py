COLOR_WHITE = [235, 235, 235]
COLOR_LIGHTGRAY = [200, 200, 203]
COLOR_GRAY = [132, 145, 158]
COLOR_BLACK = [20, 20, 20]

COLOR_RED = [112, 41, 33]
COLOR_GREEN = [51, 85, 51]
COLOR_BLUE = [51, 85, 136]
COLOR_BROWN = [89, 66, 59]

COLOR_BG = COLOR_LIGHTGRAY
COLOR_FONT = COLOR_BLACK
COLOR_GRID = COLOR_GRAY
INPUT_NODE_COLOR = COLOR_WHITE
OUTPUT_NODE_COLOR = COLOR_WHITE
DEFAULT_COLOR = COLOR_GRAY

NODE_COLORS = {
    # Generic
    'Identity': COLOR_BLACK,
    # Constant
    'Constant': COLOR_BLACK,
    'ConstantOfShape': COLOR_BLACK,
    # Math
    'Add': COLOR_BLACK,
    'Sub': COLOR_BLACK,
    'Mul': COLOR_BLACK,
    'Div': COLOR_BLACK,
    'Sqrt': COLOR_BLACK,
    'Reciprocal': COLOR_BLACK,
    'Pow': COLOR_BLACK,
    'Exp': COLOR_BLACK,
    'Log': COLOR_BLACK,
    'Abs': COLOR_BLACK,
    'Neg': COLOR_BLACK,
    'Ceil': COLOR_BLACK,
    'Floor': COLOR_BLACK,
    'Clip': COLOR_RED,
    'Erf': COLOR_BLACK,
    'IsNan': COLOR_BLACK,
    'IsInf': COLOR_BLACK,
    'Sign': COLOR_BLACK,
    # Logical
    'Greater': COLOR_BLACK,
    'Less': COLOR_BLACK,
    'Equal': COLOR_BLACK,
    'Not': COLOR_BLACK,
    'And': COLOR_BLACK,
    'Or': COLOR_BLACK,
    'Xor': COLOR_BLACK,
    # Trigonometric
    'Sin': COLOR_BLACK,
    'Cos': COLOR_BLACK,
    'Tan': COLOR_BLACK,
    'Asin': COLOR_BLACK,
    'Acos': COLOR_BLACK,
    'Atan': COLOR_BLACK,
    'Sinh': COLOR_BLACK,
    'Cosh': COLOR_BLACK,
    'Tanh': COLOR_BLACK,
    'Acosh': COLOR_BLACK,
    'Asinh': COLOR_BLACK,
    'Atanh': COLOR_BLACK,
    'Max': COLOR_BLACK,
    # Reduction
    'Sum': COLOR_BLACK,
    'Mean': COLOR_BLACK,
    'Max': COLOR_BLACK,
    'Min': COLOR_BLACK,
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
    'RandomNormal': COLOR_BLACK,
    'RandomNormalLike': COLOR_BLACK,
    'RandomUniform': COLOR_BLACK,
    'RandomUniformLike': COLOR_BLACK,
    'Multinomial': COLOR_BLACK,
    # Multiplication
    'EyeLike': COLOR_BLUE,
    'Gemm': COLOR_BLUE,
    'MatMul': COLOR_BLUE,
    'Conv': COLOR_BLUE,
    'ConvTranspose': COLOR_BLUE,
    # Conversion
    'Cast': COLOR_BLACK,
    # Reorganization
    'Transpose': COLOR_GREEN,
    'Expand': COLOR_BLACK,
    'Tile': COLOR_BLACK,
    'Split': COLOR_BLACK,
    'Slice': COLOR_BROWN,
    'DynamicSlice': COLOR_BROWN,
    'Concat': COLOR_BROWN,
    'Gather': COLOR_GREEN,
    'GatherElements': COLOR_GREEN,
    'ScatterElements': COLOR_BLACK,
    'Pad': COLOR_BLACK,
    'SpaceToDepth': COLOR_BLACK,
    'DepthToSpace': COLOR_BLACK,
    'Shape': COLOR_BLACK,
    'Size': COLOR_BLACK,
    'Reshape': COLOR_BROWN,
    'Flatten': COLOR_BLACK,
    'Squeeze': COLOR_BLACK,
    'Unsqueeze': COLOR_GREEN,
    'OneHot': COLOR_BLACK,
    'TopK': COLOR_BLACK,
    'Where': COLOR_BLACK,
    'Compress': COLOR_BLACK,
    'Reverse': COLOR_BLACK,
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
    'ReduceSum': COLOR_BLACK,
    'ReduceMean': COLOR_BLACK,
    'ReduceProd': COLOR_BLACK,
    'ReduceLogSum': COLOR_BLACK,
    'ReduceLogSumExp': COLOR_BLACK,
    'ReduceSumSquare': COLOR_BLACK,
    'ReduceL1': COLOR_BLACK,
    'ReduceL2': COLOR_BLACK,
    'ReduceMax': COLOR_BLACK,
    'ReduceMin': COLOR_BLACK,
    'ArgMax': COLOR_BLACK,
    'ArgMin': COLOR_BLACK,
    # Imaging
    'Upsample': COLOR_BLACK,
    # Flow
    'If': COLOR_BLACK,
    'Loop': COLOR_BLACK,
    'Scan': COLOR_BLACK,
    # Normalization
    'InstanceNormalization': COLOR_BLACK,
    'BatchNormalization': COLOR_BLACK,
    'LRN': COLOR_BLACK,
    'MeanVarianceNormalization': COLOR_BLACK,
    'LpNormalization': COLOR_BLACK,
    # collation
    'Nonzero': COLOR_BLACK,
    # NGram
    'TfldfVectorizer': COLOR_BLACK,
    # Aggregate
    'RNN': COLOR_BLACK,
    'GRU': COLOR_BLACK,
    'LSTM': COLOR_BLACK,
    # Training
    'Dropout': COLOR_BLACK,
    # Quantize
    'QuantizeLinear': COLOR_BLACK,
    'QLinearConv': COLOR_BLUE,
    'DequantizeLinear': COLOR_BLACK,
    'QLinearGlobalAveragePool': COLOR_GREEN,
    'QLinearAdd': COLOR_BLACK,
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
