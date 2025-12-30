import streamlit as st

def confidence_badge(confidence: float, decision: str | None = None):
    """
    Render a colored confidence badge.
    """

    if decision == "REJECTED":
        st.markdown(
            "<span style='background:#ff4d4f;color:white;padding:4px 10px;"
            "border-radius:12px;font-size:13px;'>🔴 REJECTED</span>",
            unsafe_allow_html=True,
        )
    elif confidence >= 0.80:
        st.markdown(
            "<span style='background:#52c41a;color:white;padding:4px 10px;"
            "border-radius:12px;font-size:13px;'>🟢 STRONG</span>",
            unsafe_allow_html=True,
        )
    elif confidence >= 0.65:
        st.markdown(
            "<span style='background:#faad14;color:black;padding:4px 10px;"
            "border-radius:12px;font-size:13px;'>🟡 PROBABLE</span>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<span style='background:#d9d9d9;color:black;padding:4px 10px;"
            "border-radius:12px;font-size:13px;'>UNKNOWN</span>",
            unsafe_allow_html=True,
        )
