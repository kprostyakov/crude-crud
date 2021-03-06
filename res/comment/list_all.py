from sqlite3 import Error as dbError
from response import Response, fill_template
from db.init import comment_schema

class ListComments(Response):
    def __init__(self):
        super().__init__()

    def model(self, conn, params):
        def parse_row(row, keys):
            obj_list = [(keys[i], row[i]) for i in range(len(keys))]
            return dict(obj_list)

        cursor = conn.cursor()
        query = '''SELECT comment_id, comments.name as name, last_name, middle_name, phone, email,
        cities.name as city, regions.name as region, comment
        FROM comments
        INNER JOIN regions ON regions.code = comments.region_code
        INNER JOIN cities ON cities.city_id = comments.city_id'''
        try:   
            cursor.execute(query)
        except dbError as err:
            self.props['error'] = err
            self.props['comments'] = []
        else:
            keys = comment_schema()
            self.props['comments'] = [parse_row(row, keys) for row in cursor]
            if len(self.props['comments'])==0:
                self.props['error'] = 'Данные не найдены'
        return self

    def render(self, assets):
        asset_type = 'HTML'
        rows = [fill_template(assets['row'], row) for row in self.props['comments']]
        rows_text = ''.join(rows)
        content = fill_template(assets['body'], {
            'rows': rows_text,
            'header': assets['header'],
            'script': assets['script'],
            'error': self.props['error']
            }).encode()
        status = self.status['OK']
        return status, self.headers(asset_type,content), content
