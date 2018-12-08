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
