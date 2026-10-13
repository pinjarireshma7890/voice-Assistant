
import speech_recognition as sr
import wikipedia
import webbrowser
import os
import datetime
import subprocess
import base64


# SPEAK FUNCTION - WINDOWS BUILT-IN VOICE
def speak(audio):
    message = str(audio)
    print("Amigo:", message)

    try:
        # Safely prepare text for PowerShell
        safe_message = message.replace("'", "''")

        powershell_script = (
            "Add-Type -AssemblyName System.Speech; "
            "$voice = New-Object "
            "System.Speech.Synthesis.SpeechSynthesizer; "
            "$voice.Rate = 0; "
            "$voice.Volume = 100; "
            f"$voice.Speak('{safe_message}'); "
            "$voice.Dispose()"
        )

        encoded_script = base64.b64encode(
            powershell_script.encode("utf-16le")
        ).decode("ascii")

        result = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-EncodedCommand",
                encoded_script
            ],
            capture_output=True,
            text=True,
            errors="replace"
        )

        if result.returncode != 0:
            print("VOICE ERROR:", result.stderr)

    except Exception as error:
        print("VOICE ERROR:", repr(error))


# LISTEN TO COMMANDS
def take_command():
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 0.8

    try:
        with sr.Microphone() as source:
            print("\nListening...")

            recognizer.adjust_for_ambient_noise(
                source, duration=0.5
            )

            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=8
            )

        print("Recognizing...")

        query = recognizer.recognize_google(
            audio,
            language="en-IN"
        )

        print("You said:", query)
        return query.lower()

    except sr.WaitTimeoutError:
        print("No voice detected.")
        return ""

    except sr.UnknownValueError:
        speak("Sorry, I did not understand.")
        return ""

    except sr.RequestError as error:
        print("Recognition ERROR:", repr(error))
        speak("Please check your internet connection.")
        return ""

    except Exception as error:
        print("MICROPHONE ERROR:", repr(error))
        return ""


# MAIN ASSISTANT
def run_amigo():
    speak("Hello! Amigo assistance activated.")

    while True:
        query = take_command()

        if not query:
            continue

        if any(command in query for command in [
            "exit amigo",
            "stop amigo",
            "goodbye",
            "quit",
            "shutdown amigo"
        ]):
            speak("Goodbye! Amigo is shutting down.")
            break

        elif "time" in query:
            current_time = datetime.datetime.now().strftime(
                "%I:%M %p"
            )
            speak(f"The current time is {current_time}")

        elif "date" in query or "today" in query:
            current_date = datetime.datetime.now().strftime(
                "%d %B %Y"
            )
            speak(f"Today's date is {current_date}")

        elif "open google" in query:
            speak("Opening Google.")
            webbrowser.open("https://www.google.com")

        elif "open youtube" in query:
            speak("Opening YouTube.")
            webbrowser.open("https://www.youtube.com")

        elif "open gmail" in query:
            speak("Opening Gmail.")
            webbrowser.open("https://mail.google.com")

        elif "wikipedia" in query:
            topic = query.replace("wikipedia", "").strip()

            if not topic:
                speak("Please tell me the topic name.")
                continue

            try:
                speak("Searching Wikipedia.")
                result = wikipedia.summary(
                    topic,
                    sentences=2
                )
                speak(result)

            except Exception as error:
                print("WIKIPEDIA ERROR:", repr(error))
                speak("Sorry, I could not find that information.")

        elif "open notepad" in query:
            speak("Opening Notepad.")
            os.system("notepad.exe")

        elif "open calculator" in query:
            speak("Opening Calculator.")
            os.system("calc.exe")

        else:
            speak("Sorry, I do not know that command yet.")


# START AMIGO
if __name__ == "__main__":
    try:
        run_amigo()

    except KeyboardInterrupt:
        print("\nAmigo stopped by user.")
