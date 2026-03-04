# create basic form and call dummy API online available in internet
import streamlit as st
import requests

st.set_page_config(layout="centered")
st.title("Create Post (Dummy API)")

def create_post_api(title: str, body: str, user_id: int) -> dict:
    url = "https://jsonplaceholder.typicode.com/posts"

    payload = {
        "title": title,
        "body": body,
        "userId": user_id,
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()

        return {
            "success": True,
            "data": response.json(),
            "status": response.status_code,
        }

    except requests.RequestException as e:
        return {
            "success": False,
            "error": str(e),
        }

with st.form("create_post_form"):
    title = st.text_input("Title")
    body = st.text_area("Body")
    user_id = st.number_input("User ID", min_value=1, step=1)

    submitted = st.form_submit_button("Submit")

if submitted:
    with st.spinner("Sending request..."):
        result = create_post_api(title, body, user_id)

    if result["success"]:
        st.success(f"Status: {result['status']}")
        st.json(result["data"])
    else:
        st.error(result["error"])