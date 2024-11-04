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
    "vila velha": "https://www.sympla.com.br/eventos/vila-velha-es",
    "fundão": "https://www.sympla.com.br/eventos/fundao-es",
    "guarapari": "https://www.sympla.com.br/eventos/guarapari-es", 
    "viana": "https://www.sympla.com.br/eventos/viana-es"  
}

# Função para remover acentos
def normalize_string(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').lower()

# Função para coletar dados dos eventos
def scrape_events(url, city):
    events = []
    page_number = 1  # Começa na primeira página
    
    while True:
        response = requests.get(url, params={'page': page_number})  # Adiciona o número da página na URL
        soup = BeautifulSoup(response.text, 'html.parser')
        
        event_cards = soup.select(".EventCardstyle__EventInfo-sc-1rkzctc-5")
        
        if not event_cards:  # Se não houver mais eventos, saia do loop
            break
        
        for event_card in event_cards:
            try:
                # Captura a data e hora do evento
                date_time_str = event_card.select_one(".EventCardstyle__EventDate-sc-1rkzctc-6 .fZlvlB").text.strip()
                # Captura o nome do evento
                event_name = event_card.select_one(".EventCardstyle__EventTitle-sc-1rkzctc-7").text.strip()
                # Captura o local do evento
                event_location = event_card.select_one(".EventCardstyle__EventLocation-sc-1rkzctc-8").text.strip()

                # Verifica se o local do evento contém a cidade e o estado "ES"
                if normalize_string(city) in normalize_string(event_location) and "es" in normalize_string(event_location):
                    # Adiciona o evento à lista se não for duplicado
                    event_identifier = (normalize_string(event_name), normalize_string(event_location))  # Identificador único
                    if event_identifier not in [(normalize_string(e["Nome"]), normalize_string(e["Local do Evento"])) for e in events]:
                        events.append({
                            "Nome": event_name,
                            "Local do Evento": event_location,
                            "Data e Hora": date_time_str,
                        })
            except Exception as e:
                print(f"Erro ao capturar evento: {e}")

        page_number += 1  # Avança para a próxima página
    
    return events

# Função para salvar os dados em um arquivo JSON
def save_to_json(data, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Função principal para executar a coleta de eventos
def main():
    all_events = []  # Lista para armazenar todos os eventos coletados

    while True:
        # Coleta eventos de cada cidade
        for city, url in city_urls.items():
            print(f"Coletando eventos para {city.capitalize()}...")
            events = scrape_events(url, city)
            all_events.extend(events)  # Adiciona os eventos coletados à lista

        # Salva todos os eventos em um único arquivo JSON
        save_to_json(all_events, 'data/eventos.json')
        print(f"Todos os eventos coletados e salvos em data/eventos.json.")

        print("A nova coleta será feita em 1 horas.")
        # Aguarda 1 hora antes de coletar novamente
        time.sleep(3600)  # 3600 segundos = 1 hora

# Executa o programa
if __name__ == "__main__":
    main()