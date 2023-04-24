import speech_recognition as sr
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import json
from bs4 import BeautifulSoup
import requests
import chardet
import pyfiglet
from rich.console import Console
from rich.style import Style

# import nltk
# nltk.download('punkt')
# nltk.download('stopwords')

r = sr.Recognizer()
figlet = pyfiglet.Figlet()

with open('config.json', mode='r', encoding="utf-8") as configFile:
    config = json.load(configFile)

prefix = config['name']
actions = [action['name'] for action in config['actions']]
astronomyKeyWords = config['keywords']


def refine_phrase(phrase, action):
    tokens = word_tokenize(phrase)

    stop_words = set(stopwords.words('portuguese'))
    filtered_tokens = [
        word for word in tokens if word.lower() not in stop_words]

    refined_phrase = ' '.join(filtered_tokens)

    refined_phrase = refined_phrase.replace(prefix, '')

    refined_phrase = refined_phrase.replace(action, '')

    refined_phrase = refined_phrase.strip()

    return refined_phrase


def scrapperSummary(search_terms):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
    }

    response = requests.get(
        f'https://www.google.com/search?q={search_terms}&tbm=nws', headers=headers).text

    soup = BeautifulSoup(response, 'html.parser')

    results = soup.find_all('div', {'class': 'SoaBEf'})

    for result in results:
        title = result.find('div', {'role': 'heading'}).text
        link = result.find('a', href=True)['href']

        print(title)
        print(link)
        print('------------------------')

    return results


def deepScrapper(search_terms, retry=0):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
    }

    response = requests.get(
        f'https://www.google.com/search?q={search_terms}', headers=headers)

    soup = BeautifulSoup(response.text, 'html.parser')

    search_results = soup.find_all('div', {'class': 'g'})
    first_result = search_results[retry].find('a')['href']

    try:
        response = requests.get(first_result, headers=headers)

        encoding = chardet.detect(response.content)['encoding']
        decoded_response = response.content.decode(encoding)

        soup = BeautifulSoup(decoded_response, 'html.parser')

        main_content = soup.find('main')
        paragraphs = main_content.find_all('p')

        paragraphs_without_class = [
            paragraph for paragraph in paragraphs if not paragraph.has_attr('class')]

        finalResult = [
            paragraph.text for paragraph in paragraphs_without_class]

        finalResult = " ".join(finalResult)
        console = Console()
        console.print("")
        console.print(finalResult, style=Style(color="green"))
        return finalResult
    except Exception as e:
        # print(e)
        if retry + 1 > 5:
            print('Não foi possível encontrar um resultado')
            return None
        return deepScrapper(search_terms, retry + 1)


def hasValidPrefix(text):
    return text.lower().startswith(prefix.lower())


def isTurnOffCommand(text):
    return 'desligar' in text.lower()


def hasValidKeyword(text):
    for keyword in astronomyKeyWords:
        if keyword.lower() in text.lower():
            return True
    return False


def hasValidAction(text):
    for action in actions:
        if action.lower() in text.lower():
            return action.lower()
    return False


def executeAction(action, search_terms):
    if action.lower() == 'notícias':
        scrapperSummary(search_terms)
    elif action.lower() == 'pesquisar':
        deepScrapper(search_terms)
    else:
        print('Ação não encontrada')
        return False


def welcomeMessage():
    print(figlet.renderText(prefix))
    print(f'Olá, eu sou {prefix}, assistente pessoal.')
    print(
        f'Para executar uma ação, diga "{prefix}, {actions[0]} ou {actions[1]}, termos de busca"')
    print(f'Para desligar, diga "{prefix}, desligar"')
    print('')


def listen(audio=None):
    if audio:
        with sr.AudioFile(audio) as source:
            audio = r.listen(source)
            return audio
    else:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            print("Ouvindo...")
            audio = r.listen(source, timeout=5)
            return audio


def initArtemis():
    welcomeMessage()
    isRunning = True
    while isRunning:
        audio = listen()
        try:
            text = r.recognize_google(audio, language='pt-BR')
            print("Você disse: " + text)
            if hasValidPrefix(text):
                if isTurnOffCommand(text):
                    print("Desligando...")
                    isRunning = False
                    break
                if hasValidKeyword(text):
                    action = hasValidAction(text)
                    if action:
                        print(f"Executando a ação '{action}'...")
                        search_terms = refine_phrase(text, action)
                        print(
                            f"Termos de busca: '{search_terms.split(' ')}'")
                        executeAction(action, search_terms)
                    else:
                        print('Ação não encontrada')
                else:
                    print('Palavra-chave não encontrada')

        except sr.UnknownValueError:
            print("Não entendi o que você disse")
        except sr.RequestError as e:
            print(
                "Erro ao acessar o serviço de reconhecimento de fala; {0}".format(e))


if __name__ == '__main__':
    initArtemis()
