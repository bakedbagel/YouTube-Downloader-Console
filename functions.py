from pytube import YouTube, Playlist
from pytube.cli import on_progress
from eyed3.id3.frames import ImageFrame
import os, ffmpeg, eyed3, re, requests
import dictionary

clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')
#Set download directory

#Shared functions
#----------------------------------------------------------------------------------------------------------------#
#I don't think this works. I was just thinking to be able to set/reset 'menu_exit' as a variable to change the numerical value if needed
def set_menu_exit(exit_choice):
    dictionary.menu_exit = exit_choice

#Make sure input is an integer
def get_user_choice():
    check_bool = False
    print('')

    while(check_bool == False):
        user_choice = input('Enter selection: ')

        try:
            user_choice = int(user_choice)
            check_bool = True

        except:
            print('Invalid user input. Try again')
            check_bool = False

    return user_choice

#Prompts user for youtube link, also checks to make sure if URL can pass thru youtube function
def get_url():
    clearConsole()
    check_bool = False
    while(check_bool == False):
        url = input('Enter YouTube link to download: ')

        try:
            yt = YouTube(url)
            check_bool = True

        except:
            print('Connection Error. Check for vaild URL and try again.')
            check_bool = False
    
    return url 
    
#Need to remove certain characters for naming the file
def remove_bad_char(str1):
    str2 = str1.replace('/' , '').replace('\\' , '').replace(':' , '').replace('*' , '').replace('?' , '').replace('"' , '').replace('<' , '').replace('>' , '').replace('|' , '').replace("'" , '')
    return str2

#checking for valid playlist link
def get_url_playlist():
    clearConsole()
    check_bool = False
    while(check_bool == False):
        url = input('Enter YouTube playlist to download: ')

        try:
            playlist = Playlist(url)
            check_bool = True

        except:
            print('Connection Error. Check for vaild URL and try again.')
            check_bool = False
    
    return url 

def tag_single(yt):
    #Getting YouTube thumbnail
    response = requests.get(yt.thumbnail_url)
    image = open("image.jpg", 'wb')
    image.write(response.content)
    image.close()

    #using module eyeD3 to change mp3 metadata
    #ffmpeg mp3 metadata handling seemed to not work very well
    eyed = eyed3.load("audio.mp3")
    eyed.tag.title = str(yt.title)
    eyed.tag.artist = str(yt.author)
    eyed.tag.album_artist = str(yt.watch_url)
    eyed.tag.album = "Downloaded with Crata-Downloader"
    eyed.tag.genre = 12 #Save genre as "Other" list can be found here https://eyed3.readthedocs.io/en/latest/plugins/genres_plugin.html
    eyed.tag.images.set(3, open('image.jpg','rb').read(), 'image/jpeg') #https://stackoverflow.com/questions/38510694/how-to-add-album-art-to-mp3-file-using-python-3
    eyed.tag.save()

    os.remove('image.jpg')
    #eyed.tag.publisher = str(yt.watch_url)
    #eyed.tag.comments = "This is a comment!" #not sure why this doesnt work? "attribute can't be set?"

def tag_playlist(playlist, yt, i):
    response = requests.get(yt.thumbnail_url)
    image = open("image.jpg", 'wb')
    image.write(response.content)
    image.close()

    eyed = eyed3.load("audio.mp3")
    eyed.tag.title = str(yt.title)
    eyed.tag.artist = str(yt.author)
    eyed.tag.album_artist = str(yt.watch_url)
    eyed.tag.album = 'Youtube playlist: ' + yt.title
    eyed.tag.genre = 12 #Save genre as "Other" list can be found here https://eyed3.readthedocs.io/en/latest/plugins/genres_plugin.html
    eyed.tag.track_num = (i, playlist.length)
    eyed.tag.images.set(3, open('image.jpg','rb').read(), 'image/jpeg') #https://stackoverflow.com/questions/38510694/how-to-add-album-art-to-mp3-file-using-python-3
    eyed.tag.save()

    os.remove('image.jpg')

#Single Video Functions:
#----------------------------------------------------------------------------------------------------------------#
#Shows streams for youtube object
def get_streams_info(yt):
    clearConsole()
    print('\nTotal Available Streams: ' + str(len(yt.streams)))

    print('\n*------------Avaliable Video Dash Streams: ' + str(len(yt.streams.filter(only_video=True).filter(adaptive=True))) + ' ------------*')
    for stream in yt.streams.filter(only_video=True).filter(adaptive=True).filter(mime_type="video/webm").asc():
        print(stream)
    
    print('\n')
    for stream in yt.streams.filter(only_video=True).filter(adaptive=True).filter(mime_type="video/mp4").asc():
        print(stream)

    print('\n*------------Avaliable Progressive Streams: ' + str(len(yt.streams.filter(progressive=True))) + ' ------------*')
    for stream in yt.streams.filter(progressive=True).desc():
        print(stream)

    print('\n*------------Avaliable Audio Streams: ' + str(len(yt.streams.filter(only_audio=True))) + ' ------------*')
    for stream in yt.streams.filter(only_audio=True).order_by('abr').desc():
        print(stream)

    

    print('\n')

#Downloads and merges highest quality streams - still need to specify what the audio bitrate is. this defaults to 128 kbbs
def download_single_dash(yt):
    
    if os.path.exists(remove_bad_char(yt.title) +'.mp4'):
        print('File already exists. Skipping download.')
    
    else:
        print('\nGetting highest available quality. Download started. Wait... ')
        #audioStream = yt.streams.filter(only_audio=True).desc().first().download(None,'audio.webm')
        #videoStream = yt.streams.filter(only_video=True).filter(adaptive=True).asc().first().download(None,'video.webm')
        hq_dash_audio_stream = yt.streams.filter(only_audio=True).desc().first()
        hq_dash_video_stream = yt.streams.filter(only_video=True).filter(adaptive=True).asc().first()

        audio_file_name = 'audio.webm'
        video_file_name = 'video.webm'

        hq_dash_audio_stream.download(None,audio_file_name)  
        hq_dash_video_stream.download(None,video_file_name)  
        
        print('Download Complete.')

        #os.chdir(dictionary.download_dir)
        metadata = ' -metadata title="' + remove_bad_char(yt.title) + '" -metadata album_artist="' + remove_bad_char(yt.author) + '" -metadata comment="' + yt.watch_url + '" '
        os.system('ffmpeg -i video.webm -i audio.webm' + metadata + '-c:v copy -c:a aac av_merge.mp4')
        
        print('Merge Complete.')

        os.rename('av_merge.mp4', remove_bad_char(yt.title) + '.mp4')
        os.remove(audio_file_name)
        os.remove(video_file_name)

        print('Process complete.')

#Downloads highest resolution progressive download
def download_single_prog(yt):
    #yt.streams.get_highest_resolution().download()
    hq_prog_stream = yt.streams.get_highest_resolution()
    hq_prog_stream.download()
    clearConsole()
    print('Download Complete.\n')

#Downloads highest abr streams and converts to mp3
#I should have a seperated tagging function, possibly download, process function. this gets messy
def download_single_mp3(yt):
    #Adding a download dir to make things neater
    #yt.streams.filter(only_audio=True).order_by('abr').desc().first().download(dictionary.download_dir, 'audio.webm')
    stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()

    if os.path.exists(remove_bad_char(yt.title) + ".mp3"):
        print("File already exists. Skipping download.")

    else:
        abr_yt = stream.abr
        abr_list = re.findall('\d+',abr_yt)
        abr = abr_list[0]

        file_name = 'audio.' + str(stream.subtype)

        stream.download(None, file_name)

        #Telling os to run convert command, -id3v2_verson 3 for metadata tagging
        os.system("ffmpeg -i " + file_name +  " -b:a " + abr + "k -id3v2_version 3 audio.mp3")

        tag_single(yt)

        #File clean up
        os.rename('audio.mp3', remove_bad_char(yt.title) + '.mp3')
        os.remove(file_name)
        
        print('Process complete.')

#Playlist Functions:
#----------------------------------------------------------------------------------------------------------------#
#Download playlist as mp3, error occurs if file mp3 file already exists as name
def download_mp3_playlist(playlist):
    #eyed.tag.track_num(1,20) #can use for playlist
    i=1

    for video in playlist.videos:
        url = video.watch_url
        yt = YouTube(url, on_progress_callback=on_progress)

        stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()

        if os.path.exists(remove_bad_char(yt.title) + 'mp3.'):
            print('File exists already. Skipping download.')

        else:
            file_name = 'audio.' + str(stream.subtype)

            abr_yt = stream.abr
            abr_list = re.findall('\d+',abr_yt)
            abr = abr_list[0]
            
            print(f'Downloading: {yt.title} - Video: #{i} of {playlist.length}')
            stream.download(None, file_name)
            print('')
            os.system("ffmpeg -i " + file_name +  " -b:a " + abr + "k -id3v2_version 3 audio.mp3")
            
            tag_playlist(playlist, yt, i)

            #need to be careful with naming videos to 'yt.title' some characters in youtube videos can throw an error
            os.rename('audio.mp3', remove_bad_char(yt.title) + '.mp3')
            os.remove(file_name)

            print('Process complete.')

        i += 1

def download_dash_playlist(playlist):
    i=1

    for video in playlist.videos:
        url = video.watch_url
        yt = YouTube(url, on_progress_callback=on_progress)

        if os.path.exists(remove_bad_char(yt.title) + '.mp4'):
            print('Files ' + remove_bad_char(yt.title) + '.mp4 already exists. Skipping download.')

        else:
            hq_dash_audio_stream = yt.streams.filter(only_audio=True).desc().first()
            hq_dash_video_stream = yt.streams.filter(only_video=True).filter(adaptive=True).asc().first()

            print(f'Downloading: {yt.title} - Audio: #{i} of {playlist.length}')
            hq_dash_audio_stream.download(None,dictionary.audio_file_name)  
            print(f'Downloading: {yt.title} - Video: #{i} of {playlist.length}')
            hq_dash_video_stream.download(None,dictionary.video_file_name)  
            print('\nDownload Complete.')

            #os.chdir(dictionary.download_dir)
            metadata = ' -metadata track="' + str(i) + '" -metadata title="' + remove_bad_char(yt.title) + '" -metadata album="' + remove_bad_char(playlist.title) + '" -metadata album_artist="' + remove_bad_char(yt.author) + '" -metadata comment="' + yt.watch_url + '" '
            os.system('ffmpeg -i video.webm -i audio.webm' + metadata + '-c:v copy -c:a aac av_merge.mp4')
            print('Merge Complete.')

            # Need to check for bad characters
            os.rename('av_merge.mp4', remove_bad_char(yt.title) + '.mp4')
            os.remove(dictionary.audio_file_name)
            os.remove(dictionary.video_file_name)
            print('Process complete.')

        i += 1

#Download highest quality progressive stream, no tagging
def download_prog_playlist(playlist):
    print(f'Downloading: {playlist.title}')
    for video in playlist.videos:
        video.streams.get_highest_resolution().download()

def get_playlist_info(playlist):
    seconds = 0
    dash_v_filesize = 0
    dash_a_filesize = 0
    prog_filesize = 0

    for video in playlist.videos:
        seconds += video.length

        url = video.watch_url
        yt = YouTube(url)

        dash_v_filesize += yt.streams.filter(only_video=True).filter(adaptive=True).asc().first().filesize_approx
        dash_a_filesize += yt.streams.filter(only_audio=True).desc().first().filesize_approx
        prog_filesize += yt.streams.get_highest_resolution().filesize_approx

    minutes = seconds/60

    # for url in playlist.video_urls:
    #     yt = YouTube(url)
    #     dash_v_filesize += yt.streams.filter(only_video=True).filter(adaptive=True).asc().first().filesize_approx/1000000
    #     dash_a_filesize += yt.streams.filter(only_audio=True).desc().first().filesize_approx/1000000
    #     prog_filesize += yt.streams.get_highest_resolution().filesize/1000000
    
    clearConsole()
    print('\nMinutes in playlist: ' + str(minutes) + ' (% min)')
    print('HQ Dash video filesize approx: ' + str(dash_v_filesize/1000000) + 'MBs')
    print('HQ Dash audio filesize approx: ' + str(dash_a_filesize/1000000) + 'MBs')
    print('HQ Prog filesize approx: ' + str(prog_filesize/1000000) + 'MBs')
    print('')

#Menu functions:
#----------------------------------------------------------------------------------------------------------------#
#Print main menu
def print_main_menu():
    clearConsole()
    print('*------------------------------Main Menu------------------------------*')
    for key, value in dictionary.main_menu.items():
        print("Enter " + str(key) + value)

#Print single video sub menu
def print_single_video_menu(yt):
    #Not sure where i should put these. I am duplicating these var's in dash_download also
    hq_prog_stream = yt.streams.get_highest_resolution()
    hq_dash_audio_stream = yt.streams.filter(only_audio=True).desc().first()
    hq_dash_video_stream = yt.streams.filter(only_video=True).filter(adaptive=True).asc().first()

    #Print YouTube details
    print('*-------------------------------Sub Menu------------------------------*')
    print('\nYouTube video title: ' + yt.title)
    print('Selected URL: ' + yt.watch_url)
    print('YouTube video length: ' + str(yt.length/60) +'(% min)')
    print("\n(V)Approx file size for HQ Video Dash Stream: " + "{:,} MBs, Resolution: ".format(hq_dash_video_stream.filesize/1000000) + hq_dash_video_stream.resolution);
    print("(A)Approx file size for HQ Audio Dash Stream: " + "{:,} MBs, ABR: ".format(hq_dash_audio_stream.filesize/1000000) + hq_dash_audio_stream.abr);
    print("(A/V)Approx file size for HQ Progressive Stream: " + "{:,} MBs, Resolution: ".format(hq_prog_stream.filesize/1000000) + hq_prog_stream.resolution);
    
    print('\nCurrent download directory: ' + os.getcwd())
    print('')

    #Print user Options
    for key, value in dictionary.single_video_sub_menu.items():
        print("Enter " + str(key) + value)

#Playlist menu info: URL, # of videos in playlist, approx total file size
#Playlist user choice: download hq dash, download hq prog, download hq mp3
def print_playlist_menu(playlist):
    print('\n*--------------------------Playlist Menu------------------------------*')
    print('Playlist title: ' + playlist.title)
    print('Playlist URL: ' + playlist.playlist_url)
    print('Number of videos in playlist: ' + str(playlist.length))
    print('')


    for key, value in dictionary.playlist_video_sub_menu.items():
        print("Enter " + str(key) + value)