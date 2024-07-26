import pygame
import requests
import io
import curses
import urllib.parse
import json
import Levenshtein

songs = []
accent_mapping = {
    'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
    'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
    'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
    'À': 'A', 'È': 'E', 'Ì': 'I', 'Ò': 'O', 'Ù': 'U',
    'ä': 'a', 'ë': 'e', 'ï': 'i', 'ö': 'o', 'ü': 'u',
    'Ä': 'A', 'Ë': 'E', 'Ï': 'I', 'Ö': 'O', 'Ü': 'U',
    'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o', 'û': 'u',
    'Â': 'A', 'Ê': 'E', 'Î': 'I', 'Ô': 'O', 'Û': 'U',
    'ç': 'c', 'Ç': 'C', 'ñ': 'n', 'Ñ': 'N',
}

def replace_accents(text):
    return ''.join(accent_mapping.get(c, c) for c in text)

def buscar_y_cargar(query):
    global songs
    url = "https://hayqbhgr.slider.kz/vk_auth.php?q="
    songs = []
    query = urllib.parse.quote(query)

    r = requests.get(url + query)
    posibles_canciones = json.loads(r.text)

    # Cargar canciones en la lista
    for elem in posibles_canciones["audios"]['']:
        song_name = elem["tit_art"]
        songs.append({"cancion": song_name, "url": elem['url']})
    query_normalized = replace_accents(query.lower())  # Normalizar consulta
    for song in songs:
        song["cancion_normalized"] = replace_accents(song["cancion"].lower())

    songs.sort(key=lambda song: Levenshtein.distance(query_normalized, song["cancion_normalized"]))

    # Imprimir canciones ordenadas
    for song in songs:
        print(song["cancion"])

def download_audio(url):
    response = requests.get(url)
    return io.BytesIO(response.content)

def play_music(audio_file):
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()

def main(stdscr):
    global songs
    # Inicializar pygame
    pygame.init()
    pygame.mixer.init()

    current_song_index = 0
    first_visible_index = 0
    playing = False
    curses.curs_set(0)  # Ocultar el cursor
    stdscr.nodelay(1)
    stdscr.timeout(100)

    height, width = stdscr.getmaxyx()

    while True:
        stdscr.clear()
        visible_songs = songs[first_visible_index:first_visible_index + height - 1]
        for idx, song in enumerate(visible_songs):
            display_str = replace_accents(song["cancion"])
          
            if len(display_str) > width:
                display_str = display_str[:width - 3] + "..."
            if idx + first_visible_index == current_song_index:
                stdscr.addstr(idx, 0, display_str, curses.A_REVERSE)
            else:
                stdscr.addstr(idx, 0, display_str)
        
        stdscr.refresh()
        
        key = stdscr.getch()

        if key == curses.KEY_UP:
            if current_song_index > 0:
                current_song_index -= 1
                if current_song_index < first_visible_index:
                    first_visible_index -= 1
        elif key == curses.KEY_DOWN:
            if current_song_index < len(songs) - 1:
                current_song_index += 1
                if current_song_index >= first_visible_index + height - 1:
                    first_visible_index += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if playing:
                pygame.mixer.music.stop()
            audio_file = download_audio(songs[current_song_index]["url"])
            play_music(audio_file)
            playing = True
        elif key == ord('q'):
            break
        elif key == ord('a'):
            new_song = get_user_input(stdscr, "Ingresa nombre de la canción: ")
            buscar_y_cargar(new_song)

    pygame.quit()

def get_user_input(stdscr, prompt_string):
    curses.echo()
    stdscr.clear()
    stdscr.addstr(0, 0, prompt_string)
    stdscr.refresh()
    input_str = ""
    while True:
        key = stdscr.getch()
        if key in [10, 13]:  # Enter key
            break
        elif key == 27:  # Escape key
            input_str = ""
            break
        elif key == curses.KEY_BACKSPACE or key == 127:
            input_str = input_str[:-1]
        elif 0 <= key <= 255:
            input_str += chr(key)
        stdscr.clear()
        stdscr.addstr(0, 0, prompt_string + input_str)
        stdscr.refresh()
    curses.noecho()
    return input_str

if __name__ == "__main__":
    curses.wrapper(main)
