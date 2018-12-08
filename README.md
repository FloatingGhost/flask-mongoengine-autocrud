## Flask Mongoengine Autocrud

Need more crud in your life?

me too.

The idea behind this is that, given a mongoengine type,
we can autogenerate a standard set of REST endpoints to
facilitate creation, modification, deletion and readification.
Maybe search too. I think.

### Usage

```python3
# In your blueprints folder
from flask_mongoengine_autocrud import create_crud
from models.my_model import SuperGoodModel

my_blueprint = create_crud(
  SuperGoodModel,
  "super_good_blueprint",
  __name__
)
```

and theoretically that's... it

Register the blueprint with flask in the standard way, and
should be good to go.

Now we can use standard REST calls to do stuff

The following endpoints are created

| Method | URL Pattern | Returns | Options |
|--------|-------------|---------|--------|
| GET    | /           | List of all items | page (int), size (int), for pagination |
| GET    | /<id>       | A single item | |
| POST   | /           | The created item | All valid mongoengine field names in POST body |
| PATCH  | /<id>       | The modified item | All valid mongoengine field names |
| DELETE | /<id>       | Success status | |
| POST   | /search     | List of matching items | See search section |

For example

```bash
$ curl -XPOST /mydatatype/
    --header "Content-Type: application/json" \
    --data-binary '{"title": "my data", "admin": true}'
    http://myserver

{"title": "my data", "admin": true, "_id": "1234"}

$ curl -XPATCH /mydatatype/1234
    --header "Content-Type: application/json" \
    --data-binary '{"admin": false}' 
    http://myserver

{"title": "my data", "admin": false, "_id": "1234"}

$ curl -XPOST /mydatatype/search
    --header "Content-Type: application/json" \
    --data-binary '{"filter": {"admin": false}}' 
    http://myserver

[{"title": "my data", "admin": false, "_id": "1234"}]

$ curl -XDELETE /mydatatype/1234
    --header "Content-Type: application/json" \
    --data-binary '{"filter": {"admin": false}}'
    http://myserver

{"success": true} 
```

### Search

Search options should be posted as a JSON body in the following format

All fields are optional

```json
{
  "filter": {
    "field_name": "field_value",
    ...
  },
  "sort": {
    "field_name": "direction (desc or asc)"
  },
  "size": integer,
  "page": integer
}
```

The `page` field *requires* the size field, else it'll be ignored.
