mitschreiben
============

.. image:: https://img.shields.io/codeship/f797f980-5b19-0135-2a70-66335668a83b/master.svg
    :target: https://codeship.com//projects/237404

.. image:: https://readthedocs.org/projects/mitschreiben/badge
    :target: http://mitschreiben.readthedocs.io



mitschreiben (german for 'to take notes') helps recording values during
calculations for later evaluation, e.g. check if the right objects or
values were used or to present the results in structure of tables

It provides a class called Record which is basically used for everything. It grants access to record object, it is used
for the recording and it is a context manager used to trigger whether to record or not.

Example Usage
-------------

In the first ``Record(key = value)`` or ``Record(dictionary)`` is placed where one wants to
record a value. The decorator ``Prefix`` provided by this class is used
to define a key extension under which the recorded value will be stored in the
``Record``. The Prefixes get stacked, so when there is a successive
function call to another function which is prefixed those Prefixes are
concatenated.

.. code:: python

    from mitschreiben import Record

    def magical_stuff_happens(baz, barz):
        return "That's", "great"

    class Foo():

        @Record.Prefix()
        def bar(self, baz, barz)
            some_value1, some_value2 = self.do_something(baz, barz)

            Record(a_key=some_value1, another_key=some_value2)

            return some_value1, some_value2

        @Record.Prefix()
        def do_something(self, baz, barz):

            a_dict = {'again_a_key': baz, 'so_creative': barz}

            Record(a_dict)

            return magical_stuff_happens(baz, barz)

        def __repr__(self):
            return "Foo({})".format(id(self))


Now, since ``Record`` is a contextmanager, the recording will only
happen in such a context. The ``with``-statement activates the recording and returns the current scopes record object
for convenient access. Another thing is, that record level is increased by this statement, leading to record objects
that are only available in that scope. When leaving the ``with`` the outer scopes's record will be extend by the inner
one, by prepending the outer records current prefix stack to each key of the inner one.


.. code:: python

    with Record() as rec:
        foo = Foo()
        foo.do_something("baz", "barz")
        foo.bar("baz","barz")

        print rec.entries

::

The entries are a dict whose keys are tuples which are the stacked Prefixes. In this way it is possible to determine which method on which object was called, what then led
to successive calls, where in the end a value is recorded. The example above has the following output.

.. code:: python

    {('Foo(42403656).do_something', 'again_a_key'): 'baz', ('Foo(42403656).bar', 'Foo(42403656).do_something', 'again_a_key'): 'baz', ('Foo(42403656).do_something', 'so_creative'): 'barz', ('Foo(42403656).bar', 'a_key'): "That's", ('Foo(42403656).bar', 'another_key'): 'great', ('Foo(42403656).bar', 'Foo(42403656).do_something', 'so_creative'): 'barz'}

::

Formatting the output
---------------------

The Record can be represented in different formats. The base to this is a *tree of dictionaries*,
implemented by the class ``DictTree`` in ``mitschreiben.formatting``. For the two base outputs however, one
does not need to actually instantiate a ``DictTree`` yourself. The respective methods are

.. code::python

    Record().to_csv_files(PATH)
    Record().to_html_tables(FILENAME, PATH)


Both of these methods produce tables of the output. The idea is that, that certain calculations are made with different
objects, leading to the same keywords. So one obtains a table with row keys (object names) and column keys (the keywords
used to record a value). As the name of the former methods suggests, it produces this tables and writes them as single
.csv files into ``Path``, whereas the latter construct a html document in which one can navigate through the tree structure
and see the tables at those positions where they would be placed in the tree. Those tables would look similar to

.. raw:: html

    <div class='panel-elem'><table>
    <tr class='headrow'>
    <th colspan='5'>table</th>
    </tr>
    <tr class='bodyrow'>
    <th> </th>
    <th>a_key</th>
    <th>again_a_key</th>
    <th>another_key</th>
    <th>so_creative</th>
    </tr>
    <tr class='bodyrow'>
    <th>Foo(42403656).bar</th>
    <td>That's</td>
    <td>None</td>
    <td>great</td>
    <td>None</td>
    </tr><tr class='bodyrow'>
    <th>Foo(42403656).do_something</th>
    <td>None</td>
    <td>baz</td>
    <td>None</td>
    <td>barz</td>
    </tr></table></div>
    <div class='panel'>
    <div class='panel-elem'><table>
    <tr class='headrow'>
    <th colspan='2'>table</th>
    </tr>
    <tr class='bodyrow'>
    <th> </th>
    <th>Foo(42403656).do_something</th>
    </tr>
    <tr class='bodyrow'>
    <th>again_a_key</th>
    <td>baz</td>
    </tr><tr class='bodyrow'>
    <th>so_creative</th>
    <td>barz</td>
    </tr></table></div>

Another way would be to work with the ``DictTree`` directly.

.. code:: python

    from mitschreiben.formatting import DictTree

    DT = DictTree(rec.entries)

    tables = DT.make_tables()
    for t in tables:
        print t.pretty_string()
        print

This results in the following output. The first table represents the top
level of the record, whereas the other tabels are named by
*object.function*.

.. code::

                        Values |  a_key | again_a_key | another_key | so_creative
             Foo(42403656).bar | That's |        None |       great |        None
    Foo(42403656).do_something |   None |         baz |        None |        barz

    Foo(42403656).bar
                        Values | again_a_key | so_creative
    Foo(42403656).do_something |         baz |        barz


