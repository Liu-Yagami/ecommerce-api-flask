from extensions import ma
from models import Product
from marshmallow import fields, validate

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = False

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=80))
    description = fields.Str(required=False, allow_none=True)
    price = fields.Float(required=True, validate=validate.Range(min=0.01))

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)