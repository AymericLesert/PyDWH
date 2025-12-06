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

class DWHRuleTechnicalCountRow(DWHRuleTechnical):
    """This class defines a technical rule computing the number of rows into the table"""

    @property
    def description(self):
        return "Cette règle est utilisée pour suivre la progression du nombre de lignes dans la table"

    def execute(self, table):
        self.info(f"Appending into the CSV file '{self.__csv_file}' ...")
        
        date = datetime.datetime.now().strftime(Date.DATETIME)
        columns = ['date', 'table', 'rows']
        row = { 'date': date, 'table': table.name, 'rows' : table.count_rows }

        add_header = not (os.path.exists(self.__csv_file) and os.path.getsize(self.__csv_file) > 0)
        with open(self.__csv_file, 'a', newline='', encoding=self.__encoding) as csvfile:
            writer = csv.DictWriter(csvfile, delimiter=self.__delimiter, quoting = csv.QUOTE_STRINGS, fieldnames=columns)
            if add_header:
                writer.writeheader()
            writer.writerow(row)

        self.verbose(f"{row['rows']} line(s) in '{row['table']}''")
        return True

    def __init__(self, name, csv_file, delimiter=';', encoding='utf-8', fields = False, **kwargs):
        super().__init__(name)
        self.__csv_file = csv_file
        self.__delimiter = delimiter
        self.__encoding = encoding
        self.__fields = fields
