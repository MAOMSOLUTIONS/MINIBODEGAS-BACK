import requests

# URL de la API

    

# Headers de la solicitud
headers = {
    "transId": "3",
    "transactionSrc": "Cinlat WS",
    "AccessLicenseNumber": "AD9AAC0C2B8D5AD2",
    "Username": "Ralvarez.is",
    "Password": "CinlatLogistics2022$"
}

numero_guia = '1Z607V1V0460883727'
url = f'https://wwwcie.ups.com/track/v1/details/{numero_guia}'



# Realizar la solicitud GET sin verificar el certificado SSL
response = requests.get(url, headers=headers, verify=False)

# Verificar si la solicitud fue exitosa
if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print(f"Error: {response.status_code} - {response.text}")
