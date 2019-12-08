import json

from flask import Blueprint, Flask, request, g, redirect, url_for, render_template, flash, current_app, session, Response, abort

from wordstree.db import get_db


bp = Blueprint('api', __name__, url_prefix='/api')


def _to_csv(arr):
    csv = ''
    length = len(arr)
    for i in range(length):
        if i > 0:
            csv += ', '
        csv += arr[i]
    return csv


@bp.route('/tree', methods=['GET'])
def query_tree():
    tree_ids = request.args.getlist('id')
    keys = set(request.args.getlist('keys'))
    queries = set(request.args.getlist('q'))
    length = len(tree_ids)

    db = get_db()
    cur = db.cursor()

    if length > 0:
        query = 'SELECT * FROM tree WHERE tree_id in ({});'.format(_to_csv('?'*length))
        cur.execute(query, tree_ids)
    else:
        cur.execute('SELECT * FROM tree;')
    res = cur.fetchall()
    rv = []
    if res is not None and len(res) > 0:
        valid_keys = set(res[0].keys())
        if keys:
            keys = valid_keys.intersection(keys).union({'tree_name', 'tree_id'})
        else:
            keys = valid_keys

        for row in res:
            dic = dict()
            for key in keys:
                dic[key] = row[key]
            rv.append(dic)

    # handle queries
    for tree_dic in rv:
        if 'max_zoom' in queries:
            cur.execute('SELECT tree.tree_id, COUNT(zoom_id) FROM tree JOIN zoom_info zi on tree.tree_id = zi.tree_id '
                        'WHERE tree.tree_id=?', [tree_dic['tree_id']])
            tree_dic['max_zoom'] = cur.fetchone()[1]

    response = Response(
        response=json.dumps(rv),
        mimetype='application/json',
        content_type='application/json;charset=utf-8'
    )

    return response


@bp.route('/zoom', methods=['GET'])
def query_zoom():
    """
    Query for zoom information. Returns list of entries in `zoom_info` table that match any of the conditions
    specified in the query. The following conditions are known:
      1. `id` - refers to `zoom_id` of the entry
      2. `tree-id` - refers to `tree_id` column of the entry
      3. `q` - comma separated values of of the from `<zoom level>,<tree_id>|...`; refers to entries with
        matching zoom level and tree id
      4. keys - columns to include in the other than the zoom_id; by default all column values are returned
    """
    ids = request.args.getlist('id')
    tree_ids = request.args.getlist('tree-id')
    queries = request.args.getlist('q')
    keys = set(request.args.getlist('keys'))
    parsed_queries = []

    # parse queries
    qlen = len(queries)
    try:
        for i in range(qlen):
            query = queries[i]
            slen = len(query)
            j = 0
            while j < slen:
                comma = query.find(',', j)
                pipe = query.find('|', j)
                print(query, comma, pipe)
                if comma < 0:
                    raise ValueError('\'{}\' malformed query'.format(query))
                zoom_level = int(query[j:comma])

                if pipe < 0:
                    tree_id = int(query[comma+1:])
                    pipe = slen
                else:
                    tree_id = int(query[comma+1:pipe])
                parsed_queries.append((zoom_level, tree_id))
                j = pipe + 1
    except ValueError as e:
        return Response('Malformed query', status=500)

    rv = []
    cur = get_db().cursor()

    # construct condition for WHERE clause
    clause, args = '', []
    if len(ids) > 0:
        clause += 'zoom_id IN ({})'.format(_to_csv('?'*len(ids)))
        args.extend(ids)

    if len(tree_ids) > 0:
        if clause:
            clause += ' OR '
        clause += 'tree_id IN ({})'.format(_to_csv('?'*len(tree_ids)))
        args.extend(tree_ids)

    if len(parsed_queries) > 0:
        if clause:
            clause += ' OR '
        length = len(parsed_queries)
        for i in range(length):
            if i > 0:
                clause += ' OR '
            zoom_level, tree_id = parsed_queries[i]
            clause += '(zoom_level=? AND tree_id =?)'
            args.extend([zoom_level, tree_id])

    # construct rest of SQL statement
    if clause:
        statement = 'SELECT * FROM zoom_info WHERE ' + clause + ';'
    else:
        statement = 'SELECT * FROM zoom_info;'

    cur.execute(statement, args)
    res = cur.fetchall()

    rv = []
    if res is not None and len(res) > 0:
        valid_keys = set(res[0].keys())
        if keys:
            keys = valid_keys.intersection(keys).union({'zoom_id'})
        else:
            keys = valid_keys

        for row in res:
            dic = dict()
            for key in keys:
                dic[key] = row[key]
            rv.append(dic)

    response = Response(
        response=json.dumps(rv),
        mimetype='application/json',
        content_type='application/json;charset=utf-8'
    )

    return response


@bp.route('/tile', methods=['GET'])
def query_tile():
    zoom_level = request.args.get('zoom', default=0)
    row = request.args.get('row', default=0)
    col = request.args.get('col', default=0)
    res_type = request.args.get('type', default='img')
    tree_id = request.args.get('tree-id')
    zoom_id = request.args.get('zoom-id')

    if not tree_id and not zoom_id:
        return Response('zoom-id or tree-id and zoom must be provided', status=500)
    if res_type not in ['img', 'json']:
        return Response('\'{}\' type unknown'.format(res_type), status=500)

    try:
        row = int(row)
        col = int(col)

        cur = get_db().cursor()
        if zoom_id:
            cur.execute('SELECT * FROM tiles WHERE zoom_id=? AND tile_row=? AND tile_col=?', [zoom_id, row, col])
        else:
            cur.execute(
                'SELECT * FROM tiles INNER JOIN zoom_info zi ON tiles.zoom_id = zi.zoom_id WHERE '
                'zoom_level=? AND tree_id=? AND tile_row=? AND tile_col=?', [zoom_level, tree_id, row, col]
            )
        row = cur.fetchone()
        if row is None:
            return Response('tile not found', status=404)

        if res_type == 'img':
            with open(row['img_file'], mode='rb') as f:
                response = Response(
                    response=f.read(),
                    mimetype='image/png',
                    content_type='image/png'
                )
        else:
            with open(row['json_file'], mode='r') as f:
                response = Response(
                    response=f.read(),
                    mimetype='application/json',
                    content_type='application/json'
                )

        return response
    except FileNotFoundError:
        return Response('tile data not found', status=404)
    except ValueError as e:
        return Response(str(e), status=500)




