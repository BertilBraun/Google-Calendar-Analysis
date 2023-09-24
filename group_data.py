import json


def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def tokenize_event(event):
    return tuple(sorted(word.lower() for word in event.split(' ')))


def analyze_data(data):
    grouped_data = {
        "Svenja": {"count": 0, "entries": {}},
        "Sex_related": {"count": 0, "entries": {}},
        "Kuschel_related": {"count": 0, "entries": {}},
        "Academic": {"count": 0, "entries": {}},
        "Work_and_Projects": {"count": 0, "entries": {}},
        "Others": {"count": 0, "entries": {}},
        "Tokenized": {}
    }

    for event, count in data.items():
        # Always count for 'Others'
        grouped_data["Others"]["count"] += count
        grouped_data["Others"]["entries"][event] = count

        # Old style grouping
        if 'Svenja' in event:
            grouped_data["Svenja"]["count"] += count
            grouped_data["Svenja"]["entries"][event] = count

        if 'sex' in event.lower():
            grouped_data["Sex_related"]["count"] += count
            grouped_data["Sex_related"]["entries"][event] = count

        if 'kuschel' in event.lower():
            grouped_data["Kuschel_related"]["count"] += count
            grouped_data["Kuschel_related"]["entries"][event] = count

        if any(keyword in event for keyword in ['BA', 'ÜB', 'VL', 'Klausur', 'klausur']):
            grouped_data["Academic"]["count"] += count
            grouped_data["Academic"]["entries"][event] = count

        if any(keyword in event for keyword in ['CAS', 'Daimler', 'Pyro', 'Symp']):
            grouped_data["Work_and_Projects"]["count"] += count
            grouped_data["Work_and_Projects"]["entries"][event] = count

    tokenized_grouping = {}

    for event, count in data.items():
        tokens = tokenize_event(event)

        if tokens not in tokenized_grouping:
            tokenized_grouping[tokens] = {'count': 0, 'entries': {}}

        tokenized_grouping[tokens]['count'] += count
        tokenized_grouping[tokens]['entries'][event] = count

    # Replace keys in Tokenized section with the most frequent entry
    for tokens, group_data in tokenized_grouping.items():
        most_frequent_entry = max(
            group_data['entries'], key=group_data['entries'].get)
        grouped_data["Tokenized"][most_frequent_entry] = group_data

    return grouped_data


def main():
    # Load the cleaned data
    data = load_data('cleaned_sorted_events.json')

    # Analyze and group the data
    grouped_data = analyze_data(data)

    # Sort the "Tokenized" section by count
    sorted_tokenized = {k: v for k, v in sorted(grouped_data["Tokenized"].items(
    ), key=lambda item: item[1]['count'] if isinstance(item[1], dict) else item[1], reverse=True)}

    # Update the "Tokenized" section to have the count as the value for single-entry groups
    for k, v in sorted_tokenized.items():
        if isinstance(v, dict) and len(v['entries']) == 1:
            sorted_tokenized[k] = v['count']

    grouped_data["Tokenized"] = sorted_tokenized

    # Save the grouped data to a new JSON file
    with open('grouped_data.json', 'w', encoding='utf-8') as f:
        json.dump(grouped_data, f, indent=4, ensure_ascii=False)

    print("Grouped data has been saved to grouped_data.json")


if __name__ == '__main__':
    main()
