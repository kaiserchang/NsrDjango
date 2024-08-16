from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from django.http import JsonResponse
import speech_recognition as sr
from googletrans import Translator
import threading
import queue

text_queue = queue.Queue()
running = True

def transcribe_audio():
    r = sr.Recognizer()
    while running:
        try:
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=0.5)
                audio = r.listen(source, timeout=5, phrase_time_limit=10)
                try:
                    text = r.recognize_google(audio, language="zh-TW")
                    text_queue.put(text)
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    print(f"無法從Google Speech Recognition服務獲得結果; {e}")
        except sr.WaitTimeoutError:
            pass
        except Exception as e:
            print(f"發生錯誤: {e}")

def process_text():
    translator = Translator()
    while running:
        if not text_queue.empty():
            text = text_queue.get()
            try:
                translated_en = translator.translate(text, src='zh-tw', dest='en')
                translated_ja = translator.translate(text, src='zh-tw', dest='ja')
                return {
                    'original': text,
                    'english': translated_en.text,
                    'japanese': translated_ja.text
                }
            except Exception as e:
                print(f"翻譯過程中發生錯誤: {e}")
        return None

def home(request):
    return render(request, 'translator/home.html')

def start_translation(request):
    global running
    running = True
    threading.Thread(target=transcribe_audio).start()
    return JsonResponse({'status': 'started'})

def stop_translation(request):
    global running
    running = False
    return JsonResponse({'status': 'stopped'})

def get_translation(request):
    result = process_text()
    if result:
        return JsonResponse(result)
    return JsonResponse({'status': 'no_data'})
