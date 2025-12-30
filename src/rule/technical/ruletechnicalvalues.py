# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes the abstract technical rule.
"""

import os
import csv
import datetime

from tools.date import Date

from rule.technical.ruletechnical import DWHRuleTechnical

class DWHRuleTechnicalValues(DWHRuleTechnical):
    """This class defines a technical rule extracting all distinguished values into the table"""

    @property
    def description(self):
        return "Cette règle est utilisée pour suivre la progression du nombre de lignes dans la table"

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

    def __init__(self, name, csv_file, delimiter=';', encoding='utf-8', field = None, **kwargs):
        super().__init__(name)
        self.__csv_file = csv_file
        self.__delimiter = delimiter
        self.__encoding = encoding
        self.__field = field
