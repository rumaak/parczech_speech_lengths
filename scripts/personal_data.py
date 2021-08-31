#!/usr/bin/env python3

import sys
import json
import os

import pandas as pd

# This script expects path to a file with personal data, path to a file with
# affiliations-related data, and path to an output directory. The script
# transforms the data into more suitable JSON format and saves it into the 
# output directory.

class Aggregator:
    def __init__(self, file_personal, file_affiliations, dir_out):
        self.file_personal = os.path.relpath(file_personal)
        self.file_affiliations = os.path.relpath(file_affiliations)
        self.dir_out = os.path.relpath(dir_out)

        self.personal_data = dict()

    def aggregate(self):
        personal_data_df = pd.read_csv(self.file_personal, sep="\t")
        personal_data_df.apply(self.parse_row_personal, axis=1)

        affiliations_df = pd.read_csv(self.file_affiliations, sep="\t")
        affiliations_df.apply(self.parse_row_affiliations, axis=1)

        path = os.path.join(self.dir_out, "ParCzech.ana.json")
        with open(path, "w") as file:
            json.dump(self.personal_data, file, indent=4)

    def parse_row_affiliations(self, row):
        speaker = row["id"]
        affiliation_type = row["type"]

        if speaker not in self.personal_data:
            self.personal_data[speaker] = {
                affiliation_type: []
            }
        elif affiliation_type not in self.personal_data[speaker]:
            self.personal_data[speaker][affiliation_type] = []

        affiliations = self.personal_data[speaker][affiliation_type]
        affiliations.append({
            "name_cs": row["name_cs"],
            "name_en": row["name_en"],
            "name_short": row["name_short"],
            "from": row["from"],
            "to": row["to"]
        })

    def parse_row_personal(self, row):
        fields = ["surname", "forename", "sex", "birth", "picture"]

        speaker = row["id"]

        if speaker not in self.personal_data:
            self.personal_data[speaker] = dict()

        personal_data = self.personal_data[speaker]
        for field in fields:
            personal_data[field] = row[field]

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 3:
        aggregator = Aggregator(args[0], args[1], args[2])
        aggregator.aggregate()
    else:
        print("Incorrect number of args")

