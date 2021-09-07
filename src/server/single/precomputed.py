def update_response(response, row):
    update_speaking_time(response, row)
    update_relative_diff(response, row)
    update_unanchored(response, row)
    update_wpm(response, row)

def update_speaking_time(response, row):
    role = row["role"]
    if role not in response["speaking_time"]:
        response["speaking_time"][role] = [[
            "Election period",
            "Words",
            "Sentences",
            "Paragraphs",
            "Utterances"
        ]]

    response["speaking_time"][role].append([
        row["election_period"],
        row["length_word"],
        row["length_sentence"],
        row["length_paragraph"],
        row["length_utterance"]
    ])

def update_relative_diff(response, row):
    role = row["role"]
    if role not in response["relative_diff"]:
        response["relative_diff"][role] = [[
            "Election period",
            "Utterance vs paragraph",
            "Paragraph vs sentence",
            "Sentence vs word"
        ]]

    response["relative_diff"][role].append([
        row["election_period"],
        row["utterance-paragraph"],
        row["paragraph-sentence"],
        row["sentence-word"]
    ])

def update_unanchored(response, row):
    role = row["role"]
    if role not in response["unanchored"]:
        response["unanchored"][role] = [["Election period", "Unanchored"]]

    response["unanchored"][role].append([
        row["election_period"],
        row["unanchored"]
    ])

def update_wpm(response, row):
    role = row["role"]
    if role not in response["wpm"]:
        response["wpm"][role] = [["Election period", "Words per mminute"]]

    response["wpm"][role].append([
        row["election_period"],
        row["words_per_minute"]
    ])

