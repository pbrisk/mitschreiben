# A tableclass from mst


class Table(object):
    """
        A table consist of columns and rows. Each entry has a row and a column key.
    """

    def __init__(self, default_value=None, name=None, left_upper=None):
        self.row_keys = []
        self.col_keys = []
        self._values = {}
        self._default_value = default_value
        self.name = name
        self.left_upper = left_upper

    @property
    def rows_count(self):
        return len(self.row_keys)

    @property
    def cols_count(self):
        return len(self.col_keys)

    def is_empty(self):
        return len(self.row_keys) == 0 or len(self.col_keys) == 0

    def transpose(self):
        ret = Table(name=self.name, left_upper=self.left_upper, default_value=self._default_value)
        for row_key in self.row_keys:
            for col_key in self.col_keys:
                ret.append(col_key, row_key, self.get(row_key, col_key))
        return ret


    def append(self, row_key, col_key, value):
        col_dict = self._values.get(row_key, None)
        if col_dict is None:
            self._values[row_key] = {col_key: value}
            self.row_keys.append(row_key)
        else:
            col_dict[col_key] = value
        if col_key not in self.col_keys:
            self.col_keys.append(col_key)

    def append_row(self, row_key, row):
        for col_key, value in row.items():
            self.append(row_key, col_key, value)

    def get(self, row_key, col_key):
        row_dict = self._values.get(row_key, None)
        if row_dict is None:
            return self._default_value
        ret = row_dict.get(col_key, self._default_value)
        return ret

    def __call__(self, row_key, col_key):
        return self.get(row_key, col_key)

    def get_row(self, row_key):
        ret = {}
        for col_key in self.col_keys:
            ret[col_key] = self.get(row_key, col_key)
        return ret

    def get_row_list(self, row_key, col_keys):
        """
        returns the values of the row:row_key for all col_keys.
        """
        return [self(row_key, col_key) for col_key in col_keys]

    def get_column(self, col_key):
        ret = {}
        for row_key in self.row_keys:
            ret[row_key] = self.get(row_key, col_key)
        return ret

    def get_default(self):
        return self._default_value

    def sort(self, row_compare=None, column_compare=None):
        ret = Table(name=self.name, left_upper=self.left_upper, default_value=self._default_value)
        sortrow_keys = sorted(self.row_keys, key=row_compare)
        sortcol_keys = sorted(self.col_keys, key=column_compare)
        for row_key in sortrow_keys:
            for col_key in sortcol_keys:
                ret.append(row_key, col_key, self.get(row_key, col_key))
        return ret

    def to_csv(self, leftUpper=None, tabName=None, separator=';'):
        repr = list()
        col_keys = sorted(self.col_keys)
        repr.append(""+separator+separator.join(col_keys))
        for key in self.row_keys:
            elements = [key]+self.get_row_list(key, col_keys)
            elements = map(str, elements)
            repr.append(separator.join(elements))
        return "\n".join(repr)

    def pretty_string(self, leftUpper=None, tabName=None, separator=" | "):
        representation = []
        name = tabName if tabName is not None else self.name
        if name is not None:
            representation.append(name)

        if len(self.row_keys) == 0 or len(self.col_keys) == 0:
            return '\n'.join(representation + ['Empty Table'])
        tab = self
        line = leftUpper if leftUpper is not None else (self.left_upper if self.left_upper is not None else '')
        max_row_key_width = max(map(len, map(str,tab.row_keys) + [line]))
        line = "{text:>{len}}".format(text=line, len=max_row_key_width)
        max_colkey_width = dict()
        for col_key in tab.col_keys:
            max_colkey_width[col_key] = max(map(lambda x:len(str(x)), tab.get_column(col_key).values() + [col_key]))
        for col_key in tab.col_keys:
            line += "{sep}{col:>{width}}".format(sep=separator, col=col_key, width=max_colkey_width[col_key])
        representation.append(line)
        for row_key in tab.row_keys:
            line = "{ROW:>{len}}".format(ROW=row_key, len=max_row_key_width)
            for col_key in tab.col_keys:
                element = str(tab.get(row_key, col_key))
                line += "{sep}{ELEMENT:>{width}}".format(ELEMENT=element, sep = separator, width = max_colkey_width[col_key])
            representation.append(line)
        return '\n'.join(representation)

    def to_html(self):
        rows = self.to_nested_list()
        s = "<table>\n"
        s += "<tr class='headrow'>\n"
        s += "<th colspan='{number}'>{tabname}</th>\n".format(number=len(rows[0]), tabname = self.name)
        s += "</tr>\n"
        header = rows[0]
        s += "<tr class='bodyrow'>\n"
        for cell in header:
            s += "<th>{}</th>\n".format(cell)
        s += "</tr>\n"

        for row in rows[1:]:
            s += "<tr class='bodyrow'>\n"
            s += "<th>{}</th>\n".format(row[0])
            for cell in row[1:]:
                s += "<td>{}</td>\n".format(cell)
            s +="</tr>"

        s+="</table>"
        return s

    def to_nested_list(self):
        """returns the table as a nested list rows"""
        header = [k for k in self.col_keys]
        header.insert(0, " ")
        rows = [header]
        for row_key in self.row_keys:
            row = self.get_row_list(row_key, self.col_keys)
            row.insert(0, row_key)
            rows.append(row)
        return rows

    @staticmethod
    def create_from_json_dict(json_dict):
        ret = Table(name=json_dict['TableName'], left_upper=json_dict['LeftUpper'])
        table_rows = json_dict['Table']
        header = table_rows[0][1:]
        first_col = [row[0] for row in table_rows][1:]
        for r in xrange(len(first_col)):
            row = table_rows[r + 1]
            for c in xrange(len(header)):
                ret.append(first_col[r], header[c], row[c + 1])
        return ret

