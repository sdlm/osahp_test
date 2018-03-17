from itertools import groupby

from pony.orm.core import Query

from models import *


def get_biggest_new_category(queryset: Query):
    """
    Найдём самую большую категорию в размеченных данных
    """

    # названия категорий в размеченных данных
    p2_cats = [x.eshop_category_name for x in queryset]
    # сгруппируем по названию категорий
    groups_of_cats = [(name, len(list(gr))) for name, gr in groupby(sorted(p2_cats))]
    # выберем категорию которой размечено наибольшее кол-во товаров
    cat_name, cat_size = sorted(groups_of_cats, key=lambda x: x[1], reverse=True)[0]

    cat_id = None
    for product in queryset:
        if product.eshop_category_name == cat_name:
            cat_id = product.eshop_category_id
            break

    return cat_id, cat_name, cat_size


def mark_up(mark_up_all: bool = False):
    """
    Разметим данные используя группировку по категориям.
    """
    from mark_up_products import MINIMUM_MARKED_DATA_PERCENT, MINIMUM_NEW_CAT_PERCENT

    with db_session:
        p1_count = Products_1.select().count()
        origin_p2_count = total_p2_count = Products_2.select().count()
        p2_percent_in_p1 = total_p2_count / p1_count * 100

        # Сначала пройдёмся по листам дерева категорий
        for cat in select(c for c in Categories if count(c.child_set) == 0):

            # продукты в рамках текущей категории
            p1 = list(cat.product_set)
            p1_len = len(p1)
            if p1_len > 0:

                # размеченные продукты в рамках текущей категории
                p1_ids = [x.plu for x in p1]
                p2 = select(p for p in Products_2 if p.plu in p1_ids)
                p2_len = len(p2)
                if p2_len > 0:
                    marked_up_percent = p2_len / p1_len * 100

                    # если в текущей группе размечено менее 3% продуктов,
                    # то мы считаем что данных для разметки этой группы недостаточно
                    if marked_up_percent < MINIMUM_MARKED_DATA_PERCENT:
                        continue

                    new_cat_id, new_cat_name, new_cat_size = get_biggest_new_category(p2)

                    # доля которая соответствует наибольшей категории среди размеченных данных
                    new_cat_percent = new_cat_size / p2_len * 100

                    # если категория с наибольшим кол-вом продуктов имеет долю менее половины
                    # то мы считаем что данных для разметки этой группы недостаточно
                    # т.е. в данной категории размеченные данные слишком разнородны
                    if new_cat_percent < MINIMUM_NEW_CAT_PERCENT:
                        continue

                    # дебаг
                    print(
                        '{:70s} {:5d} {:5d} {:>8.1f} {:>8.1f}   {}'.format(
                            cat.name, p1_len, p2_len,
                            marked_up_percent, new_cat_percent, new_cat_name
                        )
                    )

                    from mark_up_products import make_decision
                    mark_up_data = True if mark_up_all else make_decision(new_cat_percent, marked_up_percent)

                    # размечаем данные
                    if mark_up_data:
                        # определяем biggest_group_id
                        existed_p2_ids = [x.plu for x in p2]

                        # собственно дополняем таблицу Products_2
                        for p in select(p for p in Products_1 if p.plu in p1_ids and p.plu not in existed_p2_ids):
                            Products_2(
                                plu=p.plu,
                                title=p.title,
                                eshop_category_id=new_cat_id,
                                eshop_category_name=new_cat_name,
                            )
                        total_p2_count += p1_len - p2_len

                    # saves objects created by this moment in the database
                    flush()

        # А теперь будем проверим, сколько могут добавить остальные категории
        other_prod = sum([len(cat.product_set) for cat in select(c for c in Categories if count(c.child_set) != 0)])
        print(f'not leaf categories can add: < {other_prod / p1_count * 100:3.1f}%')

        print(f'total count of t1 products: {p1_count:6d}')
        print(f'total count of t2 products: {origin_p2_count:6d}')
        print(f'initial ratio: {p2_percent_in_p1:3.1f}%')
        print(f'  final ratio: {total_p2_count / p1_count * 100:3.1f}%')

        rollback()
