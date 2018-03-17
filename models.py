from pony.orm import *

db = Database()


class Categories(db.Entity):
    category_id = PrimaryKey(str)
    name = Optional(str)
    level = Optional(int)
    is_leaf = Optional(bool)
    product_set = Set('Products_1')
    parent_id = Optional('Categories', reverse='child_set')
    child_set = Set('Categories', reverse='parent_id')


# noinspection PyPep8Naming
class Products_1(db.Entity):
    plu = PrimaryKey(str, auto=True)
    title = Optional(str)
    category_id = Optional(Categories)


# noinspection PyPep8Naming
class Products_2(db.Entity):
    plu = PrimaryKey(str, auto=True)
    title = Optional(str)
    eshop_category_id = Optional(str)
    eshop_category_name = Optional(str)


db.bind(provider='sqlite', filename='database.sqlite', create_db=False)
db.generate_mapping(create_tables=False)
