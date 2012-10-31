import mimetypes
import cmd
import os
import os.path
import sys
import random
import Queue
import thread
import string
import glob


import pygame.mixer
pygame.mixer.init()

CHUNK = 1024

class MusicPlayer(cmd.Cmd):
    def __init__(self):
        print "Starting Panpype"
        cmd.Cmd.__init__(self)
        self.cur_song = None
        self.cwd = os.getcwd()
        self.loop = False
        self.prompt = unichr(9836) + " " if sys.stdout.encoding == "cp1252" else "$ "
        self.songs = Queue.Queue()

        self._init_decoders()
        
        self.greetings = ["Welcome to the Jam",
                          "It's Music Time",
                          "Happy Harping!"]
        print random.choice(self.greetings)
    def _init_decoders(self):
        pass
    def do_cd(self, line):
        os.chdir(line)
        self.cwd = os.getcwd()
    def do_ls(self, line):
        "Lists the current working directory. If given the argument 'music' only lists music. If given the argument 'dir' only list directories."
        if not line:
            self._pretty_table(os.listdir(self.cwd))
        elif line == "music":
            glob.glob
        elif line == "dir":
            dirs = []
            for each_file in os.listdir(self.cwd):
                if os.path.isdir(each_file): dirs.append(each_file)
            self._pretty_table(dirs)

    def _pretty_table(self, items):
        row_counter = 0
        for item in items:
            maxlenth = 25
            if len(item) > 25: item = item[:25 - 3] + "..."
            print "%-25s" % item,
            row_counter += 1
            if row_counter == 3:
                row_counter = 0
                print ""
        print ""
                
            
    def do_loop(self, line):
        "Use the arguments 'on' and 'off to turn the loop on and off. Use no arguments to get the current loop state."
        if not line:
            print "Loop is %s" % ("On" if self.loop else "Off")
        else:
            if line.lower() == "on":
                self.loop = True
                if self.cur_song != None: self.songs.put(self.cur_song)
            elif line.lower() == "off":
                self.loop = False
    def do_play(self, line):
        "Play a list of files in order."
        if not line:
            pygame.mixer.unpause()
            if self.songs.empty() and self.cur_song == None:
                print "No songs in queue."
        else:
            songs = self._split_text(line)
            for song in songs:
                if song not in os.listdir(self.cwd):
                    print "File <%s> not found." % (song)
                else:
                    with songs_queue_lock: self.songs.put({"name" : song, "type" : self._get_type(song)})
    def do_pause(self, line):
        "Pauses the current song."
        pygame.mixer.pause()
    def do_clear(self, line):
        "Clears all current songs."
        with songs_queue_lock:
            self.songs = Queue.Queue()
            pygame.mixer.stop()
    def do_echo(self, line):
        "Repeats the line."
        print line
    def do_quit(self, line):
        "Quits the program, add a ! argument to quit instantly."
        if "!" in line.split(): return True
        else:
            choice = raw_input("Are you sure? y/n: ").lower()
            if choice in ["yes", "y"]:
                return True
    def do_EOF(self, line):
        print ""
        return True
    def _get_type(self, file_name):
        "Returns the file ending of a file. i.g .mp3"
        mimetype = mimetypes.guess_type(file_name)[0]
        return mimetypes.guess_extension(mimetype)
    def _split_text(self, line):
        line = line.strip()

        inWord = True
        inQuotes = False
        words = []
        word = ""
        for char in line:
            if char == "\"":
                if inQuotes:
                    words.append(word)
                    word = ""
                inQuotes = not inQuotes
            elif char in string.whitespace and not inQuotes:
                if word:
                    words.append(word)
                    word = ""
            else:
                word += char
        if word: words.append(word)

        return words

def play_music(root):
    while True:
        songs_queue_lock.acquire()
        if not root.songs.empty() and not pygame.mixer.get_busy():
            song = root.songs.get()
            root.cur_song = song
            if root.loop: root.songs.put(song)
            songs_queue_lock.release()
            file_name = song["name"]
            file_type = song["type"]

            sound_obj = pygame.mixer.Sound(file_name)
            sound_obj.play()
            songs_queue_lock.acquire()
        if not pygame.mixer.get_busy(): root.cur_song = None
            
        songs_queue_lock.release()
    
if __name__ == "__main__":
    root = MusicPlayer()
    songs_queue_lock = thread.allocate_lock()
    thread.start_new_thread(play_music, (root,))
    root.cmdloop()
    pygame.mixer.quit


