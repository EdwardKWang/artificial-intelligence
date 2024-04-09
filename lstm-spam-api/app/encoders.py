import json
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    """This is a custom JSONEncoder for numpy types

    :param json: _description_
    :type json: _type_
    """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def encode_to_json(data, as_py=True):
    encoded = json.dumps(data, cls=NumpyEncoder)
    if as_py:
        encoded = json.loads(encoded)
    return encoded
