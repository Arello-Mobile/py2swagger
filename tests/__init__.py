import os
import json


FIXTURES_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'fixtures'))


def unordered(struct_with_ordered_dict):
    return json.loads(json.dumps(struct_with_ordered_dict))
