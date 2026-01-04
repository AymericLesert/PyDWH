# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the abstract technical rule.
"""

import os
import csv
import datetime

from tools.date import Date
from tools.markdown import Markdown

from rule.technical.ruletechnical import DWHRuleTechnical

class DWHRuleTechnicalValues(DWHRuleTechnical):
    """This class defines a technical rule extracting all distinguished values into the table"""

    @property
    def description(self):
        return self.__description

    def execute(self, table):
        self.info(f"Appending into the CSV file '{self.__csv_file}' ...")
        
        date = datetime.datetime.now().strftime(Date.DATETIME)
        columns = ['date', 'table', 'field', 'value', 'count']
        row = { 'date': date, 'table': table.name, 'field': self.__field, 'value': '', 'count' : 0 }
        nb_rows = 0

        directory = os.path.dirname(self.__csv_file)
        if directory != '':
            try:
                os.makedirs(directory, exist_ok=True)
            except:
                pass

        add_header = not (os.path.exists(self.__csv_file) and os.path.getsize(self.__csv_file) > 0)
        with open(self.__csv_file, 'a', newline='', encoding=self.__encoding) as csvfile:
            writer = csv.DictWriter(csvfile, delimiter=self.__delimiter, quoting = csv.QUOTE_STRINGS, fieldnames=columns)
            if add_header:
                writer.writeheader()

            for line in table.get_distinct_values(self.__field):
                row['value'] = line[0]
                row['count'] = line[1]
                writer.writerow(row)
                nb_rows += 1

        self.verbose(f"{nb_rows} values(s) in '{row['table']}.{row['field']}''")
        return True

    def markdown(self, table, directory):
        """Get the markdown documentation of the technical rule (counting the list of values)"""
        if directory is None and self.__field not in table.fields:
            return None

        self.info(f"Creating markdown documentation for the field '{table.name}.{self.__field}' ...")

        try:
            os.makedirs(directory, exist_ok=True)
        except:
            self.exception(f"Unable to create directory '{directory}' for markdown field")

        markdown_filename = os.path.join(directory, self.__field + '.md')
        markdown_file = open(markdown_filename, 'w', encoding='utf-8')
        markdown_file.write(f"# Valeur du champ '{table.name}.{self.__field}'\n\n")

        description = table.fields[self.__field].description
        if description is not None and description != "":
            markdown_file.write(f"**description** : {description}\n\n")
            
        markdown_file.write("| Valeur | Nombre d'enregistrements |\n")
        markdown_file.write("| :--- | :----: |\n")

        nb_rows = 0
        for line in table.get_distinct_values(self.__field):
            markdown_file.write(f"| {line[0]} | {line[1]} |\n")
            nb_rows += 1
        self.__description = f"Le champ '{table.name}.{self.__field}' contient {nb_rows} valeurs distinctes"

        markdown_file.close()
        Markdown.Convert(markdown_filename)

        return os.path.join(table.name, self.__field + '.md')

    def __init__(self, name, csv_file, delimiter=';', encoding='utf-8', field = None, **kwargs):
        super().__init__(name)
        self.__csv_file = csv_file
        self.__delimiter = delimiter
        self.__encoding = encoding
        self.__field = field
        self.__description = f"Cette règle extrait les valeurs distinctes de la colonne '{self.__field}' dans la table"
