"""
    You can define utility functions here if needed
    For example, a function to create a JsonResponse
    with a specified status code or a message, etc.

    DO NOT FORGET to complete url patterns in market/urls.py
"""
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.utils import json
from rest_framework import status
from .models import Product, OrderRow, Order
from accounts.models import Customer


@csrf_exempt
def product_insert(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        json_data = json.loads(body_unicode)
        try:
            pro = Product(**json_data)
            pro.save()
            json_data = {"id": pro.id}
            return JsonResponse(json_data, status=status.HTTP_201_CREATED)
        except:
            json_data = {"message": 'Duplicate code'}
            return JsonResponse(json_data, status=status.HTTP_400_BAD_REQUEST)

    # hint: you should check request method like below
    else:
        data = {"message": 'Bad error'}
        return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)


def product_list(request):
    if request.method == 'GET':
        try:
            search = request.GET.get('search')
            pro = Product.objects.filter(name__contains=search)
            data = {"products": list(pro.values("id", 'code', "name", "price", 'inventory'))}
            return JsonResponse(data, status=status.HTTP_200_OK)

        except:
            pro = Product.objects.all()
            data = {"products": list(pro.values("id", 'code', "name", "price", 'inventory'))}
            return JsonResponse(data, status=status.HTTP_200_OK)
    else:
        data = {"message": 'Wrong Method'}
        return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)


def product_details(request, product_id):
    if request.method == 'GET':
        if Product.objects.filter(pk=product_id).count() == 0:
            data = {"message": 'Product Not Found.'}
            return JsonResponse(data, status=status.HTTP_404_NOT_FOUND)
        else:
            pro = Product.objects.get(pk=product_id)
            data = {'id': pro.pk, 'code': pro.code, 'name': pro.name, 'price': pro.price, 'inventory': pro.inventory}
            return JsonResponse(data, status=status.HTTP_200_OK)
    else:
        data = {"message": 'Wrong Method'}
        return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)


def edit_inventory(request, product_id):
    if request.method == 'POST':
        if Product.objects.filter(pk=product_id).count() == 0:
            data = {"message": 'Product Not Found.'}
            return JsonResponse(data, status=status.HTTP_404_NOT_FOUND)
        else:
            body_unicode = request.body.decode('utf-8')
            amount = json.loads(body_unicode)
            pro = Product.objects.get(pk=product_id)
            if amount[ 'amount' ] >= 0:
                try:
                    pro.increase_inventory(**amount)
                    data = {'id': pro.pk, 'code': pro.code, 'name': pro.name, 'price': pro.price,
                            'inventory': pro.inventory}
                    return JsonResponse(data, status=status.HTTP_200_OK)
                except:
                    data = {"message": 'This action is not available'}
                    return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)
            elif amount[ 'amount' ] < 0:
                try:
                    pro.decrease_inventory(**amount)
                    data = {'id': pro.pk, 'code': pro.code, 'name': pro.name, 'price': pro.price,
                            'inventory': pro.inventory}
                    return JsonResponse(data, status=status.HTTP_200_OK)
                except:
                    data = {"message": 'Not enough inventory.'}
                    return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)
    else:
        data = {"message": 'This is not Post Method'}
        return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)


def shopping_cart(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            custom = Order.initiate(request.user)
            try:
                raw = OrderRow.objects.filter(order=custom)
                data = dict(total_price=custom.total_price)
                data.update(items=list(raw.values('product__code', 'product__name',
                                                  'product__price', 'amount')))
                for item in data[ "items" ]:
                    item[ 'code' ] = item.pop('product__code')
                    item[ 'name' ] = item.pop('product__name')
                    item[ 'price' ] = item.pop('product__price')
                    item[ 'amount' ] = item.pop('amount')

                return JsonResponse(data, status=status.HTTP_200_OK)
            except:
                data = dict(items=[ ])
                return JsonResponse(data, status=status.HTTP_200_OK)
        else:
            data = {"message": 'You are not logged in.'}
            return JsonResponse(data, status=status.HTTP_403_FORBIDDEN)
    else:
        data = {"message": 'This is not GET Method'}
        return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def add_item(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            body_unicode = request.body.decode('utf-8')
            json_data = json.loads(body_unicode)
            custom = Order.initiate(request.user)
            errors = list()
            for item in json_data:
                try:
                    custom.add_product(item[ 'code' ], item[ 'amount' ])
                except ValueError:
                    error = dict(code=item[ 'code' ], message="Not enough inventory.")
                    errors.append(error)
                    data = dict(errors=errors)
                except OverflowError:
                    error = dict(code=item[ 'code' ], message="Not enough inventory for this product.")
                    errors.append(error)
                    data = dict(errors=errors)
                except:
                    error = dict(code=item[ 'code' ], message="Product not found.")
                    errors.append(error)
                    data = dict(errors=errors)
            if len(errors) == 0:
                raw = OrderRow.objects.filter(order=custom)
                data = dict(total_price=custom.total_price)
                data.update(items=list(raw.values('product__code', 'product__name',
                                                  'product__price', 'amount')))
                for item in data[ "items" ]:
                    item[ 'code' ] = item.pop('product__code')
                    item[ 'name' ] = item.pop('product__name')
                    item[ 'price' ] = item.pop('product__price')
                    item[ 'amount' ] = item.pop('amount')
            else:
                raw = OrderRow.objects.filter(order=custom)
                data = dict(total_price=custom.total_price)
                data.update(errors=errors)
                data.update(items=list(raw.values('product__code', 'product__name',
                                                  'product__price', 'amount')))
                for item in data[ "items" ]:
                    item[ 'code' ] = item.pop('product__code')
                    item[ 'name' ] = item.pop('product__name')
                    item[ 'price' ] = item.pop('product__price')
                    item[ 'amount' ] = item.pop('amount')
                return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST, safe=False)

            return JsonResponse(data, status=status.HTTP_200_OK)
        else:
            data = {"message": 'You are not logged in.'}
            return JsonResponse(data, status=status.HTTP_403_FORBIDDEN)
    else:
        data = {"message": 'This is not Post Method'}
        return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def remove_item(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            body_unicode = request.body.decode('utf-8')
            json_data = json.loads(body_unicode)
            custom = Order.initiate(request.user)
            errors = list()
            for item in json_data:
                if 'amount' in item:
                    try:
                        custom.remove_product(item[ 'code' ], item[ 'amount' ])
                    except ValueError:
                        error = dict(code=item[ 'code' ], message="Not enough amount in cart.")
                        errors.append(error)
                        data = dict(errors=errors)
                    except ZeroDivisionError:
                        error = dict(code=item[ 'code' ], message="Product not found in cart.")
                        errors.append(error)
                        data = dict(errors=errors)
                    except:
                        error = dict(code=item[ 'code' ], message="Product not found.")
                        errors.append(error)
                        data = dict(errors=errors)
                else:
                    try:

                        custom.remove_product(item[ 'code' ], None)
                    except ValueError:
                        error = dict(code=item[ 'code' ], message="Not enough amount in cart.")
                        errors.append(error)
                        data = dict(errors=errors)
                    except ZeroDivisionError:
                        error = dict(code=item[ 'code' ], message="Product not found in cart.")
                        errors.append(error)
                        data = dict(errors=errors)
                    except:
                        error = dict(code=item[ 'code' ], message="Product not found.")
                        errors.append(error)
                        data = dict(errors=errors)
            if len(errors) == 0:
                raw = OrderRow.objects.filter(order=custom)
                data = dict(total_price=custom.total_price)
                data.update(items=list(raw.values('product__code', 'product__name',
                                                  'product__price', 'amount')))
                for item in data[ "items" ]:
                    item[ 'code' ] = item.pop('product__code')
                    item[ 'name' ] = item.pop('product__name')
                    item[ 'price' ] = item.pop('product__price')
                    item[ 'amount' ] = item.pop('amount')
            else:
                raw = OrderRow.objects.filter(order=custom)
                data = dict(total_price=custom.total_price)
                data.update(errors=errors)
                data.update(items=list(raw.values('product__code', 'product__name',
                                                  'product__price', 'amount')))
                for item in data[ "items" ]:
                    item[ 'code' ] = item.pop('product__code')
                    item[ 'name' ] = item.pop('product__name')
                    item[ 'price' ] = item.pop('product__price')
                    item[ 'amount' ] = item.pop('amount')
                return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST, safe=False)

            return JsonResponse(data, status=status.HTTP_200_OK)
        else:
            data = {"message": 'You are not logged in.'}
            return JsonResponse(data, status=status.HTTP_403_FORBIDDEN)
    else:
        data = {"message": 'This is not Post Method'}
        return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def submit(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            custom = Order.initiate(request.user)
            raw = OrderRow.objects.filter(order=custom)
            try:
                custom.submit()
                data = dict(id=custom.id)
                data.update(order_time=custom.order_time)
                data.update(status="submitted")
                data.update(total_price=custom.total_price)
                data.update(raws=list(raw.values('product__code', 'product__name',
                                                 'product__price', 'amount')))
                for item in data[ 'raws' ]:
                    item[ 'code' ] = item.pop('product__code')
                    item[ 'name' ] = item.pop('product__name')
                    item[ 'price' ] = item.pop('product__price')
                    item[ 'amount' ] = item.pop('amount')
                return JsonResponse(data, status=status.HTTP_200_OK)

            except ValueError:
                data = {"message": "Not enough money."}
                return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)
            except TypeError:
                data = {"message": "Bad request."}
                return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)
