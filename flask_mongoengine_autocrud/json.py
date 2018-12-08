from flask import Response
import json
from bson import json_util, SON, ObjectId
from bson.py3compat import iteritems, text_type
from bson.dbref import DBRef
import datetime


def _json_convert(obj):
    """Recursive helper method that converts BSON types so they can be
    converted into json.
    """
    if hasattr(obj, "iteritems") or hasattr(obj, "items"):
        return SON(((k, _json_convert(v))
                    for k, v in iteritems(obj)))
    elif hasattr(obj, "__iter__") and not isinstance(obj, (text_type, bytes)):
        return list((_json_convert(v,) for v in obj))
    try:
        return default(obj)
    except TypeError:
        return obj


def default(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, DBRef):
        return _json_convert(obj.as_doc())
    if isinstance(obj, datetime.datetime):
        return obj.strftime("%Y-%m-%dT%H:%M:%S")
    if isinstance(obj, bool):
        return obj
    raise TypeError("%r is not JSON serializable" % obj)


def load_json(data):
    return json.loads(data, object_hook=json_util.object_hook)


def dump_json(output, status=200):
    return Response(
        response=json.dumps(output, default=default),
        status=status,
        content_type="application/json"
    )
