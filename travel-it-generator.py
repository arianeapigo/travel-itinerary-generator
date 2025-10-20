import os
import streamlit as st
from openai import AzureOpenAI
from typing import Any


def _get_env_or_default(name: str, default: str | None = None) -> str | None:
    return os.environ.get(name, default)


# Page config
st.set_page_config(page_title="Travel Itinerary Generator 🌎", page_icon="🌎", layout="wide")

# Create a container for the sticky header
header_container = st.container()
with header_container:
    st.markdown("""
        <div style="position: fixed; top: 3.5rem; left: 0; right: 0; background-color: white; z-index: 999; padding: 1rem; border-bottom: 1px solid #ddd;">
            <h1 style="margin: 0;">Travel Itinerary Generator 🌎</h1>
        </div>
        <div style="margin-top: 8rem;"></div>
    """, unsafe_allow_html=True)

# Configuration from environment variables (no sidebar)
endpoint = "https://hai5014-aa.openai.azure.com/"
api_key = os.environ.get("AZURE_AI_SECRET")
deployment_name = "gpt-4o"
api_version = "2024-12-01-preview"

# Basic validation
if not endpoint or not api_key or not deployment_name:
    st.error("Missing Azure OpenAI configuration. Set AZURE_AI_ENDPOINT, AZURE_AI_SECRET, and AZURE_AI_DEPLOYMENT as environment variables.")
    st.stop()

# Initialize Azure OpenAI client
try:
    client = AzureOpenAI(azure_endpoint=endpoint, api_key=api_key, api_version=api_version)
except Exception as e:
    st.error(f"Failed to initialize AzureOpenAI client: {e}")
    st.stop()


if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": """Purpose: You're a helpful travel assistant. If the user responds in English, assume they are a resident of the US and converse in English. If the user responds in Korean, assume they are a resident of South Korea and converse in Korean. Keep formatting constant regardless of the language. Help the user create a travel itinerary for a 3- or 4-day holiday weekend trip, depending on how many activities they're interested in. Ask questions one at a time.
1. Choose a destination you haven't been to before: Filandia, Colombia; Southern Tunisia; Côn Đảo, Vietnam; Prince Edward Island, Canada; Sibiu, Romania
2. Assume the user has no knowledge of the destination. Introduce what the destination is known for and provide a quick overview of the types of activities available. If you were to travel to this destination, what do you imagine would be your main purpose? (visiting must-see attractions, cultural immersion, culinary exploration, relaxation, etc)
3. Who do you imagine yourself going with?
4. What is your travel style?
5. Suggest 3 first-day itineraries for the user to choose from, considering their answers to the previous questions. Each day should have different activities; highlight how the activities fit the user's preferences. Which day are you most interested in starting your trip with?
6. Are there any adjustments you'd like to make to this day?
7. Guide the user in building the itinerary day by day, while building knowledge on their preferences. Provide 1-day itineraries as options, and ask the user if they want to make any adjustments before moving on to the next day. When the user makes adjustments, provide rational suggestions for subsequent changes based on locations and timing, as well as the user's preferences. Display the full itinerary when presenting the user with new options."""}
    ]


def _extract_response_content(response: Any) -> str:
    # support both SDK response shapes
    try:
        return response.choices[0].message.content
    except Exception:
        try:
            return response["choices"][0]["message"]["content"]
        except Exception:
            return str(response)


# Display chat messages
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])


# Chat input
if prompt := st.chat_input("Say hello and we'll get started!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        try:
            # Stream the response
            for response in client.chat.completions.create(
                messages=st.session_state.messages,
                max_tokens=1024,
                temperature=1.0,
                model=deployment_name,
                stream=True  # Enable streaming
            ):
                try:
                    # Extract the text from the chunk
                    content = response.choices[0].delta.content
                    if content is not None:
                        full_response += content
                        # Update the placeholder with the accumulated response
                        placeholder.markdown(full_response + "▌")
                except Exception:
                    # Fallback for different response shapes
                    try:
                        content = response.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        if content:
                            full_response += content
                            placeholder.markdown(full_response + "▌")
                    except Exception:
                        continue

            # Final update without the cursor
            placeholder.markdown(full_response)
            # Save the full response to message history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Error during API call: {e}")
            try:
                if hasattr(e, "args") and e.args:
                    st.error(f"Detailed error: {e.args[0]}")
            except Exception:
                pass