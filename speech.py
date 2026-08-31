import speech_recognition as sr
import pyttsx3
import threading
import queue


class SpeechManager:

    def __init__(self):

     
        self.recognizer = sr.Recognizer()

        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.5

     
        self.speech_queue = queue.Queue()
        self.current_engine = None
        self.engine_lock = threading.Lock()

        self.speech_thread = threading.Thread(
            target=self._speech_worker,
            daemon=True
        )

        self.speech_thread.start()


    def _speech_worker(self):

        """
        Dedicated thread for Text-to-Speech.

        Every response goes into a queue.
        This thread speaks them one by one.
        """

        while True:

            text = self.speech_queue.get()

            if text is None:
                break

            try:

                print("🔊 Speaking:", text)

                engine = pyttsx3.init()

                with self.engine_lock:
                    self.current_engine = engine

                engine.setProperty(
                    "rate",
                    165
                )

                engine.setProperty(
                    "volume",
                    1.0
                )

                voices = engine.getProperty(
                    "voices"
                )

                if voices:

                    selected_voice = voices[0].id

                    for voice in voices:

                        voice_info = (
                            str(voice.name) +
                            " " +
                            str(voice.id)
                        ).lower()

                        if "english" in voice_info:

                            selected_voice = voice.id
                            break

                    engine.setProperty(
                        "voice",
                        selected_voice
                    )

                engine.say(text)

                engine.runAndWait()

                engine.stop()

                del engine

                print("✅ Finished speaking")

            except Exception as error:

                print(
                    "❌ Text-to-Speech error:",
                    error
                )

            finally:

                with self.engine_lock:
                    self.current_engine = None

                self.speech_queue.task_done()


    def speak(self, text):

        """
        Add text to speech queue.
        """

        if not text:
            return

        self.speech_queue.put(
            str(text)
        )

    def stop_speaking(self):

        while True:

            try:
                self.speech_queue.get_nowait()
                self.speech_queue.task_done()
            except queue.Empty:
                break

        with self.engine_lock:
            if self.current_engine is not None:
                try:
                    self.current_engine.stop()
                except Exception:
                    pass


    
    def listen(self):

        try:

            with sr.Microphone() as source:

                print(
                    "🎤 Adjusting microphone..."
                )

                self.recognizer.adjust_for_ambient_noise(
                    source,
                    duration=0.5
                )

                print(
                    "🎤 Listening..."
                )

                audio = self.recognizer.listen(
                    source,
                    timeout=7,
                    phrase_time_limit=12
                )

            print(
                "🧠 Recognizing..."
            )

            text = self.recognizer.recognize_google(
                audio,
                language="en-US"
            )

            print(
                "You said:",
                text
            )

            return text

        except sr.WaitTimeoutError:

            print(
                "No speech detected."
            )

            return None

        except sr.UnknownValueError:

            print(
                "Could not understand audio."
            )

            return None

        except sr.RequestError as error:

            print(
                "Speech recognition service error:",
                error
            )

            return None

        except Exception as error:

            print(
                "Microphone error:",
                error
            )

            return None
