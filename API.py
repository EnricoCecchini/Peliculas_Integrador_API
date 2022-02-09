from flask import Flask, jsonify, request
from flask_cors import CORS
import loaf

app = Flask(__name__)
CORS(app)

loaf.bake(
    host='127.0.0.1',
    port=3306,
    user='root',
    pasw='',
    db='peliculas2'
)

# Obtener todas las peliculas
@app.route('/dashboard')
def dashboard():
    peliculas = list(loaf.query(''' SELECT director.nombre, PD.titulo, PD.duracion, PD.peliculaID, PD.ano
                                    FROM (SELECT P.titulo, P.duracion, P.peliculaID, P.ano, directorID 
                                        FROM (SELECT titulo, duracion, peliculaID, ano FROM pelicula) AS P
                                            INNER JOIN dirige ON P.peliculaID = dirige.peliculaID) AS PD
                                    INNER JOIN director ON PD.directorID = director.directorID '''))

    if not peliculas:
        return jsonify({
            'success': 'False',
            'message': 'No hay peliculas registradas'
        })
    
    listaPeliculas = []

    for i in range(len(peliculas)):
        listaPeliculas.append({
            'Pelicula': {
                'peliculaID': peliculas[i][3],
                'titulo': peliculas[i][1],
                'director': peliculas[i][0],
                'duracion': f'{int(peliculas[i][2])//60}:{int(peliculas[i][2])%60}'
            }
        })

    return jsonify({
        'peliculas': listaPeliculas
    })

# Obtener todas las peliculas de la misma categoria
@app.route('/dashboard_filtrado')
def dashboard_filtrado():
    categoriaID = request.args.get('categoria')

    if not categoriaID:
        return jsonify({
            'success': 'False',
            'message': 'Selecciona la categoria'
        })

    try:
        categoriaID = loaf.query(f''' SELECT categoriaid  
                                    FROM categoria
                                    WHERE categoriaID = '{categoriaID}' ''')[0][0]
    except IndexError:
        return jsonify({
                'success': 'False',
                'message': 'La categoria no existe'
            })
    
    peliculas = loaf.query(f''' SELECT director.nombre, PD.titulo, PD.duracion, PD.peliculaID
                                FROM (SELECT P.titulo, P.duracion, P.peliculaID, directorID
                                    FROM (SELECT pelicula.titulo, CP.peliculaID, pelicula.duracion
                                        FROM pelicula INNER JOIN (SELECT peliculaID FROM movie_cat 
                                            WHERE categoriaID = '{categoriaID}') AS CP
                                        ON pelicula.peliculaID = CP.peliculaID) AS P
                                    INNER JOIN dirige ON P.peliculaID = dirige.peliculaID) AS PD
                                INNER JOIN director ON PD.directorID = director.directorID
                            ''')
    
    if not peliculas:
        return jsonify({
            'success': 'False',
            'message': 'No hay peliculas registradas de esta categoria'
        })
    
    listaPeliculas = []

    for i in range(len(peliculas)):
        listaPeliculas.append({
            'Pelicula': {
                'peliculaID': peliculas[i][3],
                'titulo': peliculas[i][1],
                'director': peliculas[i][0],
                'duracion': f'{int(peliculas[i][2])//60}:{int(peliculas[i][2])%60}'
            }
        })

    return jsonify({
        'peliculas': listaPeliculas
    })

@app.route('/get_categorias')
def get_categorias():
    categorias = loaf.query(''' SELECT categoriaID, descripcion FROM categoria''')

    listaCat = []

    for i in range(len(categorias)):
        listaCat.append({
            'categoriaID': categorias[i][0],
            'descripcion': categorias[i][1]
        })
    
    return jsonify({
        'categorias': listaCat
    })


@app.route('/registrar_pelicula')
def registrar_pelicula():
    titulo = request.args.get('titulo')
    anio = request.args.get('anio')
    dur = request.args.get('dur')
    director = request.args.get('director')
    categoria = request.args.get('categoria')
    protag = request.args.get('protag')

    if not (titulo and dur and director and categoria and protag):
        return jsonify({
            'success': 'False',
            'message': 'Faltan campos'
        })
    
    dur = dur.split(':')
    durMin = int(dur[0]) * 60 + int(dur[1])

    peliculaExists = False
    
    # Checar si director y protagonista ya existen si no agregarlos
    directorID = loaf.query(f''' SELECT directorID FROM director WHERE nombre = '{director}' ''')
    peliculaID = loaf.query(f''' SELECT peliculaID FROM pelicula WHERE titulo = '{titulo}' ''')

    if bool(directorID and peliculaID):
        peli = loaf.query(f''' SELECT peliculaID FROM dirige WHERE directorID = '{directorID[0][0]}' AND peliculaID = '{peliculaID[0][0]}' ''')
        if peli:
            peliculaExists = True
        else:
            peliculaExists = False

    if peliculaExists:
        return jsonify({
            'success': 'False',
            'message': 'La pelicula ya esta registrada'
        })

    try:
        protagID = loaf.query(f''' SELECT protagonistaID FROM protagonista WHERE nombre='{protag}' ''')[0][0]
    except IndexError:
        protagID = False
        
    if directorID and protagID:
        directorID = directorID[0][0]
        loaf.query(f'''INSERT INTO pelicula (titulo, duracion, ano)
                        VALUES ('{titulo}', '{durMin}', '{anio}') ''')
                
        peliculaID = loaf.query(f''' SELECT peliculaID FROM pelicula WHERE titulo = '{titulo}' AND ano = '{anio}' ''')[0][0]
        
        loaf.query(f''' INSERT INTO actua (peliculaID, protagonistaID)
                    VALUES ('{peliculaID}', '{protagID}') ''')
        
        loaf.query(f''' INSERT INTO dirige (peliculaID, directorID)
                    VALUES ('{peliculaID}', '{directorID}')''')
        
        loaf.query(f''' INSERT INTO movie_cat (peliculaID, categoriaID)
                    VALUES ('{peliculaID}', '{categoria}') ''')
    
    elif directorID and not protagID:
        directorID = directorID[0][0]
        
        loaf.query(f'''INSERT INTO pelicula (titulo, duracion, ano)
                        VALUES ('{titulo}', '{durMin}', '{anio}') ''')
                
        peliculaID = loaf.query(f''' SELECT peliculaID FROM pelicula WHERE titulo = '{titulo}' AND ano = '{anio}' ''')[0][0]
        
        loaf.query(f''' INSERT INTO protagonista (nombre)
                    VALUES ('{protag}') ''')

        protagID = loaf.query(f''' SELECT protagonistaID FROM protagonista WHERE nombre = '{protag}' ''')[0][0]

        loaf.query(f''' INSERT INTO actua (peliculaID, protagonistaID)
                    VALUES ('{peliculaID}', '{protagID}') ''')
        
        loaf.query(f''' INSERT INTO dirige (peliculaID, directorID)
                    VALUES ('{peliculaID}', '{directorID}')''')
        
        loaf.query(f''' INSERT INTO movie_cat (peliculaID, categoriaID)
                    VALUES ('{peliculaID}', '{categoria}') ''')
    
    elif protagID and not directorID:
        loaf.query(f'''INSERT INTO pelicula (titulo, duracion, ano)
                        VALUES ('{titulo}', '{durMin}', '{anio}') ''')
                
        peliculaID = loaf.query(f''' SELECT peliculaID FROM pelicula WHERE titulo = '{titulo}' AND ano = '{anio}' ''')[0][0]

        
        loaf.query(f''' INSERT INTO director (nombre)
                    VALUES ('{director}') ''')

        directorID = loaf.query(f''' SELECT directorID FROM director WHERE nombre = '{director}' ''')[0][0]
        
        loaf.query(f''' INSERT INTO actua (peliculaID, protagonistaID)
                    VALUES ('{peliculaID}', '{protagID}') ''')
        
        loaf.query(f''' INSERT INTO dirige (peliculaID, directorID)
                    VALUES ('{peliculaID}', '{directorID}')''')
        
        loaf.query(f''' INSERT INTO movie_cat (peliculaID, categoriaID)
                    VALUES ('{peliculaID}', '{categoria}') ''')

    else:
        loaf.query(f'''INSERT INTO pelicula (titulo, duracion, ano)
                        VALUES ('{titulo}', '{durMin}', '{anio}') ''')
                
        peliculaID = loaf.query(f''' SELECT peliculaID FROM pelicula WHERE titulo = '{titulo}' AND ano = '{anio}' ''')[0][0]

        loaf.query(f''' INSERT INTO protagonista (nombre)
                    VALUES ('{protag}') ''')

        protagID = loaf.query(f''' SELECT protagonistaID FROM protagonista WHERE nombre = '{protag}' ''')[0][0]
        
        loaf.query(f''' INSERT INTO director (nombre)
                    VALUES ('{director}') ''')

        directorID = loaf.query(f''' SELECT directorID FROM director WHERE nombre = '{director}' ''')[0][0]
        
        loaf.query(f''' INSERT INTO actua (peliculaID, protagonistaID)
                    VALUES ('{peliculaID}', '{protagID}') ''')
        
        loaf.query(f''' INSERT INTO dirige (peliculaID, directorID)
                    VALUES ('{peliculaID}', '{directorID}')''')
        
        loaf.query(f''' INSERT INTO movie_cat (peliculaID, categoriaID)
                    VALUES ('{peliculaID}', '{categoria}') ''')
    
    return jsonify({
        'success': 'True',
        'message': 'Pelicula registrada'
    })


@app.route('/del_pelicula')
def del_pelicula():
    pid = request.args.get('pid')

    if not pid:
        return jsonify({
            'success': 'False',
            'message': 'Falta ID de pelicula'
        })
    
    loaf.query(f''' DELETE FROM dirige WHERE peliculaID = {pid} ''')
    loaf.query(f''' DELETE FROM actua WHERE peliculaID = {pid} ''')
    loaf.query(f''' DELETE FROM movie_cat WHERE peliculaID = {pid} ''')
    loaf.query(f''' DELETE FROM pelicula WHERE peliculaID = {pid} ''')

    return jsonify({
        'success': 'True',
        'message': 'Pelicula eliminada'
    })

@app.route('/modify_pelicula')
def modify_pelicula():
    pid = request.args.get('pid')
    titulo = request.args.get('titulo')
    anio = request.args.get('anio')
    dur = request.args.get('dur')
    director = request.args.get('director')
    categoriaID = request.args.get('categoriaid')
    protag = request.args.get('protag')

    if not (pid and titulo and anio and dur and director and categoriaID and protag):
        return jsonify({
            'success': 'False',
            'message': 'Faltan campos'
        })
    
    directorID = loaf.query(f''' SELECT directorID FROM director WHERE nombre='{director}' ''')
    protagonistaID = loaf.query(f''' SELECT protagonistaID FROM protagonista WHERE nombre='{protag}' ''')

    if not bool(directorID):
        loaf.query(f''' INSERT INTO director(nombre)
                        Values('{director}')''')
        
        directorID = loaf.query(f''' SELECT directorID FROM director WHERE nombre='{director}' ''')[0][0]
    
    if not bool(protagonistaID):
        loaf.query(f''' INSERT INTO protagonista(nombre)
                        Values('{protag}')''')
        
        protagonistaID = loaf.query(f''' SELECT protagonistaID FROM protagonista WHERE nombre='{protag}' ''')[0][0]

    loaf.query(f''' UPDATE pelicula
                    SET titulo='{titulo}', ano='{anio}', duracion='{dur}' 
                    WHERE peliculaID = {pid} ''')

    loaf.query(f''' UPDATE dirige
                    SET directorID = '{directorID}'
                    WHERE peliculaID = {pid} ''')

    loaf.query(f''' UPDATE movie_cat
                    SET categoriaID = '{categoriaID}'
                    WHERE peliculaID = {pid} ''')

    loaf.query(f''' UPDATE actua
                    SET protagonistaID = '{protagonistaID}'
                    WHERE peliculaID = {pid}
                ''')
    
    return jsonify({
        'success': 'True',
        'message': 'Datos actualizados exitosamente'
    })

@app.route('/buscar')
def buscar():
    busc = str(request.args.get('param'))

    # checar si busc = titulo, director o protagonista
    q = loaf.query('''  SELECT PD.peliculaID, director.nombre, PD.titulo, PD.duracion, PD.ano
                        FROM (SELECT P.titulo, P.duracion, P.peliculaID, P.ano, directorID 
                            FROM (SELECT titulo, duracion, peliculaID, ano FROM pelicula) AS P
                                INNER JOIN dirige ON P.peliculaID = dirige.peliculaID) AS PD
                        INNER JOIN director ON PD.directorID = director.directorID ''')

    #return jsonify(q)

    listaPeliculas = []
    #f'{int(peliculas[i][2])//60}:{int(peliculas[i][2])%60}'
    for i in range(len(q)):
        if busc in str(q[i][1]) or busc in str(q[i][2]):
            listaPeliculas.append({
                'Pelicula': {
                    'peliculaID': q[i][0],
                    'director': q[i][1],
                    'titulo': q[i][2],
                    'duracion': str(f'{int(q[i][3])//60}:{int(q[i][3])%60}'),
                    'anio': q[i][4]
                }
            })
    
    return jsonify(listaPeliculas)


if __name__ == "__main__":
    app.run(debug=True)