from pytube import YouTube

yt = YouTube("https://www.youtube.com/watch?v=kn8ZuOCn6r0")
stream = yt.streams.get_by_itag(251)
stream.download()