import requests

## создание нового юзера
# response = requests.post("http://127.0.0.1:5000/user",
#                         json={"name": "user_1", "password": "Ww12345678", "email": "anonymous@yandex.ru"},
#                         )
# print(response.status_code)
# print(response.text)

## Логин
response = requests.post("http://127.0.0.1:5000/login",
                        json={"name": "user_1", "password": "Ww12345678"},
                        )
print(response.status_code)
print(response.text)



headers = {"Authorization": f"{response.json()['token']}"}


##  создание нового объявления
response = requests.post("http://127.0.0.1:5000/advertisement",
                        json={
                            "header": "PRADAm Pomidori",
                            "description": "Vah, kakie vkusnie",
                            "user_id": 5,
                        },
                         headers=headers
                        )
print(response.status_code)
print(response.text)


## удаление объявление
response = requests.delete("http://127.0.0.1:5000/advertisement/2",
                        json={
                            "user_id": 5,
                        },
                         headers=headers
                        )
print(response.status_code)
print(response.text)



