import inspect
import datetime
import sqlite3

import MySQLdb
import MySQLdb.cursors
from _mysql_exceptions import OperationalError
from coyote_framework.config.database_config import DatabaseConfig
from dateutil import parser
from coyote_framework.mixins.stringconversion import get_delimited_string_from_list
from ConfigParser import NoOptionError


class NoRecordsFoundException(ValueError):
    """Exception raised when no records found when expecting at least one"""


class NOTSET(object):
    """Used to flag db columns as not being set when used as the default, so you can still pass in values of None

        e.g.

        >>> def query(entity_id=NOTSET):

        as a signature will allow you to pass None-values

        >>> query(entity_id=None)

    """


class CoyoteDb(object):

    @staticmethod
    def __get_db_cursor(target_database=None):
        db = CoyoteDb.__get_db_write_instance(target_database=target_database)
        return db.cursor()

    @staticmethod
    def __get_db_write_instance(target_database=None):
        db_config = DatabaseConfig(target_database=target_database)
        db_type = db_config.get('database_type')
        if db_type == 'mysql':
            db_host = db_config.get('mysql_host')
            db_port = int(db_config.get('mysql_port'))
            db_user = db_config.get('mysql_user')
            db_pass = db_config.get('mysql_pass')
            db_name = db_config.get('mysql_dbname')
            db = MySQLdb.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                passwd=db_pass,
                db=db_name,
                cursorclass=MySQLdb.cursors.DictCursor
            )
            return db
        elif db_type == 'sqlite':
            db_filename = db_config.get('sqlite_file_location')
            db = sqlite3.connect(db_filename)

            def dict_factory(cursor, row):
                d = {}
                for idx, col in enumerate(cursor.description):
                    d[col[0]] = row[idx]
                return d
            db.row_factory = dict_factory

            return db
        else:
            raise NoOptionError('database_type', 'database')

    @staticmethod
    def __add_query_comment(sql):
        """
        Adds a comment line to the query to be executed containing the line number of the calling
        function.  This is useful for debugging slow queries, as the comment will show in the slow
        query log

        @type sql: str
        @param sql: sql needing comment
        @return:
        """
        # Inspect the call stack for the originating call
        file_name = ''
        line_number = ''
        caller_frames = inspect.getouterframes(inspect.currentframe())
        for frame in caller_frames:
            if "ShapewaysDb" not in frame[1]:
                file_name = frame[1]
                line_number = str(frame[2])
                break

        comment = "/*COYOTE: Q_SRC: {file}:{line} */\n".format(file=file_name, line=line_number)
        return comment + sql,


    @staticmethod
    def get_single_record(*args, **kwargs):
        db, cursor = CoyoteDb.execute(*args, **kwargs)
        return cursor.fetchone()

    @staticmethod
    def get_all_records(*args, **kwargs):
        db, cursor = CoyoteDb.execute(*args, **kwargs)
        return cursor.fetchall()

    @staticmethod
    def get_single_instance(sql, class_type, *args, **kwargs):
        """Returns an instance of class_type populated with attributes from the DB record; throws an error if no
        records are found

        @param sql: Sql statement to execute
        @param class_type: The type of class to instantiate and populate with DB record
        @return: Return an instance with attributes set to values from DB
        """
        record = CoyoteDb.get_single_record(sql, *args, **kwargs)
        try:
            instance = CoyoteDb.get_object_from_dictionary_representation(dictionary=record, class_type=class_type)
        except AttributeError:
            raise NoRecordsFoundException('No records found for {class_type} with sql run on {host}: \n {sql}'.format(
                sql=sql,
                host=DatabaseConfig().get('mysql_host'),
                class_type=class_type
            ))
        return instance

    @staticmethod
    def get_all_instances(sql, class_type, *args, **kwargs):
        """Returns a list of instances of class_type populated with attributes from the DB record

        @param sql: Sql statement to execute
        @param class_type: The type of class to instantiate and populate with DB record
        @return: Return a list of instances with attributes set to values from DB
        """
        records = CoyoteDb.get_all_records(sql, *args, **kwargs)
        instances = [CoyoteDb.get_object_from_dictionary_representation(
            dictionary=record, class_type=class_type) for record in records]
        for instance in instances:
            instance._query = sql
        return instances

    @staticmethod
    def escape_dictionary(dictionary, datetime_format='%Y-%m-%d %H:%M:%S'):
        """Escape dictionary values with keys as column names and values column values

        @type dictionary: dict
        @param dictionary: Key-values
        """
        for k, v in dictionary.iteritems():
            if isinstance(v, datetime.datetime):
                v = v.strftime(datetime_format)

            if isinstance(v, basestring):
                v = CoyoteDb.db_escape(str(v))
                v = '"{}"'.format(v)

            if v is True:
                v = 1

            if v is False:
                v = 0

            if v is None:
                v = 'NULL'

            dictionary[k] = v

    @staticmethod
    def get_insert_fields_and_values_from_dict(dictionary, datetime_format='%Y-%m-%d %H:%M:%S', db_escape=True):
        """Formats a dictionary to strings of fields and values for insert statements

        @param dictionary: The dictionary whose keys and values are to be inserted
        @param db_escape: If true, will db escape values
        @return: Tuple of strings containing string fields and values, e.g. ('user_id, username', '5, "pandaman"')
        """
        if db_escape:
            CoyoteDb.escape_dictionary(dictionary, datetime_format=datetime_format)

        fields = get_delimited_string_from_list(dictionary.keys(), delimiter=',')  # keys have no quotes
        vals = get_delimited_string_from_list(dictionary.values(), delimiter=',')  # strings get quotes

        return fields, vals

    @staticmethod
    def get_kwargs(**kwargs):
        """This method should be used in query functions where user can query on any number of fields

            >>> def get_instances(entity_id=NOTSET, my_field=NOTSET):
            >>>     kwargs = CoyoteDb.get_kwargs(entity_id=entity_id, my_field=my_field)
        """
        d = dict()
        for k, v in kwargs.iteritems():
            if v is not NOTSET:
                d[k] = v
        return d

    @staticmethod
    def get_update_clause_from_dict(dictionary, datetime_format='%Y-%m-%d %H:%M:%S'):
        """Builds the update values clause of an update statement based on the dictionary representation of an
        instance"""
        items = []

        CoyoteDb.escape_dictionary(dictionary, datetime_format=datetime_format)
        for k,v in dictionary.iteritems():
            item = '{k} = {v}'.format(k=k, v=v)
            items.append(item)
        clause = ', '.join(item for item in items)
        return clause

    @staticmethod
    def get_where_clause_from_dict(dictionary, join_operator='AND'):
        """Builds a where clause from a dictionary
        """
        CoyoteDb.escape_dictionary(dictionary)
        clause = join_operator.join(
            (' {k} is {v} ' if str(v).lower() == 'null' else ' {k} = {v} ').format(k=k, v=v)  # IS should be the operator for null values
            for k, v in dictionary.iteritems())
        return clause

    @staticmethod
    def get_dictionary_representation_of_object_attributes(obj, omit_null_fields=False):
        """Returns a dictionary of object's attributes, ignoring methods

        @param obj: The object to represent as dict
        @param omit_null_fields: If true, will not include fields in the dictionary that are null
        @return: Dictionary of the object's attributes
        """
        obj_dictionary = obj.__dict__

        obj_dictionary_temp = obj_dictionary.copy()
        for k, v in obj_dictionary.iteritems():
            if omit_null_fields:
                if v is None:
                    obj_dictionary_temp.pop(k, None)
            if k.startswith('_'):
                obj_dictionary_temp.pop(k, None)

        return obj_dictionary_temp

    @staticmethod
    def get_object_from_dictionary_representation(dictionary, class_type):
        """Instantiates a new class (that takes no init params) and populates its attributes with a dictionary

        @type dictionary: dict
        @param dictionary: Dictionary representation of the object
        @param class_type: type
        @return: None
        """
        assert inspect.isclass(class_type), 'Cannot instantiate an object that is not a class'

        instance = class_type()

        CoyoteDb.update_object_from_dictionary_representation(dictionary, instance)

        return instance

    @staticmethod
    def build_where_clause(mappings, operator='AND'):
        """Constructs the where clause based on a dictionary of values

        >>> build_where_clause({'id': 456, 'name': 'myrecord'}, operator='OR')
        >>> 'WHERE id = 456 OR name = "myrecord" '

        """
        where_clause_mappings = {}
        where_clause_mappings.update(mappings)

        where_clause = 'WHERE ' + ' {} '.format(operator).join(
            '{k} = {v}'.format(k=k, v='"{}"'.format(v) if isinstance(v, basestring) else v)
            for k, v in where_clause_mappings.iteritems()
        )
        return where_clause

    @staticmethod
    def execute(*args, **kwargs):
        """Executes the sql statement, but does not commit. Returns the cursor to commit

        @return: DB and cursor instance following sql execution
        """

        # Inspect the call stack for the originating call
        args = CoyoteDb.__add_query_comment(args[0])
        db = CoyoteDb.__get_db_write_instance(target_database=kwargs.pop('target_database', None))
        filtered_kwargs = {k: v for k, v in kwargs.iteritems() if k != 'target_database'}

        # Execute the query
        cursor = db.cursor()
        try:
            cursor.execute(*args, **filtered_kwargs)
        except OperationalError, e:
            raise OperationalError('{} when executing: {}'.format(e.args, args[0]))
        return db, cursor

    @staticmethod
    def execute_read_only(*args, **kwargs):
        # TODO: consolidate with execute
        """Executes the sql statement, but does not commit. Returns the cursor to commit

        @return: DB and cursor instance following sql execution
        """

        # Inspect the call stack for the originating call
        args = CoyoteDb.__add_query_comment(args[0])

        # Execute the query
        db = CoyoteDb.__get_db_read_instance()
        cursor = db.cursor()
        try:
            cursor.execute(*args, **kwargs)
        except OperationalError, e:
            raise OperationalError('{} when executing: {}'.format(e.args, args[0]))
        return db, cursor

    @staticmethod
    def execute_and_commit(*args, **kwargs):
        """Executes and commits the sql statement

        @return: None
        """
        db, cursor = CoyoteDb.execute(*args, **kwargs)
        db.commit()
        return cursor

    @staticmethod
    def insert(sql, *args, **kwargs):
        """Inserts and commits with an insert sql statement, returns the record, but with a small chance of a race
        condition

        @param sql: sql to execute
        @return: The last row inserted
        """

        assert "insert into" in sql.lower(), 'This function requires an insert statement, provided: {}'.format(sql)
        cursor = CoyoteDb.execute_and_commit(sql, *args, **kwargs)

        # now get that id
        last_row_id = cursor.lastrowid

        return last_row_id

    @staticmethod
    def insert_instance(instance, table):
        """Inserts an object's values into a given table, will not populate Nonetype values

        @param instance: Instance of an object to insert
        @param table: Table in which to insert instance values
        @return: ID of the last inserted row
        """
        instancedict = instance.__dict__.copy()
        instancedictclone = instancedict.copy()

        # Remove all Nonetype values
        for k, v in instancedictclone.iteritems():
            if v is None:
                instancedict.pop(k)

        keys, values = CoyoteDb.get_insert_fields_and_values_from_dict(instancedict)
        sql = """INSERT INTO {table} ({keys}) VALUES ({values})""".format(
            table=table,
            keys=keys,
            values=values
        )

        insert = CoyoteDb.insert(sql=sql)
        return insert

    @staticmethod
    def update(sql, *args, **kwargs):
        """Updates and commits with an insert sql statement, returns the record, but with a small chance of a race
        condition

        @param sql: sql to execute
        @return: The last row inserted
        """
        assert "update" in sql.lower(), 'This function requires an update statement, provided: {}'.format(sql)
        cursor = CoyoteDb.execute_and_commit(sql, *args, **kwargs)

        # now get that id
        last_row_id = cursor.lastrowid

        return last_row_id

    @staticmethod
    def delete(sql, *args, **kwargs):
        """Deletes and commits with an insert sql statement"""
        assert "delete" in sql.lower(), 'This function requires a delete statement, provided: {}'.format(sql)
        CoyoteDb.execute_and_commit(sql, *args, **kwargs)

    @staticmethod
    def update_object_from_dictionary_representation(dictionary, instance):
        """Given a dictionary and an object instance, will set all object attributes equal to the dictionary's keys and
        values. Assumes dictionary does not have any keys for which object does not have attributes

        @type dictionary: dict
        @param dictionary: Dictionary representation of the object
        @param instance: Object instance to populate
        @return: None
        """
        for key, value in dictionary.iteritems():
            if hasattr(instance, key):
                setattr(instance, key, value)

        return instance

    @staticmethod
    def format_time(time):
        """Formats a time to be Shapeways database-compatible

        @param time: Datetime or string object to format
        @rtype: str
        @return: Time formatted as a string
        """
        # Handle time typing
        try:
            time = time.isoformat()
        except AttributeError:  # Not a datetime object
            time = str(time)

        time = parser.parse(time).strftime('%Y-%m-%d %H:%M:%S')
        return time

    @staticmethod
    def format_date(date):
        """Formats a date to be Shapeways database-compatible

        @param date: Datetime or string object to format
        @rtype: str
        @return: Date formatted as a string
        """
        # Handle time typing
        try:
            date = date.isoformat()
        except AttributeError:  # Not a datetime object
            date = str(date)

        date = parser.parse(date).strftime('%Y-%m-%d')
        return date

    @staticmethod
    def db_escape(string):
        """Escapes special characters in a string

        @param string: The string to escape
        @return: String with escaped special characters
        """
        string = MySQLdb.escape_string(string)
        return string
