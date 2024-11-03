import requests
from bs4 import BeautifulSoup
import json
import time
import os
import unicodedata

# Mapeamento de entradas de cidade para URLs
city_urls = {
    "serra": "https://www.sympla.com.br/eventos/serra-es",
    "vitoria": "https://www.sympla.com.br/eventos/vitoria-es",
    "cariacica": "https://www.sympla.com.br/eventos/cariacica-es",
    "vila velha": "https://www.sympla.com.br/eventos/vila-velha-es"
}

# Função para remover acentos
def normalize_string(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').lower()

# Função para coletar dados dos eventos
def scrape_events(url, city):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    events = []
    
    for event_card in soup.select(".EventCardstyle__EventInfo-sc-1rkzctc-5"):
        try:
            # Captura a data e hora do evento
            date_time_str = event_card.select_one(".EventCardstyle__EventDate-sc-1rkzctc-6 .fZlvlB").text.strip()
            # Captura o nome do evento
            event_name = event_card.select_one(".EventCardstyle__EventTitle-sc-1rkzctc-7").text.strip()
            # Captura o local do evento
            event_location = event_card.select_one(".EventCardstyle__EventLocation-sc-1rkzctc-8").text.strip()

            # Verifica se o local do evento contém o nome da cidade (insensível a maiúsculas)
            if normalize_string(city) in normalize_string(event_location):
                # Adiciona o evento à lista
                events.append({
                    "Nome": event_name,
                    "Local do Evento": event_location,
                    "Data e Hora": date_time_str,
                })
        except Exception as e:
            print(f"Erro ao capturar evento: {e}")

    return events

# Função para salvar os dados em um arquivo JSON
def save_to_json(data, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Função principal para executar a coleta de eventos
def main():
    all_events = []
    
    # Solicita ao usuário a cidade
    user_input = input("Digite a cidade que deseja buscar (Serra, Vitória, Cariacica, Vila Velha): ")
    
    # Normaliza a entrada do usuário
    normalized_input = normalize_string(user_input)

    # Verifica se a cidade está no mapeamento
    if normalized_input in city_urls:
        url = city_urls[normalized_input]
    else:
        print("Cidade não reconhecida. Tente novamente.")
        return  # Sai da função se a cidade não for válida
    
    while True:
        all_events.extend(scrape_events(url, user_input))  # Passa a cidade para a função
        
        # Salva os eventos no arquivo JSON
        save_to_json(all_events, 'data/eventos.json')
        print(f"Eventos coletados e salvos em data/eventos.json. A nova coleta será feita em 6 horas.")

        # Aguarda 6 horas antes de coletar novamente
        time.sleep(21600)  # 21600 segundos = 6 horas

# Executa o programa
if __name__ == "__main__":
    main()
