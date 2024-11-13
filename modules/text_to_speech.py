import pyttsx3
import time

# Инициализация pyttsx3
engine = pyttsx3.init()

# Установка параметров
engine.setProperty('rate', 150)  # Скорость речи
engine.setProperty('volume', 1)  # Громкость (0.0 до 1.0)

# Текст для озвучки
text = "My ex told me if i ever got a cat, he’d do his best to run it over with his car because he hates cats. \n\nThat was after i told him i loved cats and wanted go volunteer in a shelter."

# Озвучиваем текст
engine.save_to_file(text, 'output_audio.mp3')

# Запуск озвучки
engine.runAndWait()

print("Текст сохранен в файл output_audio.mp3")