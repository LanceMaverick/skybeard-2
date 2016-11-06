import omdb

def search(message,title):
    #makes the imdb search url if match not found
    def build_imdb_url(title):
        title_list = [element.strip() for element in title.split(' ')]
        url_elements = [
                'http://www.imdb.com/find?ref_=nv_sr_fn&q=',
                '+'.join(title_list),
                '&s=all'
                ]
        url = ''.join(url_elements)
        return url
    
    #poll api
    result = omdb.get(title=title)
    if not result:
        message.reply_text('I could not find what you were looking for. Try here: ')
        message.reply_text(build_imdb_url(title))
        #sendText(bot,message.chat_id,str(buildImdbUrl(title)),True)
    else:
        film = result.title
        year = result.year
        director = result.director
        metascore = result.metascore
        imdbscore = result.imdb_rating
        plot = result.plot
        poster = result.poster
        imdb = 'http://www.imdb.com/title/'+result.imdb_id
        
        #exception handling for movies with no poster   
        message.reply_photo(photo=poster)
        reply = (
                'Title: '+film+'\n'
                'Year: '+year+'\n'
                'Director: '+director+'\n'
                'Metascore: '+metascore+'\n'
                'IMDb rating: '+imdbscore+'\n'
                'Plot:\n'+plot
                )     

        message.reply_text(reply)
        message.reply_text(imdb, parse_mode = 'Markdown')
