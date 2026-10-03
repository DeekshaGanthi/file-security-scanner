import os
import streamlit as st
import requests


API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


st.set_page_config(
    page_title="AI File Security Scanner",
    page_icon="🛡️",
    layout="wide"
)


st.title(
    "🛡️ AI File Security Scanner"
)


st.write(
    """
Upload a file and analyze it for
suspicious indicators.

The system performs static analysis,
calculates a risk score, and uses
Gemini to explain the results.
"""
)


uploaded_file = st.file_uploader(
    "Upload a file",
    type=[
        "pdf",
        "txt",
        "jpg",
        "jpeg",
        "png",
        "gif",
        "webp",
        "bmp"
    ]
)


if uploaded_file:

    st.write(
        "### Selected File"
    )

    st.write(
        uploaded_file.name
    )

    if st.button(
        "Scan File"
    ):

        with st.spinner(
            "Analyzing file..."
        ):

            try:

                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type
                    )
                }

                response = requests.post(
                    f"{API_URL}/scan",
                    files=files
                )

                result = response.json()

            except Exception as error:

                st.error(
                    f"Error: {error}"
                )

                st.stop()


        st.success(
            "Scan completed"
        )


        risk = result["risk"]


        col1, col2 = st.columns(2)


        with col1:

            st.metric(
                "Risk Score",
                f"{risk['score']} / 100"
            )


        with col2:

            st.metric(
                "Risk Level",
                risk["level"]
            )


        st.write(
            "## Static Analysis"
        )

        st.json(
            result["analysis"]
        )


        st.write(
            "## Risk Indicators"
        )

        if risk["reasons"]:

            for reason in risk["reasons"]:

                st.warning(
                    reason
                )

        else:

            st.success(
                "No suspicious indicators found."
            )


        st.write(
            "## 🤖 Gemini AI Security Analysis"
        )


        gemini = result[
            "gemini_analysis"
        ]


        if gemini["success"]:

            st.write(
                gemini["report"]
            )

        else:

            st.error(
                gemini["message"]
            )


st.divider()


st.write(
    "## Previous Scans"
)


if st.button(
    "Load Scan History"
):

    try:

        response = requests.get(
            f"{API_URL}/scans"
        )

        scans = response.json()

        st.dataframe(
            scans,
            use_container_width=True
        )

    except Exception as error:

        st.error(
            str(error)
        )