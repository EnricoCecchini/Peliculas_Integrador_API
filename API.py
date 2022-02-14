from flask import Flask, jsonify, request
from flask_cors import CORS
from itsdangerous import json
import loaf
from pymysql import ProgrammingError

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
    peliculas = list(loaf.query(''' SELECT MC2.nombre, MC2.titulo, MC2.duracion, MC2.peliculaID, MC2.ano, categoria.descripcion, MC2.categoriaID
                                    FROM categoria
                                    INNER JOIN (SELECT categoriaID, MC.nombre, MC.titulo, MC.duracion, MC.peliculaID, MC.ano
                                        FROM movie_cat INNER JOIN ( SELECT director.nombre, PD.titulo, PD.duracion, PD.peliculaID, PD.ano
                                            FROM (SELECT P.titulo, P.duracion, P.peliculaID, P.ano, directorID 
                                                FROM (SELECT titulo, duracion, peliculaID, ano FROM pelicula) AS P
                                                INNER JOIN dirige ON P.peliculaID = dirige.peliculaID) AS PD
                                            INNER JOIN director ON PD.directorID = director.directorID ) AS MC
                                        ON MC.peliculaID = movie_cat.peliculaID) AS MC2
                                    ON categoria.categoriaID = MC2.categoriaID '''))

    qActores = loaf.query(''' SELECT PID.protagonistaID, PID.peliculaID, nombre
                                FROM protagonista INNER JOIN 
                                    (SELECT protagonistaID, peliculaID FROM actua) as PID
                                ON protagonista.protagonistaID = PID.protagonistaID''')
                        
    if not peliculas:
        return jsonify({
            'success': 'False',
            'message': 'No hay peliculas registradas'
        })
    
    listaPeliculas = []

    for i in range(len(peliculas)):
        actores = []
        for actor in range(len(qActores)):
            idActor = qActores[actor][1]
            idPeli = peliculas[i][3]

            if idActor == idPeli:
                actores.append({
                    'nombre': qActores[actor][2],
                    'protagID': qActores[actor][0]
                })

        listaPeliculas.append({
                'peliculaID': peliculas[i][3],
                'titulo': peliculas[i][1],
                'anio': peliculas[i][4],
                'director': peliculas[i][0],
                'categoria': peliculas[i][5],
                'categoriaID': peliculas[i][6],
                'duracion': f'{int(peliculas[i][2])//60}:{int(peliculas[i][2])%60}',
                'protagonista': actores
            })

    return jsonify({
        'peliculas': listaPeliculas
    })

# Obtener todas las peliculas de la misma categoria
@app.route('/dashboard_filtrado')
def dashboard_filtrado():
    categoriaID = request.args.get('cat')

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
    
    peliculas = loaf.query(f''' SELECT MC2.nombre, MC2.titulo, MC2.duracion, MC2.peliculaID, MC2.ano, categoria.descripcion, MC2.categoriaID
                                    FROM categoria
                                    INNER JOIN (SELECT categoriaID, MC.nombre, MC.titulo, MC.duracion, MC.peliculaID, MC.ano
                                        FROM movie_cat INNER JOIN ( SELECT director.nombre, PD.titulo, PD.duracion, PD.peliculaID, PD.ano
                                            FROM (SELECT P.titulo, P.duracion, P.peliculaID, P.ano, directorID 
                                                FROM (SELECT titulo, duracion, peliculaID, ano FROM pelicula) AS P
                                                INNER JOIN dirige ON P.peliculaID = dirige.peliculaID) AS PD
                                            INNER JOIN director ON PD.directorID = director.directorID ) AS MC
                                        ON MC.peliculaID = movie_cat.peliculaID AND categoriaID = {categoriaID}) AS MC2
                                    ON categoria.categoriaID = MC2.categoriaID
                            ''')
    
    qActores = loaf.query(''' SELECT PID.protagonistaID, PID.peliculaID, nombre
                                FROM protagonista INNER JOIN 
                                    (SELECT protagonistaID, peliculaID FROM actua) as PID
                                ON protagonista.protagonistaID = PID.protagonistaID''')
    
    if not peliculas:
        return jsonify({
            'success': 'False',
            'message': 'No hay peliculas registradas de esta categoria'
        })
    
    listaPeliculas = []

    for i in range(len(peliculas)):
        actores = []
        for actor in range(len(qActores)):
            idActor = qActores[actor][1]
            idPeli = peliculas[i][3]

            if idActor == idPeli:
                actores.append({
                    'nombre': qActores[actor][2],
                    'protagID': qActores[actor][0]
                })

        listaPeliculas.append({
            'peliculaID': peliculas[i][3],
            'titulo': peliculas[i][1],
            'anio': peliculas[i][4],
            'director': peliculas[i][0],
            'categoria': peliculas[i][5],
            'categoriaID': peliculas[i][6],
            'duracion': f'{int(peliculas[i][2])//60}:{int(peliculas[i][2])%60}',
            'protagonista': actores

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

@app.route('/get_pelicula')
def get_pelicula():
    pid = request.args.get('pid')

    if not pid:
        return jsonify({
            'success': 'False',
            'message': 'Falta ID de pelicula'
        })
    
    exists = loaf.query(f''' SELECT peliculaID from pelicula WHERE peliculaID = {pid} ''')
    
    if not exists:
        return jsonify({
            'success': 'False',
            'message': 'La pelicula no esta registrada'
        })

    p = loaf.query(f''' SELECT nombre, D.directorID, D.descripcion, D.categoriaID, D.peliculaID, D.titulo, D.duracion, D.ano
                                FROM director
                                INNER JOIN (SELECT directorID, PD.descripcion, PD.categoriaID, PD.peliculaID, PD.titulo, PD.duracion, PD.ano
                                FROM dirige 
                                INNER JOIN (SELECT descripcion, PC.categoriaID, PC.peliculaID, PC.titulo, PC.duracion, PC.ano
                                            FROM categoria 
                                            INNER JOIN (SELECT categoriaID, P.peliculaID, titulo, duracion, ano
                                                FROM movie_cat INNER JOIN 
                                                    (SELECT peliculaID, titulo, duracion, ano
                                                        FROM pelicula WHERE peliculaID = {pid}) AS P
                                                ON movie_cat.peliculaID = P.peliculaID) AS PC
                                            ON categoria.categoriaID = PC.categoriaID) AS PD
                                        ON PD.peliculaID = dirige.peliculaID) AS D
                                ON director.directorID = D.directorID
                        ''')[0]
    
    qActores = loaf.query(f''' SELECT PID.protagonistaID, PID.peliculaID, nombre
                                FROM protagonista INNER JOIN 
                                    (SELECT protagonistaID, peliculaID 
                                        FROM actua 
                                        WHERE peliculaID = {pid}) as PID
                                ON protagonista.protagonistaID = PID.protagonistaID''')
    
    print('*'*15)
    print(p)
    print(qActores)

    actores = []
    for i in range(len(qActores)):
        actores.append({
            'nombre': qActores[i][2],
            'protagID': qActores[i][0],
        })

    pelicula = {
        'director': p[0],
        'categoria': p[2],
        'categoriaID': p[3],
        'peliculaID': p[4],
        'titulo': p[5],
        'duracion': f'{int(p[6])//60}:{int(p[6])%60}',
        'anio': p[7],
        'protagonista': actores
    }
    
    return jsonify({'pelicula': pelicula})


@app.route('/registrar_pelicula')
def registrar_pelicula():
    titulo = request.args.get('titulo')
    anio = request.args.get('ano')
    dur = request.args.get('dur')
    director = request.args.get('director')
    categoria = request.args.get('cat')
    protag = request.args.get('protag').replace("'",' ').replace(', ', ',').split(',')

    if not (titulo and anio and dur and director and categoria and protag):
        return jsonify({
            'success': 'False',
            'message': 'Faltan campos'
        })
    
    try:
        dur = dur.split(':')
        dur = int(dur[0]) * 60 + int(dur[1])
    except ValueError:
        return jsonify({
            'success': 'False',
            'message': 'Duracion Invalida'
        })

    if dur < 30:
        return jsonify({
            'success': 'False',
            'message': 'Duracion invalida',
        })

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

    protags = []
    for p in protag:
        try:
            protagID = loaf.query(f''' SELECT protagonistaID FROM protagonista WHERE nombre='{p}' ''')[0][0]
        except IndexError:
            protagID = False

        protags.append({
                'nombre': p,
                'protagID': protagID
            })
    
    actorIDS = []

    for p in protags:
        try:
            idExists = loaf.query(f''' SELECT protagonistaID FROM protagonista WHERE nombre = '{p['nombre']}' ''')[0][0]
            actorIDS.append(idExists)
        except IndexError:
            loaf.query(f''' INSERT INTO protagonista (nombre)
                        VALUES ('{p['nombre']}') ''')
            p['protagID'] = loaf.query(f''' SELECT protagonistaID FROM protagonista WHERE nombre = '{p['nombre']}' ''')[0][0]
            actorIDS.append(p['protagID'])
        
    peliculaID = loaf.query(f''' SELECT peliculaID FROM pelicula WHERE titulo = '{titulo}' AND ano = '{anio}' ''')

    if peliculaID:
        return jsonify({
            'success': 'False',
            'message': 'La pelicula ya esta registrada'
        })

    loaf.query(f''' INSERT INTO pelicula (titulo, duracion, ano)
                    VALUES ('{titulo}', '{dur}', '{anio}') ''')
                
    peliculaID = loaf.query(f''' SELECT peliculaID FROM pelicula WHERE titulo = '{titulo}' AND ano = '{anio}' ''')[0][0]
    
    if not directorID:
        loaf.query(f''' INSERT INTO director (nombre)
                        VALUES ('{director}') ''')

        directorID = loaf.query(f''' SELECT directorID FROM director WHERE nombre = '{director}' ''')

    did = directorID[0][0]

    loaf.query(f''' INSERT INTO dirige (peliculaID, directorID)
                    VALUES ('{peliculaID}', '{did}')''')

    loaf.query(f''' INSERT INTO movie_cat (peliculaID, categoriaID)
                    VALUES ('{peliculaID}', '{categoria}') ''')
    
    for id in actorIDS:
        loaf.query(f''' INSERT INTO actua (peliculaID, protagonistaID)
                        VALUES ('{peliculaID}', '{id}') ''') 
    
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
    protag = request.args.get('protag').split(',')
    # print('*'*15)
    # print(protag)

    if not (pid and titulo and anio and dur and director and categoriaID and protag):
        return jsonify({
            'success': 'False',
            'message': 'Faltan campos'
        })
    try:
        dur = dur.split(':')
        dur = int(dur[0]) * 60 + int(dur[1])
    except ValueError:
        return jsonify({
            'success': 'False',
            'message': 'Duracion Invalida'
        })
    
    directorID = loaf.query(f''' SELECT directorID FROM director WHERE nombre='{director}' ''')[0][0]
    
    # print('*'*15)
    # print(protag)

    protagonistaID = []

    #return jsonify(actores)

    for p in range(len(protag)):
        existe = loaf.query(f''' SELECT protagonistaID FROM protagonista WHERE nombre='{protag[p]}' ''')

        if not bool(existe):
            print('*'*15)
            print('No Existe')
            loaf.query(f''' INSERT INTO protagonista(nombre)
                            Values('{protag[p]}')''')
        
        id = loaf.query(f''' SELECT DISTINCT protagonistaID FROM protagonista WHERE nombre='{protag[p]}' ''')[0][0]
        #return jsonify(id)
        protagonistaID.append(id)
    
    print('*'*15)
    print(protagonistaID)

    loaf.query (f''' DELETE FROM actua WHERE peliculaID = {pid}''')
    
    print('*'*15)
    print('actores',protagonistaID)

    for p in protagonistaID:
        loaf.query(f''' INSERT INTO actua (peliculaID, protagonistaID)
                            VALUES ('{pid}', '{p}') ''')

    if not bool(directorID):
        loaf.query(f''' INSERT INTO director(nombre)
                        Values('{director}')''')
        
        directorID = loaf.query(f''' SELECT directorID FROM director WHERE nombre='{director}' ''')[0][0]

    print('*'*15)
    print(protagonistaID)

    loaf.query(f''' UPDATE pelicula
                    SET titulo='{titulo}', ano='{anio}', duracion='{dur}' 
                    WHERE peliculaID = {pid} ''')

    loaf.query(f''' UPDATE dirige
                    SET directorID = '{directorID}'
                    WHERE peliculaID = {pid} ''')

    loaf.query(f''' UPDATE movie_cat
                    SET categoriaID = '{categoriaID}'
                    WHERE peliculaID = {pid} ''')
    
    return jsonify({
        'success': 'True',
        'message': 'Datos actualizados exitosamente'
    })

@app.route('/buscar')
def buscar():
    busc = str(request.args.get('param'))

    # checar si busc = titulo, director o protagonista
    peliculas = loaf.query(''' SELECT MC2.nombre, MC2.titulo, MC2.duracion, MC2.peliculaID, MC2.ano, categoria.descripcion, MC2.categoriaID
                        FROM categoria
                        INNER JOIN (SELECT categoriaID, MC.nombre, MC.titulo, MC.duracion, MC.peliculaID, MC.ano
                            FROM movie_cat INNER JOIN ( SELECT director.nombre, PD.titulo, PD.duracion, PD.peliculaID, PD.ano
                                FROM (SELECT P.titulo, P.duracion, P.peliculaID, P.ano, directorID 
                                    FROM (SELECT titulo, duracion, peliculaID, ano FROM pelicula) AS P
                                    INNER JOIN dirige ON P.peliculaID = dirige.peliculaID) AS PD
                                INNER JOIN director ON PD.directorID = director.directorID ) AS MC
                            ON MC.peliculaID = movie_cat.peliculaID) AS MC2
                        ON categoria.categoriaID = MC2.categoriaID ''')
    
    qActores = loaf.query(''' SELECT PID.protagonistaID, PID.peliculaID, nombre
                            FROM protagonista INNER JOIN 
                                (SELECT protagonistaID, peliculaID FROM actua) as PID
                            ON protagonista.protagonistaID = PID.protagonistaID''')
    
    listaPeliculas = []

    for i in range(len(peliculas)):
        actores = []
        for actor in range(len(qActores)):
            idActor = qActores[actor][1]
            idPeli = peliculas[i][3]

            if idActor == idPeli:
                actores.append({
                    'nombre': qActores[actor][2],
                    'protagID': qActores[actor][0]
                })
        if busc.lower() in peliculas[i][1].lower() or busc.lower() in peliculas[i][0].lower():   
           listaPeliculas.append({
                'peliculaID': peliculas[i][3],
                'titulo': peliculas[i][1],
                'anio': peliculas[i][4],
                'director': peliculas[i][0],
                'categoria': peliculas[i][5],
                'categoriaID': peliculas[i][6],
                'duracion': f'{int(peliculas[i][2])//60}:{int(peliculas[i][2])%60}',
                'protagonista': actores

            })
    
    return jsonify({
        'peliculas': listaPeliculas
    })

# if busc.lower() in tit.lower() or busc.lower() in dirNom.lower():
if __name__ == "__main__":
    app.run(debug=True)