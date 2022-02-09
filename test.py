import requests

# titulo = 'Harry Potter'
# dur = '1:39'
# director = 'George Lucas XD'
# categoria = 'Terror'
# protag = 'Daniel Radcliffe'

titulo = 'Avengers Endgame'
dur = '2:39'
director = 'Hermanos Russo'
categoria = 1
protag = 'Robert Downey JR'

url = f'http://127.0.0.1:5000/registrar_pelicula?titulo={titulo}&dur={dur}&director={director}&categoria={categoria}&protag={protag}'

print(url)
#requests.post(url)