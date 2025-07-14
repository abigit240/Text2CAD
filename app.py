from flask import Flask, render_template, request
import requests
import subprocess
import re

app = Flask(__name__)

def extract_block_dimensions(text):
    # Try to find labeled lines like "Length: 100mm", "Width: 20mm", "Height: 20mm"
    length_match = re.search(r"length.*?(\d+)", text, re.IGNORECASE)
    width_match = re.search(r"width.*?(\d+)", text, re.IGNORECASE)
    height_match = re.search(r"height.*?(\d+)", text, re.IGNORECASE)

    if length_match and width_match and height_match:
        return int(length_match.group(1)), int(width_match.group(1)), int(height_match.group(1))

    # Fallback: look for format like "100 x 20 x 20"
    match = re.search(r"(\d+)\s*(?:mm)?\s*[xX×]\s*(\d+)\s*(?:mm)?\s*[xX×]\s*(\d+)", text)
    return tuple(map(int, match.groups())) if match else None

def extract_solid_cylinder_dimensions(text):
    # Match radius and height, optionally with mm
    radius_match = re.search(r"radius.*?(\d+)", text, re.IGNORECASE)
    height_match = re.search(r"height.*?(\d+)", text, re.IGNORECASE)

    if radius_match and height_match:
        return int(radius_match.group(1)), int(height_match.group(1))
    return None

@app.route("/", methods=["GET", "POST"])
def index():
    output = ""
    cad_result = ""

    if request.method == "POST":
        user_prompt = request.form["prompt"]

        # === Step 1: Query LLaMA (Ollama) ===
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama3", "prompt": user_prompt, "stream": False}
            )
            result = response.json()
            output = result.get("response", "")
        except Exception as e:
            output = f"LLM Error: {e}"
            cad_result = "❌ LLaMA API error — make sure Ollama is running"
            return render_template("index.html", output=output, cad_result=cad_result)

        # === Step 2: Determine shape and extract dimensions ===
        output_lower = output.lower()
        shape = None
        if "cylinder" in output_lower:
            shape = "solid_cylinder"
        elif "block" in output_lower:
            shape = "block"

        print(f"📨 Model response:\n{output}")
        print(f"🔍 Detected shape: {shape}")
        print(f"🧾 Raw output from model: {repr(output)}")

        if shape == "block":
            dims = extract_block_dimensions(output)
            print(f"📦 Block dimensions: {dims}")
            if dims:
                length, width, height = dims
                try:
                    subprocess.run([
                        "python", "create_block.py",
                        str(length), str(width), str(height)
                    ], check=True)
                    cad_result = f"✅ Block created: {length}×{width}×{height} mm"
                except subprocess.CalledProcessError as e:
                    cad_result = f"❌ Error running create_block.py: {e}"
            else:
                cad_result = "❌ Block dimensions not found."

        elif shape == "solid_cylinder":
            dims = extract_solid_cylinder_dimensions(output)
            print(f"🔵 Solid cylinder dimensions: {dims}")
            if dims:
                radius, height = dims
                try:
                    subprocess.run([
                        "python", "create_solidcylinder.py",
                        str(radius), str(height)
                    ], check=True)
                    cad_result = f"✅ Solid cylinder created: Radius={radius} mm, Height={height} mm"
                except subprocess.CalledProcessError as e:
                    cad_result = f"❌ Error running create_solidcylinder.py: {e}"
            else:
                cad_result = "❌ Solid cylinder dimensions not found."

        else:
            cad_result = "❌ Shape type not detected in LLM output."

    return render_template("index.html", output=output, cad_result=cad_result)

if __name__ == "__main__":
    app.run(debug=True)
