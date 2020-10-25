from flask import Flask, request, jsonify, render_template


def detect_text(path):
    """Detects text in the file."""
    from google.cloud import vision
    import io
    import os
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=r"C:\Users\shahd\OneDrive\Desktop\MediDate Application\MediDate_Credentials\steel-aileron-266916-d88c69f449c7.json"
# Imports the Google Cloud client library
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    
    d = {"Name": "Advil", "Fill Date": 0, "RX": 0, "Qty": 90, "date-to-take": 0, "Morning": 1, "Noon": 3,"Evening": 2, "MorningClick": 0, "NoonClick": 0, "EveningClick": 0}
    count = 0
    for text in texts:
        if(text.description == "Rx" or text.description == "Rx#" or text.description == "#" or text.description == "Rx:" or text.description == "Rx:#" or text.description == "Rx: #" or text.description == ":"):
            count = 1
            continue
        if(text.description[0:2] == "Qty"):
            d["Qty"] = text.description[3:len(text.description)-1]
            
        if(count == 1):
            d["RX"] = text.description
            count = 0
        vertices = (['({},{})'.format(vertex.x, vertex.y)
                    for vertex in text.bounding_poly.vertices])

        print('bounds: {}'.format(','.join(vertices)))
    return d

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))