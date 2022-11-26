from django.http import HttpResponse


def create_shopping_list(ingredients, user):
    filename = f'{user.username}_shopping_list.txt'
    shopping_cart = {}
    for ingredient in ingredients:
        name = ingredient[0]
        shopping_cart[name] = {
            'amount': ingredient[2],
            'measurement_unit': ingredient[1]
        }
        shopping_list = ['Список покупок\n']
        for key, value in shopping_cart.items():
            shopping_list.append(
                f'{key}: {value["amount"]} {value["measurement_unit"]}\n'
            )
    response = HttpResponse(
        shopping_list, content_type='text.txt; charset=utf-8'
    )
    response['Content-Disposition'] = (
        f'attachment; filename={filename}.txt'
    )
    return response
