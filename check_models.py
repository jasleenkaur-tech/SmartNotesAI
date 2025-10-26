import google.generativeai as genai

for model in genai.list_models():
    print(model.name)
