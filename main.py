from itertools import groupby

from models import *


def main():
    with db_session:
        p1_count = Products_1.select().count()
        origin_p2_count = total_p2_count = Products_2.select().count()
        p2_proc_in_p1 = int(total_p2_count / p1_count * 100)

        # Сначала пройдёмся по листам дерева категорий
        for cat in select(c for c in Categories if count(c.child_set) == 0):

            # продукты в рамках текущей категории
            p1 = list(cat.product_set)
            if len(p1) > 0:

                # размеченные продукты в рамках текущей категории
                p1_ids = [x.plu for x in p1]
                p2 = list(select(p for p in Products_2 if p.plu in p1_ids))
                if len(p2) > 0:
                    proc = len(p2) / len(p1) * 100

                    # если в текущей группе размечено менее 3% продуктов,
                    # то мы считаем что данных для разметки этой группы недостаточно
                    if proc < 3:
                        continue

                    # названия категорий в размеченных данных
                    p2_cats = [x.eshop_category_name for x in p2]
                    # сгруппируем по названию категорий
                    groups_of_cats = [(name, len(list(gr))) for name, gr in groupby(sorted(p2_cats))]
                    # выберем категорию которой размечено наибольшее кол-во товаров
                    biggest_group_name, biggest_group_size = sorted(groups_of_cats, key=lambda x: x[0], reverse=True)[0]

                    # доля которая соответствует наибольшей категории среди размеченных данных
                    cat2_proc = biggest_group_size / len(p2) * 100

                    # если категория с наибольшим кол-вом продуктов имеет долю менее половины
                    # то мы считаем что данных для разметки этой группы недостаточно
                    # т.е. в данной категории размеченные данные слишком разнородны
                    if cat2_proc < 50:
                        continue

                    # дебаг
                    print(
                        '{:70s} {:5d} {:5d} {:>8.1f} {:>8.1f}   {}'.format(
                            cat.name, len(p1), len(p2),
                            proc, cat2_proc, biggest_group_name
                        )
                    )
                    addition = len(p1) - len(p2)

                    # нам важны как однородность размеченных данных так и процент размеченных данных
                    # грубо, можно было бы сделать if cat2_proc + proc > 100,
                    # но на мой взгляд это смотрится черезчур дико
                    mark_up_data = False
                    if cat2_proc == 100:
                        mark_up_data = True
                    elif cat2_proc > 90:
                        if proc >= 10:
                            mark_up_data = True
                    elif cat2_proc > 80:
                        if proc >= 20:
                            mark_up_data = True
                    elif cat2_proc > 70:
                        if proc >= 30:
                            mark_up_data = True

                    # размечаем данные
                    if mark_up_data:
                        # определяем biggest_group_id
                        biggest_group_id = None
                        for product in p2:
                            if product.eshop_category_name == biggest_group_name:
                                biggest_group_id = product.eshop_category_id
                                break
                        existed_p2_ids = [x.plu for x in p2]

                        # собственно дополняем таблицу Products_2
                        fact_addition = 0
                        for p in select(p for p in Products_1 if p.plu in p1_ids and p.plu not in existed_p2_ids):
                            Products_2(
                                plu=p.plu,
                                title=p.title,
                                eshop_category_id=biggest_group_id,
                                eshop_category_name=biggest_group_name,
                            )
                            fact_addition += 1
                        if fact_addition != addition:
                            print('wtf ' + '!'*50)
                        total_p2_count += addition

                    # saves objects created by this moment in the database
                    flush()

        print(f'total count of t1 products: {p1_count}')
        print(f'total count of t2 products: {origin_p2_count}')
        print(f'initial ratio: {p2_proc_in_p1}%')
        print(f'  final ratio: {int(total_p2_count / p1_count * 100)}%')

        rollback()
