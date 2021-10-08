from pytube import YouTube, Playlist
from pytube.cli import on_progress
#from Main.functions import print_playlist_menu
#import ffmpeg, os
import functions, dictionary


#In order to get this working, you must have:
#   ffmpeg installed and path-ed,
#   pytube installed

#Things to work on:
#   Directly referencing ffmpeg instead of os.system(ffmpeg...)
#   Channel options, downloading, etc.
# Hello!!!

#----------------------------------------------------------------------------------------------------------------#
#Decalring variables
sub_choice = 0
user_choice = 0
#should set menu_exit variable in dictionary.py so setting another exit key later down the line might be easier
#functions.set_menu_exit(9) #I dont think this works

#----------------------------------------------------------------------------------------------------------------#
#Main program start
while(user_choice != 9):

    #Print intro screen
    functions.print_main_menu()
    
    #User input for Main Menu
    user_choice = functions.get_user_choice()

    #Single Video Start
    if(user_choice == 1):

        #Getting user input for YouTube link
        url = functions.get_url()
        yt = YouTube(url, on_progress_callback=on_progress)

        #Start Sub Menu Loop
        while(sub_choice != 9):
            #Printing (Single Video) Sub Menu
            functions.print_single_video_menu(yt)

            #User choice for Sub Menu
            sub_choice = functions.get_user_choice()

            #Show number of streams
            if(sub_choice == 1):
                functions.get_streams_info(yt)
                
            #Choose a new url
            elif(sub_choice == 2):
                url = functions.get_url()
                yt = YouTube(url, on_progress_callback=on_progress)

            #Download as highest quality MP3
            elif(sub_choice == 3):
                functions.download_single_mp3(yt)

            #download highest quality progressive stream
            elif(sub_choice == 4):
                functions.download_single_prog(yt)

            #download and merge highest quality DASH / audio streams
            #Program breaks when file already exists (wont overwrite current file with same name)
            elif(sub_choice == 5):
                functions.download_single_dash(yt)

            #invalid selection
            else:
                print(str(sub_choice) +' is an invalid choice. Try again.\n')

    #Start Playlist menu
    elif(user_choice == 2):
        sub_choice = 0
        url = functions.get_url_playlist()
        playlist = Playlist(url)
        
        #Playlist options
        while(sub_choice != 9):
            functions.print_playlist_menu(playlist)
            sub_choice = functions.get_user_choice()

            #Get Playlist info
            if(sub_choice == 1):
                functions.get_playlist_info(playlist)

            #Enter new URL
            if(sub_choice == 2):
                url = functions.get_url_playlist()
                playlist = Playlist(url)

            #Download as mp3
            if(sub_choice == 3):
                functions.download_mp3_playlist(playlist)

            #Download HQ progressive stream
            if(sub_choice == 4):
                functions.download_prog_playlist(playlist)

            #Download HQ DASH streams & Merge
            if(sub_choice == 5):
                functions.download_dash_playlist(playlist)

