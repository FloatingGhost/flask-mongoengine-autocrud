from flask import Blueprint, request, Response
import json
from bson import json_util
from .json import default


def load_json(data):
    return json.loads(data, object_hook=json_util.object_hook)


def dump_json(output, status=200):
    return Response(
        response=json.dumps(output, default=default),
        status=status,
        content_type="application/json"
    )


def dotted_to_mongoengine(key):
    # Mongoengine can handle embedded fields with __
    return key.replace(".", "__")


def create_crud(
    mongoengine_object,
    blueprint_name,
    blueprint_import_name,
):
    """Create a CRUD blueprint for the specified mongoengine type

    Uses the attributes provided by the object to create 6 routes
        - GET / Get all objects of this type
        - GET /id Get a single object with the specified ID
        - POST / Create an object with attributes specified in the body
        - PATCH /id modify the specified object
        - DELETE /id Delete the specified object
        - POST /search Like GET / but will filter base on a set of criteria
    """

    this_bp = Blueprint(blueprint_name, blueprint_import_name)

    def get_objs():
        matching = mongoengine_object.objects.all()
        if "size" in request.args:
            # Paginate!
            size = request.args.get("size")
            page = request.args.get("page", 0)

            matching = matching.skip(page * size).limit(size)

        return dump_json([x.to_mongo() for x in matching])

    def get_obj(id):
        matching = mongoengine_object.objects(id=id).first()
        if not matching:
            return dump_json({
                "error": "Invalid ID"
            }, status=410)
        return dump_json(matching.to_mongo())

    def new_obj():
        try:
            arguments = load_json(request.data.decode())
        except Exception as ex:
            return dump_json({
                "error": "Could not decode arguments!",
                "verbose": str(ex)
            }, status=400)

        created = mongoengine_object(**arguments)
        try:
            created.validate()
        except Exception as ex:
            return dump_json({
                "error": "Not a valid object",
                "verbose": str(ex)
            }, status=400)

        try:
            created.save()
        except Exception as ex:
            return dump_json({
                "error": "Could not create object",
                "verbose": str(ex)
            }, status=500)

        return dump_json(created.to_mongo(), status=201)

    def edit_obj(id):
        try:
            arguments = load_json(request.data.decode())
        except Exception as ex:
            return dump_json({
                "error": "Could not decode arguments!",
                "verbose": str(ex)
            }, status=400)

        matching = mongoengine_object.objects(id=id).first()
        if not matching:
            return dump_json({
                "error": "Invalid ID"
            }, status=410)
        matching.update(**arguments)
        try:
            matching.save()
        except Exception as ex:
            return dump_json({
                  "error": "Could not save object",
                  "verbose": str(ex)
              }, status=500)

    def delete_obj(id):
        matching = mongoengine_object.objects(id=id).first()
        if not matching:
            return dump_json({
                "error": "Invalid ID"
            }, status=410)
        matching.delete()
        return dump_json({"success": True})

    def search():
        try:
            arguments = load_json(request.data.decode())
        except Exception as ex:
            return dump_json({
                "error": "Could not decode arguments!",
                "verbose": str(ex)
            }, status=400)

        sort = arguments.get("sort", {})
        filt = arguments.get("filter", {})
        # Mongoengine wants sorters in the form "-field" or field
        processed_sort = []
        for field, direction in sort.items():
            direction = "-" if direction == "desc" else ""
            processed_sort.append("{}{}".format(direction, field))

        processed_filt = {}
        for field, value in filt.items():
            field = dotted_to_mongoengine(field)
            if isinstance(value, int):
                # We must query as-is
                processed_filt[field] = value
            else:
                # Standard string matching
                # Let's do an icontains
                field = "{}__icontains".format(field)
                processed_filt[field] = value

        # Now we can run the search
        matching = mongoengine_object.objects.filter(
            **processed_filt
        ).order_by(*processed_sort)

        # Now paginate if required
        if "size" in arguments:
            size = arguments.get("size")
            page = request.args.get("page", 0)

            matching = matching.skip(page * size).limit(size)

        return dump_json([x.to_mongo() for x in matching])

    this_bp.add_url_rule("/", view_func=get_objs)
    this_bp.add_url_rule("/search", view_func=search, methods=["POST"])
    this_bp.add_url_rule("/", view_func=new_obj, methods=["POST"])
    this_bp.add_url_rule("/<id>", view_func=get_obj)
    this_bp.add_url_rule("/<id>", view_func=edit_obj, methods=["PATCH"])
    this_bp.add_url_rule("/<id>", view_func=delete_obj, methods=["DELETE"])
    return this_bp
