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
        return self.__description

    def execute(self, table):
        # TODO : Write into a writer (CSV, DB, ...)
        self.info(f"Appending into the CSV file '{self.__csv_file}' ...")
        
        date = datetime.datetime.now().strftime(Date.DATETIME)
        columns = ['date', 'table', 'rows']
        row = { 'date': date, 'table': table.name, 'rows' : table.count_rows }

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
            writer.writerow(row)

        self.verbose(f"{row['rows']} line(s) in '{row['table']}''")

        self.send_mail(self.__email,
                        f"[{self.name}] [{Date.NOW.strftime("%Y-%m-%d")}] Notification", 
                        f"La table '{table.name}' compte {row['rows']} ligne(s).", 
                        self.__csv_file)
        return True

    def markdown(self, table, directory):
        """Get the markdown documentation of the technical rule (counting the number of rows)"""
        self.__description = f"La table compte {table.count_rows} ligne(s) dans la table."
        return super().markdown(table, directory)

    def __init__(self, instance, name, csv_file, delimiter=';', encoding='utf-8', email = None, **kwargs):
        super().__init__(instance, name)
        self.__csv_file = csv_file
        self.__delimiter = delimiter
        self.__encoding = encoding
        self.__description = "Cette règle compte le nombre de lignes dans la table"
        self.__email = email
