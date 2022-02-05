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
    db='peliculas_integrador'
)

# Obtener todas las peliculas
@app.route('/dashboard')
def dashboard():
    peliculas = list(loaf.query('''  SELECT director.nombre, PD.titulo, PD.duracion, PD.peliculaID
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
                'duracion': str(datetime.timedelta(seconds=peliculas[i][2]))
            }
        })

    return jsonify({
        'peliculas': listaPeliculas
    })

# Obtener todas las peliculas de la misma categoria
@app.route('/dashboard_filtrado')
def dashboard_filtrado():
    categoria = request.args.get('categoria')

    if not categoria:
        return jsonify({
            'success': 'False',
            'message': 'Selecciona la categoria'
        })

    categoriaID = loaf.query(f''' SELECT categoriaid  
                                FROM categoria
                                WHERE descripcion = '{categoria}' ''')[0][0]
    
    peliculas = loaf.query(f''' SELECT director.nombre, PD.titulo, PD.duracion, PD.peliculaID
                                FROM (SELECT P.titulo, P.duracion, P.peliculaID, directorID
                                    FROM (SELECT pelicula.titulo, CP.peliculaID, pelicula.duracion
                                        FROM pelicula INNER JOIN (SELECT peliculaID FROM pelicula_categoria 
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
                'duracion': str(datetime.timedelta(seconds=peliculas[i][2]))
            }
        })

    return jsonify({
        'peliculas': listaPeliculas
    })


@app.route('/registrar_pelicula')
def registrar_pelicula():
    titulo = request.args.get('titulo')
    dur = request.args.get('dur')
    director = request.args.get('director')
    categoria = request.args.get('categoria')
    protag = request.args.get('protag').split('_')

    if not (titulo and dur and director and categoria and protag):
        return jsonify({
            'success': 'False',
            'message': 'Faltan campos'
        })
    
    checkRegistro = loaf.query(f''' ''')

    if checkRegistro:
        return jsonify({
            'success': 'False',
            'message': 'La pelicula ya esta registrada'
        })
    
    # Checar si director y protagonista ya existen si no agregarlos

@app.route('/del_pelicula')
def del_pelicula():
    pid = request.args.get('pid')

    return jsonify(pid)

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

    for i in range(len(q)):
        listaPeliculas.append({
            'Pelicula': {
                'peliculaID': q[i][0],
                'titulo': q[i][1],
                'director': q[i][2],
                'duracion': str(datetime.timedelta(seconds=q[i][3])),
                'protagonista': q[i][4]
            }
        })
    
    resultados = []
    idPelis = []
    
    for i in range(len(listaPeliculas)):
        pass

    return jsonify({'peliculas': listaPeliculas})


if __name__ == "__main__":
    app.run(debug=True)