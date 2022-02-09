import requests

# titulo = 'Harry Potter'
# dur = '1:39'
# director = 'George Lucas XD'
# categoria = 'Terror'
# protag = 'Daniel Radcliffe'

titulo = 'Harry Potter'
dur = '2:39'
anio = 2001
director = 'J.K Rowling'
categoria = 1
protag = 'Daniel Radcliffe'

url = f'http://127.0.0.1:5000/registrar_pelicula?titulo={titulo}&anio={anio}&dur={dur}&director={director}&categoria={categoria}&protag={protag}'

print(url)
#requests.post(url)