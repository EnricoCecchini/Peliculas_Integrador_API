import requests

# titulo = 'Harry Potter'
# dur = '1:39'
# director = 'George Lucas XD'
# categoria = 'Terror'
# protag = 'Daniel Radcliffe'

titulo = 'Esward SCissorhands'
dur = '2:39'
anio = 2011
director = 'Tim Burton'
categoriaid = 3
protag = 'Daniel Radcliffe,Jack Sparrow'

url = f'http://127.0.0.1:5000/registrar_pelicula?titulo={titulo}&anio={anio}&dur={dur}&director={director}&categoriaid={categoriaid}&protag={protag}'

#url = f'http://127.0.0.1:5000/modify_pelicula?pid={pid}&titulo={titulo}&anio={anio}&dur={dur}&director={director}&categoriaid={categoriaid}&protag={protag}'

print(url)
#requests.post(url)