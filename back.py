from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
import tempfile
import os
from steg import ImageSteganography
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
steg = ImageSteganography()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/steganography/hide")
async def hide_message(
    image: UploadFile = File(...),
    message: str = Form(...),
    password: str = Form(...)
):
    try:
        # Create temporary files for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_input:
            # Save uploaded file
            content = await image.read()
            temp_input.write(content)
            temp_input.flush()

        # Create temporary output file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_output:
            output_path = temp_output.name

        # Process the image
        steg.hide_message(temp_input.name, message, password, output_path)

        # Clean up input temp file
        os.unlink(temp_input.name)

        # Return the processed image
        return FileResponse(
            output_path,
            media_type='image/png',
            filename='stego_image.png',
            background=lambda: os.unlink(output_path)
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while processing the image")

@app.post("/api/steganography/extract")
async def extract_message(
    image: UploadFile = File(...),
    password: str = Form(...)
):
    try:
        # Create temporary file for processing
        # with tempfile.NamedTemporaryFile(
        #     delete=False, suffix='.png') as temp_file:
        temp_file = open("temp.png", "wb")
        content = await image.read()
        temp_file.write(content)
        temp_file.flush()
        # Extract the message
        message = steg.extract_message(temp_file.name, password)
        # Clean up
        os.unlink(temp_file.name)
        return {"message": message}

    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while extracting the message")
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)