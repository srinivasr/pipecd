import json

with open("pkg/app/ops/firestoreindexensurer/indexes.json", "r") as f:
    data = json.load(f)

# The 4 bad paths to remove
bad_paths = [
    ["ProjectId", "Id"],
    ["ProjectId", "Name", "Id"],
    ["ProjectId", "Kind", "Id"],
    ["ProjectId", "Name", "Kind", "Id"],
]

new_indexes = []
for idx in data:
    if idx.get("collectionGroup") == "Application":
        paths = [f["fieldPath"] for f in idx.get("fields", [])]
        if paths in bad_paths:
            continue
    new_indexes.append(idx)

# Find where ProjectId | PipedId | Disabled | Id is
insert_pos = 0
for i, idx in enumerate(new_indexes):
    if idx.get("collectionGroup") == "Application":
        paths = [f["fieldPath"] for f in idx.get("fields", [])]
        if paths == ["ProjectId", "PipedId", "Disabled", "Id"]:
            insert_pos = i + 1
            break

new_app_1 = {
    "collectionGroup": "Application",
    "queryScope": "COLLECTION",
    "fields": [
        {"fieldPath": "ProjectId", "order": "ASCENDING", "arrayConfig": ""},
        {"fieldPath": "Disabled", "order": "ASCENDING", "arrayConfig": ""},
        {"fieldPath": "Name", "order": "ASCENDING", "arrayConfig": ""},
        {"fieldPath": "Id", "order": "ASCENDING", "arrayConfig": ""}
    ]
}

new_app_2 = {
    "collectionGroup": "Application",
    "queryScope": "COLLECTION",
    "fields": [
        {"fieldPath": "ProjectId", "order": "ASCENDING", "arrayConfig": ""},
        {"fieldPath": "Disabled", "order": "ASCENDING", "arrayConfig": ""},
        {"fieldPath": "Kind", "order": "ASCENDING", "arrayConfig": ""},
        {"fieldPath": "Id", "order": "ASCENDING", "arrayConfig": ""}
    ]
}

new_app_3 = {
    "collectionGroup": "Application",
    "queryScope": "COLLECTION",
    "fields": [
        {"fieldPath": "ProjectId", "order": "ASCENDING", "arrayConfig": ""},
        {"fieldPath": "Disabled", "order": "ASCENDING", "arrayConfig": ""},
        {"fieldPath": "Name", "order": "ASCENDING", "arrayConfig": ""},
        {"fieldPath": "Kind", "order": "ASCENDING", "arrayConfig": ""},
        {"fieldPath": "Id", "order": "ASCENDING", "arrayConfig": ""}
    ]
}

new_indexes.insert(insert_pos, new_app_3)
new_indexes.insert(insert_pos, new_app_2)
new_indexes.insert(insert_pos, new_app_1)

with open("pkg/app/ops/firestoreindexensurer/indexes.json", "w") as f:
    json.dump(new_indexes, f, indent=2)

with open("pkg/app/ops/firestoreindexensurer/indexes.json", "a") as f:
    f.write("\n")

# Now generate indexes_test.go
go_code = []
for idx in new_indexes:
    go_code.append("\t\t{")
    go_code.append(f'\t\t\tCollectionGroup: "{idx["collectionGroup"]}",')
    go_code.append(f'\t\t\tQueryScope:      "{idx["queryScope"]}",')
    go_code.append("\t\t\tFields: []field{")
    for field in idx["fields"]:
        go_code.append("\t\t\t\t{")
        go_code.append(f'\t\t\t\t\tFieldPath:   "{field["fieldPath"]}",')
        go_code.append(f'\t\t\t\t\tOrder:       "{field["order"]}",')
        go_code.append(f'\t\t\t\t\tArrayConfig: "{field.get("arrayConfig", "")}",')
        go_code.append("\t\t\t\t},")
    go_code.append("\t\t\t},")
    go_code.append("\t\t},")

want_slice = "\n".join(go_code)

with open("pkg/app/ops/firestoreindexensurer/indexes_test.go", "r") as f:
    lines = f.readlines()

new_lines = []
in_want = False
for line in lines:
    if "want := []index{" in line:
        new_lines.append(line)
        new_lines.append(want_slice + "\n")
        in_want = True
    elif in_want:
        if line == "\t}\n":
            in_want = False
            new_lines.append(line)
    else:
        new_lines.append(line)

with open("pkg/app/ops/firestoreindexensurer/indexes_test.go", "w") as f:
    f.writelines(new_lines)
