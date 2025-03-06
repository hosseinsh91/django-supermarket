from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.utils import json
from accounts.models import Customer, User


@csrf_exempt
def customer_register(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        json_data = json.loads(body_unicode)
        try:
            user = User.objects.create(username=json_data[ 'username' ], first_name=json_data[ 'first_name' ],
                                       last_name=json_data[ 'last_name' ], email=json_data[ 'email' ])
            user.set_password(json_data[ 'password' ])
            user.save()
            customer = Customer.objects.create(user=user, phone=json_data[ 'phone' ], address=json_data[ 'address' ])
            customer.save()
            json_data = {"id": customer.id}
            return JsonResponse(json_data, status=status.HTTP_201_CREATED)
        except:
            json_data = {"message": 'Username already exists.'}
            return JsonResponse(json_data, status=status.HTTP_400_BAD_REQUEST)

    # hint: you should check request method like below
    else:
        data = {"message": 'Method Error'}
        return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)


def customer_list(request):
    if request.method == 'GET':
        try:
            search = request.GET.get('search')
            pro = Customer.objects.filter(Q(user__username__contains=search) | Q(user__first_name__contains=search)
                                          | Q(user__last_name__contains=search) | Q(address__contains=search))
            data = dict(
                customers=list(pro.values('id', 'user__username', 'user__first_name', 'user__last_name', 'user__email',
                                          'phone', 'address', 'balance')))
            for item in data[ "customers" ]:
                item[ 'id' ] = item.pop('id')
                item[ 'username' ] = item.pop('user__username')
                item[ 'first_name' ] = item.pop('user__first_name')
                item[ 'last_name' ] = item.pop('user__last_name')
                item[ 'email' ] = item.pop('user__email')
                item[ 'phone' ] = item.pop('phone')
                item[ 'address' ] = item.pop('address')
                item[ 'balance' ] = item.pop('balance')
            return JsonResponse(data, status=status.HTTP_200_OK)

        except:
            pro = Customer.objects.all()
            data = dict(
                customers=list(pro.values('id', 'user__username', 'user__first_name', 'user__last_name', 'user__email',
                                          'phone', 'address', 'balance')))
            for item in data[ "customers" ]:
                item[ 'id' ] = item.pop('id')
                item[ 'username' ] = item.pop('user__username')
                item[ 'first_name' ] = item.pop('user__first_name')
                item[ 'last_name' ] = item.pop('user__last_name')
                item[ 'email' ] = item.pop('user__email')
                item[ 'phone' ] = item.pop('phone')
                item[ 'address' ] = item.pop('address')
                item[ 'balance' ] = item.pop('balance')
            return JsonResponse(data, status=status.HTTP_200_OK)
    elif request.method != 'GET':
        data = {"message": 'Wrong Method'}
        return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)


def customer_details(request, customer_id):
    if request.method == 'GET':
        if Customer.objects.filter(pk=customer_id).count() == 0:
            data = {"message": 'Customer Not Found.'}
            return JsonResponse(data, status=status.HTTP_404_NOT_FOUND)
        else:
            pro = Customer.objects.get(pk=customer_id)
            data = {'id': pro.pk, 'username': pro.user.username, 'first_name': pro.user.first_name,
                    'last_name': pro.user.last_name, 'email': pro.user.email, 'phone': pro.phone,
                    'address': pro.address, 'balance': pro.balance}
            return JsonResponse(data, status=status.HTTP_200_OK)
    else:
        data = {"message": 'Wrong Method'}
        return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def customer_edit(request, customer_id):
    if request.method == 'POST':
        if Customer.objects.filter(pk=customer_id).count() == 0:
            data = {"message": 'Customer Not Found.'}
            return JsonResponse(data, status=status.HTTP_404_NOT_FOUND)
        else:
            body_unicode = request.body.decode('utf-8')
            edit = json.loads(body_unicode)
            pro = Customer.objects.get(pk=customer_id)
            usi = pro.user.username
            if 'username' in edit or 'password' in edit or 'id' in edit:
                data = {"message": "Cannot edit customer's identity and credentials."}
                return JsonResponse(data, status=status.HTTP_403_FORBIDDEN)
            else:
                count = 0
                n = len(edit)
                try:
                    if 'first_name' in edit:
                        User.objects.filter(username=usi).update(first_name=edit['first_name'])
                        count += 1
                    if 'last_name' in edit:
                        User.objects.filter(username=usi).update(last_name=edit['last_name'])
                        count += 1
                    if 'email' in edit:
                        User.objects.filter(username=usi).update(email=edit['email'])
                        count += 1
                    if 'phone' in edit:
                        Customer.objects.filter(id=customer_id).update(phone=edit['phone'])
                        count += 1
                    if 'address' in edit:
                        Customer.objects.filter(id=customer_id).update(address=edit['address'])
                        count += 1
                    if 'balance' in edit:
                        Customer.objects.filter(id=customer_id).update(balance=edit['balance'])
                        count += 1
                    if count == n:
                        pro = Customer.objects.get(pk=customer_id)
                        data = {'id': pro.pk, 'username': pro.user.username, 'first_name': pro.user.first_name,
                                'last_name': pro.user.last_name, 'email': pro.user.email, 'phone': pro.phone,
                                'address': pro.address, 'balance': pro.balance}
                        return JsonResponse(data, status=status.HTTP_200_OK)
                    else:
                        data = {"message": 'wrong keys.'}
                        return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)
                except ValueError:
                    data = {"message": 'Balance should be integer.'}
                    return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)
    else:
        data = {"message": 'This is not Post Method'}
        return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def customer_login(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        edit = json.loads(body_unicode)
        if request.method == 'POST':
            user = authenticate(request, username=edit[ 'username' ], password=edit[ 'password' ])
            if user is not None:
                login(request, user)
                data = {"message": 'You are logged in successfully.'}
                return JsonResponse(data, status=status.HTTP_200_OK)
            else:
                data = {"message": 'Username or Password is incorrect.'}
                return JsonResponse(data, status=status.HTTP_404_NOT_FOUND)
    else:
        data = {"message": 'This is not Post Method'}
        return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def customer_logout(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            logout(request)
            data = {"message": 'You are logged out successfully.'}
            return JsonResponse(data, status=status.HTTP_200_OK)
        else:
            data = {"message": 'You are not logged in.'}
            return JsonResponse(data, status=status.HTTP_403_FORBIDDEN)
    else:
        data = {"message": 'This is not Post Method'}
        return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)


def customer_profile(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            name = request.user
            custom = Customer.objects.get(user=name)
            data = {'id': name.id, 'username': name.username, 'first_name': name.first_name,
                    'last_name': name.last_name, 'email': name.email, 'phone': custom.phone,
                    'address': custom.address, 'balance': custom.balance}
            return JsonResponse(data, status=status.HTTP_200_OK)
        else:
            data = {"message": 'You are not logged in.'}
            return JsonResponse(data, status=status.HTTP_403_FORBIDDEN)
    else:
        data = {"message": 'Wrong Method'}
        return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)
