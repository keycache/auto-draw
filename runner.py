import cv2
import numpy as np
import streamlit as st

from constants import ACTIVE
from image_orchestrator import AutoImageDraw


def process_image(image):
    st.write(type(st.session_state["image-display"]))
    aid = AutoImageDraw(image=st.session_state["image-display"])
    print("Processing image")
    aid.process_image()
    print("Image processing complete")
    colorized_aid = aid.create_version()
    image = colorized_aid.create_image()
    st.session_state["image-display"] = image


def run():
    st.session_state["image-display"] = None
    with st.form(key="coloring-image-form"):
        image_file = st.file_uploader(
            "Select coloring image",
            key="coloring-image-form-upload",
            type=("png", "jpg", "jpeg"),
        )
        submitted = st.form_submit_button()

    if submitted:
        if not image_file:
            st.error("Need to enter an image path")
            return
        file_bytes = np.asarray(bytearray(image_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, 1)
        st.session_state["image-display"] = image
    image_placeholder = st.empty()
    if st.session_state["image-display"] is not None:
        image_placeholder.image(
            image=st.session_state["image-display"], channels="BGR"
        )
        process_image(st.session_state["image-display"])
        image_placeholder.image(
            image=st.session_state["image-display"], channels="BGR"
        )


if __name__ == "__main__":
    run()
