import json
import sys

import yaml

schema = yaml.load(open(sys.argv[1]))
json.dump(schema, open(sys.argv[2], 'w'))
