# тестовое задание для osahp

[Тестовов задание](https://yadi.sk/i/-I3tHZAc3TTxDd) для [вакансии](http://osahp.jobingood.com/) Python, Backend developer.

## порядок работы
1. Найдём все категории являющиеся листами дерева категорий.
1. Для каждой такой категории найдём размеченные товары.
1. Найдём процент размеченных данных внутри категории.
1. Найдём наибольшую новую категорию внутри размеченных данных.
1. Разметим данные.

## результаты

Если размечать более-менее аккуратно.

```
$ ./mark_up_products.py
not leaf categories can add: < 1.8%
total count of t1 products: 221198
total count of t2 products:  25570
initial ratio: 11.6%
  final ratio: 58.4%
```

Если размечать всё что можем.

```
$ ./mark_up_products.py -a
not leaf categories can add: < 1.8%
total count of t1 products: 221198
total count of t2 products:  25570
initial ratio: 11.6%
  final ratio: 80.7%
```
