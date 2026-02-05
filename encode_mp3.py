import base64
 
with open("audio/myaudio.mp3", "rb") as f:  # Change to your file name if needed
    encoded = base64.b64encode(f.read()).decode("utf-8")
 
# Write the base64 string to output.txt
with open("output.txt", "w") as out:
    out.write(encoded)
print("Base64 string written to output.txt")