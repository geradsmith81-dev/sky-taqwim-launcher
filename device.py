"""Phone layout: one switch the pages consult to fit a small, upright screen.

It starts ON when the browser says it is a phone (User-Agent contains Mobile, iPhone, iPod or
Android) and can be changed in the sidebar. With it on, the settings move into a fold-out panel
at the top of the page and the month is shown as a day-by-day list instead of a grid.
"""
import streamlit as st

KEY = "phone_layout"
PHONE_WORDS = ("mobi", "iphone", "ipod", "android")


def detected() -> bool:
    try:
        ua = (st.context.headers.get("User-Agent") or "").lower()
    except Exception:
        ua = ""
    return any(w in ua for w in PHONE_WORDS)


def phone() -> bool:
    if KEY not in st.session_state:
        st.session_state[KEY] = detected()
    return bool(st.session_state[KEY])


def switch():
    phone()
    st.sidebar.toggle("Phone layout", key=KEY,
                      help="Fits the pages to a phone: settings in a panel at the top, the month as a list. "
                           "It switches on by itself on phones.")


def input_panel(label: str, expanded: bool = False):
    """The sidebar on a computer, a fold-out panel at the top of the page on a phone."""
    if phone():
        return st.expander(label, expanded=expanded, icon=":material/tune:")
    return st.sidebar
