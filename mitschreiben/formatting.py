from table import Table
import os
import datetime


class DictTree(dict):
    """
    A class to work with a dict whose keys are tuples as if this dict was a dictionary of dictionaries of dictionaries...
    When trying to look up a value with key (=tuple) and this tuple is partially contained in other keys (=tuples) than
    a DictTree with only those truncated keys is returned.
    """

    def __getitem__(self, tpl):
        if not isinstance(tpl, tuple):
            tpl = (tpl,)
        if tpl in self.keys():
            return super(DictTree, self).__getitem__(tpl)
        else:
            kvals = [(key[len(tpl):], value) for key, value in self.items() if len(key) >= len(tpl) and key[0:len(tpl)] == tpl]
            if kvals:
                return DictTree(kvals)
            else:
                raise KeyError

    def toplevel_tables(self, name):
        """Return tables from the two uppermost layers of the DictTree. One of them is a true table and the
        other is a collection of values"""

        len1_keys = [key for key in self.keys() if len(key)==1]
        len2_keys = [key for key in self.keys() if len(key)==2]

        pt = Table(name= name,)
        for k in len1_keys:
            pt.append('', k[0], self[k])

        vt = Table(name=name)
        for k in len2_keys:
            vt.append(k[0], k[1], self[k])

        return pt.sort(), vt.sort()

    def to_tables(self):
        """Makes a table from each level within the DictTree"""
        max_level = max(map(len, self.keys()))
        tables = list()
        for i in range(0, max_level):
            for key in sorted(list(set([k[0:i] for k in self.keys()]))):
                T = self[key]
                if isinstance(T, DictTree):
                    a, b = T.toplevel_tables("Table: " + "|".join(map(str, key)))
                    if not a.is_empty() and i == 0:
                        a.name = "Properties"
                        tables.append(a)
                    if not b.is_empty():
                        tables.append(b)
        return tables

    def pretty_print(self):
        "this function prints an alphabetically sorted tree in a directory-like structure."

        def compare_keys(tpl_prev, tpl_next):

            equal_list = [x==y for x,y in zip(tpl_prev, tpl_next)]
            j = equal_list.index(False)
            return j, tpl_next[j:]

        keys = sorted(self.keys())
        previous_key = None
        indent = 0
        indentfactor = 1

        for key in keys:
            rest_key = key
            if previous_key:
                indent, rest_key = compare_keys(previous_key, key)

            for i, value in enumerate(rest_key):
                print ("|"+" "*indentfactor)*(indent+i)+value \
                      + ((":" +" " * indentfactor + str(self[key]))if i == len(rest_key) - 1 else "")
            previous_key = key

    def as_tree_to_html(self, filename, path=None):
        """This function creates a html file that presents the dicttree in its tree structure."""

        if path and not os.path.isdir(path):
            os.makedirs(path)

        if path:
            target_file_path = os.path.join(path, filename)
        else:
            target_file_path = filename

        def make_button(caption):
            return "<button class='accordion'>{}</button>".format(caption)

        def compare_keys(tpl_prev, tpl_next):
            equal_list = [x==y for x,y in zip(tpl_prev, tpl_next)]
            j = equal_list.index(False)
            return j, tpl_next[j:]

        keys = sorted(self.keys())
        previous_key = None

        with open("htmldicttree.temp", "w") as tempfile:

            for key in keys:
                rest_key = key
                if previous_key:
                    indent, rest_key = compare_keys(previous_key, key)
                    previous_indent = len(previous_key)-1
                    if indent < previous_indent:
                        tempfile.write("\n</div>" * abs(previous_indent - indent))
                for i, value in enumerate(rest_key):
                    if i == len(rest_key)-1:
                        tempfile.write("\n<div class='panel-elem'>" + value +" : " + str(self[key]) + "</div>")
                    else:
                        tempfile.write("\n"+make_button(value))
                        tempfile.write("\n<div class='panel'>")
                previous_key = key

        template = open('html_basics/accordion.html')
        s1,s2 = template.read().split("#SPLIT#")
        with open('htmldicttree.temp') as temp:
            with open(target_file_path, 'w') as target_file:
                target_file.write(s1)
                for line in temp.readlines():
                    target_file.write(line)
                target_file.write(s2)

        os.remove('htmldicttree.temp')

    def as_tables_to_html(self, filename, path=None):
        """This functions creates a html file presenting the tree in tables"""

        if path and not os.path.isdir(path):
            os.makedirs(path)

        if path:
            target_file_path = os.path.join(path, filename)
        else:
            target_file_path = filename

        tbs = self.to_tables()
        abs_path = os.path.join(os.path.split(__file__)[0],'html_basics','tables.html')

        f = open(abs_path)
        s1, s2 = f.read().split("#SPLIT#")
        f.close()

        with open(target_file_path, "w") as f:

            f.write(s1)

            for tb in sorted(tbs, key=lambda x: x.name):
                f.write("<table>\n")
                f.write("<tr><td>{}</td></tr>\n".format(tb.to_html()))
                f.write("</table>\n")
            f.write(s2)

    def to_csv_files(self, path):
        "this function creates csv files for every table that can be made from the tree"

        def make_filename(tabname):
            timestamp = datetime.datetime.now().strftime("%Y%m%d")
            if len(tabname)>200:
                tabname = tabname[:100]+"___"+reversed(reversed(tabname)[:100])

            return timestamp + "_" +tabname + ".csv"

        if path and not os.path.isdir(path):
            os.makedirs(path)

        for tb in self.to_tables():
            filename = make_filename(tb.name)
            if path:
                target_file_path = os.path.join(path, filename)
            else:
                target_file_path = filename

            with open(target_file_path, "w") as f:
                f.write(tb.to_csv())