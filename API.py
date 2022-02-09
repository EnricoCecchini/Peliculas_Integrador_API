from time import sleep
from flask import Flask, jsonify, request
from flask_cors import CORS
import loaf
import datetime

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
    peliculas = list(loaf.query(''' SELECT director.nombre, PD.titulo, PD.duracion, PD.peliculaID
                                    FROM (SELECT P.titulo, P.duracion, P.peliculaID, directorID FROM
                                        (SELECT titulo, duracion, peliculaID FROM pelicula) AS P
                                        INNER JOIN dirige ON P.peliculaID = dirige.peliculaID) AS PD
                                    INNER JOIN director ON PD.directorID = director.directorID'''))

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
    
    # Checar si director y protagonista ya existen si no agregarlos
    directorID = loaf.query(f''' SELECT directorID FROM director WHERE nombre = '{director}' ''')
    peliculaID = loaf.query(f''' SELECT peliculaID FROM pelicula WHERE titulo = '{titulo}' ''')
    peliculaExists = False

    # return jsonify({
    #     'directorID': directorID,
    #     'peliculaID': peliculaID
    # })

    for p in peliculaID:
        peli = loaf.query(f''' SELECT peliculaID FROM dirige WHERE directorID = '{directorID}' AND peliculaID = '{p}' ''')
        if peli:
            peliculaExists = True
            break
    
    # return jsonify({
    #     'directorID': directorID,
    #     'peliculaID': peliculaID,
    #     'exists': peliculaExists
    # })

    if peliculaExists:
        return jsonify({
            'success': 'False',
            'message': 'La pelicula ya esta registrada'
        })

    try:
        protagID = loaf.query(f''' SELECT protagonistaID FROM protagonista WHERE nombre='{protag}' ''')[0][0]
    except IndexError:
        protagID = False
        
    #return jsonify(protagID)
    if directorID and protagID:
        directorID = directorID[0][0]
        loaf.query(f'''INSERT INTO pelicula (titulo, duracion)
                        VALUES ('{titulo}', '{durMin}') ''')
                
        peliculaID = loaf.query(f''' SELECT peliculaID FROM pelicula WHERE titulo = '{titulo}' AND duracion = '{durMin}' ''')[0]
        
        loaf.query(f'''INSERT INTO dirige (directorID, peliculaID)
                        VALUES ('{directorID}', '{peliculaID}') ''')

        loaf.query(f'''INSERT INTO actua(protagonistaID, peliculaID)
                        VALUES('{protagID}', '{peliculaID}') ''')
        
        loaf.query(f'''INSERT INTO movie_cat(peliculaID, categoriaID)
                        VALUES({peliculaID}, {categoria}) ''')
    
    if directorID and protagID:
        return jsonify({'message': 'Director y protag'})
        # loaf.query(f''' INSERT INTO pelicula (titulo, duracion) 
        #             VALUES ('{titulo}', {durMin}) ''')
        
        # peliculaID = loaf.query(f''' SELECT peliculaID FROM pelicula WHERE titulo = '{titulo}' AND duracion = '{durMin}' ''')

        # loaf.query(f''' INSERT INTO dirige (peliculaID, directorID)
        #             VALUES ('{peliculaID}', '{directorID}') ''')
        
        # loaf.query(f''' INSERT INTO actua (protagonistaID, peliculaID)
        #             VALUES ('{protagID}', '{peliculaID}') ''')
        
        # loaf.query(f''' INSERT INTO movie_cat (peliculaID, categoriaID)
        #             VALUES ('{peliculaID}', '{categoria}') ''')
    
    elif directorID and not protagID:
        return jsonify({'message': 'Director y no protag'})
        # loaf.query(f''' INSERT INTO pelicula (titulo, duracion) 
        #     VALUES ('{titulo}', {durMin})''')
        
        # peliculaID = loaf.query(f''' SELECT peliculaID FROM pelicula WHERE titulo = '{titulo}' AND duracion = '{durMin}' ''')
        
        # loaf.query(f''' INSERT INTO protagonista (nombre)
        #             VALUES ('{protag}') ''')

        # protagID = loaf.query(f''' SELECT protagonistaID FROM protagonista WHERE nombre = '{protag}' ''')
        
        # loaf.query(f''' INSERT INTO actua (protagonistaID, peliculaID)
        #             VALUES ('{protagID}', '{peliculaID}') ''')
        
        # loaf.query(f''' INSERT INTO dirige (peliculaID, directorID)
        #             VALUES ('{peliculaID}', '{directorID}')''')
        
        # loaf.query(f''' INSERT INTO movie_cat (peliculaID, categoriaID)
        #             VALUES ('{protagID}', '{categoria}') ''')
    
    elif protagID and not directorID:
        return jsonify({'message': 'No Director y si protag'})
        # loaf.query(f''' INSERT INTO pelicula (titulo, duracion) 
        #     VALUES ('{titulo}', {durMin})''')
        
        # peliculaID = loaf.query(f''' SELECT peliculaID FROM pelicula WHERE titulo = '{titulo}' AND duracion = '{durMin}' ''')

        
        # loaf.query(f''' INSERT INTO director (nombre)
        #             VALUES ('{director}') ''')

        # directorID = loaf.query(f''' SELECT directorID FROM director WHERE nombre = '{director}' ''')
        
        # loaf.query(f''' INSERT INTO dirige (peliculaID, directorID)
        #             VALUES ('{peliculaID}', '{directorID}')''')
        
        # loaf.query(f''' INSERT INTO actua (peliculaID, protagonistaID)
        #             VALUES ('{peliculaID}', '{protagID}')''')
        
        # loaf.query(f''' INSERT INTO movie_cat (peliculaID, categoriaID)
        #             VALUES ('{peliculaID}', '{categoria}') ''')

    else:
        return jsonify({'message': 'No Director y no protag'})
        # loaf.query(f''' INSERT INTO pelicula (titulo, duracion) 
        #     VALUES ('{titulo}', {durMin})''')
        
        # peliculaID = loaf.query(f''' SELECT peliculaID FROM pelicula WHERE titulo = '{titulo}' AND duracion = '{durMin}' ''')

        # loaf.query(f''' INSERT INTO protagonista (nombre)
        #             VALUES ('{protag}') ''')

        # protagID = loaf.query(f''' SELECT protagonistaID FROM protagonista WHERE nombre = '{protag}' ''')
        
        # loaf.query(f''' INSERT INTO director (nombre)
        #             VALUES ('{director}') ''')

        # directorID = loaf.query(f''' SELECT directorID FROM director WHERE nombre = '{director}' ''')
        
        # loaf.query(f''' INSERT INTO dirige (peliculaID, directorID)
        #             VALUES ('{peliculaID}', '{directorID}') ''')
        
        # loaf.query(f''' INSERT INTO actua (protagonistaID, peliculaID)
        #             VALUES ('{protagID}', '{peliculaID}') ''')
        
        # loaf.query(f''' INSERT INTO movie_cat (peliculaID, categoriaID)
        #             VALUES ('{peliculaID}', '{categoria}') ''')
    
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
    dur = request.args.get('dur')
    director = request.args.get('director')
    categoria = request.args.get('categoria')
    protag = request.args.get('protag').split('_')

    return jsonify(pid, titulo, dur, director, categoria, protag)

@app.route('/buscar')
def buscar():
    busc = request.args.get('param')

    # checar si busc = titulo, director o protagonista
    q = loaf.query(''' SELECT PP.peliculaID, PP.titulo, PP.nombre, PP.duracion, protagonista.nombre
                            FROM (SELECT actua.protagonistaID, PID.titulo, PID.nombre, PID.duracion, PID.peliculaID 
                                FROM    (SELECT PD.titulo, director.nombre, PD.duracion, PD.peliculaID
                                            FROM (SELECT P.titulo, P.duracion, P.peliculaID, directorID FROM
                                                (SELECT titulo, duracion, peliculaID FROM pelicula) AS P
                                                INNER JOIN dirige ON P.peliculaID = dirige.peliculaID) AS PD
                                        INNER JOIN director ON PD.directorID = director.directorID) AS PID
                                INNER JOIN actua ON PID.peliculaID = actua.peliculaID ) AS PP
                            INNER JOIN protagonista ON protagonista.protagonistaID = PP.protagonistaID ''')

    #print(q)

    listaPeliculas = []
    #f'{int(peliculas[i][2])//60}:{int(peliculas[i][2])%60}'
    for i in range(len(q)):
        listaPeliculas.append({
            'Pelicula': {
                'peliculaID': q[i][0],
                'titulo': q[i][1],
                'director': q[i][2],
                'duracion': f'{int(q[i][3])//60}:{int(q[i][3])%60}',
                'protagonista': q[i][4]
            }
        })
    
    resultados = []
    idPelis = []
    
    for i in range(len(listaPeliculas)):
        # Checar si el parametro coincide con 
        # nombre de autor/director o titulo
        pass

    return jsonify({'peliculas': listaPeliculas})


if __name__ == "__main__":
    app.run(debug=True)