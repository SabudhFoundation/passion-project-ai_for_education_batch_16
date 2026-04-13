task 1: text extraction  tool used reducto
code for the same :-
from reducto import Reducto
from pathlib import Path
import json

# client init
client = Reducto(api_key="e02d0bf058bada7a6ca848dc99081385d4bf09a1004a63547855f6957a69eca81c8e0d392350a9ad39e8dd4f78a4db33")



# upload file
upload = client.upload(file=Path("resume.pdf"))

# schema
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "email": {"type": "string"},
        "phone": {"type": "string"},
        "skills": {
            "type": "array",
            "items": {"type": "string"}
        },
        "education": {
            "type": "array",
            "items": {"type": "string"}
        },
        "projects": {
            "type": "array",
            "items": {"type": "string"}
        },
        "experience": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}

# extract
result = client.extract.run(
    input=upload.file_id,
    instructions={
        "schema": schema,
        "system_prompt": "This is a student resume. Extract structured info."
    },
    settings={
        "array_extract": True
    }
)

# convert JSON → pointer format
def json_to_points(data, indent=0):
    space = "  " * indent

    if isinstance(data, dict):
        for k, v in data.items():
            print(f"{space}{k.upper()}:")
            json_to_points(v, indent + 1)

    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                json_to_points(item, indent + 1)
            else:
                print(f"{space}- {item}")

    else:
        print(f"{space}{data}")

# output
print("\n🔹 POINTER FORMAT:\n")
json_to_points(result.result[0])


task 2: the web scrapper 