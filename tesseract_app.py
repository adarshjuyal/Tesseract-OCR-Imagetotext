import numpy as np
import pytesseract
import streamlit as st
import helpers.constants as constants
import helpers.opencv as opencv
import helpers.tesseract as tesseract

# pytesseract.pytesseract.tesseract_cmd = None
# if text not in st.session_state:
#     st.session_state.text = ""

# set tesseract path
# @st.cache_resource
# @st.cache(allow_output_mutation=True)
# def set_tesseract_path(tesseract_path: str):
#     pytesseract.pytesseract.tesseract_cmd = tesseract_path

# streamlit config
st.set_page_config(page_title="Tesseract OCR", page_icon="📖", layout="wide", initial_sidebar_state="expanded")

# apply custom css
with open('helpers/style.css') as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

# add streamlit title
st.title("Image to Text convertor - Optical Character Recognition 🪬")

# add streamlit markdown text
st.markdown('''**Tesseract OCR** - Optical Character Recognition using Tesseract, OpenCV and Streamlit.<br>
This is a simple OCR demo app that can be used to extract text from images.
        Tweak with Image preproccessing parameter to get the best results
''', unsafe_allow_html=True)

# set tesseract binary path
# pytesseract.pytesseract.tesseract_cmd = tesseract.find_tesseract_binary()
# if not pytesseract.pytesseract.tesseract_cmd:
#     st.error("Tesseract binary not found in PATH. Please install Tesseract.")
#     st.stop()

# check if tesseract is installed
try:
    tesseract_version = pytesseract.get_tesseract_version()
except pytesseract.TesseractNotFoundError:
    st.error("TesseractNotFoundError: Tesseract is not installed. Please install Tesseract.")
    st.stop()
except Exception as e:
    st.error("Unexpected Exception")
    st.error(f"Error Message: {e}")
    st.stop()
else:
    if not tesseract_version:
        st.error("Tesseract is not installed. Please install Tesseract.")
        st.stop()

# with st.sidebar:
    # st.success(f"Tesseract Version **{tesseract_version}** is installed.")
    # st.header("OCR Settings")
    # st.markdown('---')
    # st.header("Image Preprocessing")
    # st.write("Check the boxes below to apply preprocessing to the image.")
    # cGrayscale = st.checkbox(label="Grayscale", value=True)
    # cDenoising = st.checkbox(label="Denoising", value=True)
    # cDenoisingStrength = st.slider(label="Denoising Strength", min_value=1, max_value=40, value=1, step=1)
    # cThresholding = st.checkbox(label="Thresholding", value=True)
    # cThresholdLevel = st.slider(label="Threshold Level", min_value=0, max_value=255, value=200, step=1)
    # cRotate90 = st.checkbox(label="Rotate in 90° steps", value=False)
    # angle90 = st.slider("Rotate rectangular [Degree]", min_value=0, max_value=270, value=0, step=90)
    # cRotateFree = st.checkbox(label="Rotate in free degrees", value=False)
    # angle = st.slider("Rotate freely [Degree]", min_value=-180, max_value=180, value=0, step=1)

# two column layout for image preprocessing options and image preview
col1, col2 = st.columns(spec=[2, 3], gap="large")
image = None

with col1:
    # upload image
    st.subheader("Upload Image")
    uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg", "bmp", "tif", "tiff"])

    if uploaded_file is not None:
        try:
                # convert uploaded file to numpy array
            image = opencv.load_image(uploaded_file)
        except Exception as e:
            st.error("Exception during Image Conversion")
            st.error(f"Error Message: {e}")
            st.stop()
        try:
            st.header("OCR Settings")
            st.markdown('---')
            st.header("Image Preprocessing")
            st.write("Check the boxes below to apply preprocessing to the image.")
            cGrayscale = st.checkbox(label="Grayscale", value=True)
            cDenoising = st.checkbox(label="Denoising", value=True)
            cDenoisingStrength = st.slider(label="Denoising Strength", min_value=1,max_value=40, value=1, step=1)
            cThresholding = st.checkbox(label="Thresholding", value=True)
            cThresholdLevel = st.slider(label="Threshold Level", min_value=0,max_value=255, value=200, step=1)
            cRotate90 = st.checkbox(label="Rotate in 90° steps", value=False)
            angle90 = st.slider("Rotate rectangular [Degree]", min_value=0,max_value=270, value=0, step=90)
            cRotateFree = st.checkbox(label="Rotate in free degrees", value=False)
            angle = st.slider("Rotate freely [Degree]", min_value=-180,max_value=180, value=0, step=1)
            if cGrayscale:
                image = opencv.grayscale(image)
            if cDenoising:
                image = opencv.denoising(image, strength=cDenoisingStrength)
            if cThresholding:
                image = opencv.thresholding(image, threshold=cThresholdLevel)
            if cRotate90:
                # convert angle to opencv2 enum
                angle90 = constants.angles.get(angle90, None)
                image = opencv.rotate90(image, rotate=angle90)
            if cRotateFree:
                image = opencv.rotate_scipy(image, angle=angle, reshape=True)
            image = opencv.convert_to_rgb(image)
        except Exception as e:
            st.error(f"Exception during Image Preprocessing (Probably you selected Threshold on a color image?): {e}")
            st.stop()

with col2:
    st.subheader("Image Preview")
    if image is not None:
        # preview image
        st.image(image, caption="Uploaded Image Preview", use_column_width=True)

        # add streamlit button
        if st.button("Extract Text"):
            # streamlit spinner
            with st.spinner("Extracting Text..."):
                try:
                    text = pytesseract.image_to_string(image=image)
                except pytesseract.TesseractError as e:
                    st.error("TesseractError: Tesseract reported an error during text extraction.")
                    st.error(f"Error Message: {e}")
                    st.stop()
                except pytesseract.TesseractNotFoundError:
                    st.error("TesseractNotFoundError: Tesseract is not installed. Please install Tesseract..")
                    st.stop()
                except RuntimeError:
                    st.error("RuntimeError: Tesseract timed out during text extraction.")
                    st.stop()
                except Exception as e:
                    st.error("Unexpected Exception")
                    st.error(f"Error Message: {e}")
                    st.stop()

            if text:
                    # TODO: try Ace Editor for text area instead
                    # add streamlit text area
                    # st.text_area(label="Extracted Text", value=text, height=500)
                    st.code(text, language="text")
                    st.download_button(label="Download Extracted Text", data=text.encode("utf-8"), file_name="extract.txt", mime="text/plain")
            else:
                st.warning("No text was extracted.")
