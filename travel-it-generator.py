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
        <style>
            :root {
                /** define dark mode color variables */
                /** Base colors */
                --clr-dark-a0: #000000;
                --clr-light-a0: #ffffff;

                /** Theme primary colors */
                --clr-primary-a0: #73b702;
                --clr-primary-a10: #85bf35;
                --clr-primary-a20: #95c752;

                /** Theme surface colors */
                --clr-surface-a0: #121212;
                --clr-surface-a10: #282828;
                --clr-surface-a20: #3f3f3f;

                /** Theme tonal surface colors */
                --clr-surface-tonal-a0: #1c2016;
                --clr-surface-tonal-a10: #31352b;
                --clr-surface-tonal-a20: #474b42;
                --clr-surface-tonal-a30: #5f625a;
                --clr-surface-tonal-a40: #777a73;
                --clr-surface-tonal-a50: #91938d;
                --clr-surface-tonal-a60: #abada9;

                /** Success colors */
                --clr-success-a0: #22946e;
                --clr-success-a10: #47d5a6;
                --clr-success-a20: #9ae8ce;

                /** Warning colors */
                --clr-warning-a0: #a87a2a;
                --clr-warning-a10: #d7ac61;
                --clr-warning-a20: #ecd7b2;

                /** Danger colors */
                --clr-danger-a0: #9c2121;
                --clr-danger-a10: #d94a4a;
                --clr-danger-a20: #eb9e9e;

                /** Info colors */
                --clr-info-a0: #21498a;
                --clr-info-a10: #4077d1;
                --clr-info-a20: #92b2e5;
            }
                
            /** style sticky header */
            .header-fixed {
                position: fixed;
                top: 3.5rem;
                left: 0;
                right: 0;
                background-color: var(--clr-light-a0);
                z-index: 999;
                padding: 1rem;
                border-bottom: 1px solid var(--clr-surface-tonal-a60);
            }
            
            .header-fixed h1 {
                margin: 0;
                color: var(--clr-dark-a0);
            }

            /* user avatar color */
            .stChatMessage[data-testid="user-message"] .stChatMessageAvatar {
            background-color: var(--clr-surface-tonal-a40);
            }
            
            .stChatMessage[data-testid="user-message"] .stChatMessageAvatar svg {
                color: var(--clr-light-a0) !important;
            }
            
            /* Alternative approach using CSS selectors */
            div[data-testid="stChatMessageAvatarUser"] {
                background-color: var(--clr-surface-tonal-a40);
            }

            /* chatbot avatar color */
            div[data-testid="stChatMessageAvatarAssistant"] {
                background-color: var(--clr-primary-a0);
            }

            /* input bar border */
            .st-emotion-cache-yd4u6l.exaa2ht1 {
                border: 1px solid var(--clr-primary-a20);
            }
            
            /* dark mode header */
            [data-theme="dark"] .header-fixed,
            .stApp[data-theme="dark"] .header-fixed,
            html[data-theme="dark"] .header-fixed,
            body[data-theme="dark"] .header-fixed {
                background-color: var(--clr-surface-tonal-a20) !important;
                border-bottom: 4px solid var(--clr-surface-tonal-a10);
            }
            
            [data-theme="dark"] .header-fixed h1,
            .stApp[data-theme="dark"] .header-fixed h1,
            html[data-theme="dark"] .header-fixed h1,
            body[data-theme="dark"] .header-fixed h1 {
                color: var(--clr-light-a0) !important;
            }

            /* Lighter gray for user avatar in dark mode */
            [data-theme="dark"] .stChatMessage[data-testid="user-message"] .stChatMessageAvatar,
            .stApp[data-theme="dark"] .stChatMessage[data-testid="user-message"] .stChatMessageAvatar,
            html[data-theme="dark"] .stChatMessage[data-testid="user-message"] .stChatMessageAvatar,
            body[data-theme="dark"] .stChatMessage[data-testid="user-message"] .stChatMessageAvatar,
            [data-theme="dark"] div[data-testid="stChatMessageAvatarUser"],
            .stApp[data-theme="dark"] div[data-testid="stChatMessageAvatarUser"],
            html[data-theme="dark"] div[data-testid="stChatMessageAvatarUser"],
            body[data-theme="dark"] div[data-testid="stChatMessageAvatarUser"] {
                background-color: var(--clr-surface-tonal-a60) !important;
            }

            /* Increase contrast of message input bar in dark mode */
            [data-theme="dark"] .st-emotion-cache-x1bvup.exaa2ht1,
            .stApp[data-theme="dark"] .st-emotion-cache-x1bvup.exaa2ht1,
            html[data-theme="dark"] .st-emotion-cache-x1bvup.exaa2ht1,
            body[data-theme="dark"] .st-emotion-cache-x1bvup.exaa2ht1 {
                background-color: var(--clr-surface-tonal-a20) !important;
                border: 1px solid var(--clr-primary-a0) !important;
            }

            [data-theme="dark"] .st-emotion-cache-x1bvup.exaa2ht1 textarea,
            .stApp[data-theme="dark"] .st-emotion-cache-x1bvup.exaa2ht1 textarea,
            html[data-theme="dark"] .st-emotion-cache-x1bvup.exaa2ht1 textarea,
            body[data-theme="dark"] .st-emotion-cache-x1bvup.exaa2ht1 textarea {
                background-color: var(--clr-surface-tonal-a20) !important;
                color: var(--clr-light-a0) !important;
                border: none !important;
            }
            
            [data-theme="dark"] .st-emotion-cache-x1bvup.exaa2ht1 textarea::placeholder,
            .stApp[data-theme="dark"] .st-emotion-cache-x1bvup.exaa2ht1 textarea::placeholder,
            html[data-theme="dark"] .st-emotion-cache-x1bvup.exaa2ht1 textarea::placeholder,
            body[data-theme="dark"] .st-emotion-cache-x1bvup.exaa2ht1 textarea::placeholder {
                color: var(--clr-surface-tonal-a60) !important;
            }
            
            /* Fallback for system dark mode preference */
            @media (prefers-color-scheme: dark) {
                /* App, header, footer background */
                .header-fixed, .stAppToolbar, .stMainBlockContainer, .stMain, div[data-testid="stBottomBlockContainer"] {
                    background-color: var(--clr-surface-tonal-a0);
                }

                /* Header border */
                .header-fixed {
                    border-bottom: 4px solid var(--clr-surface-tonal-a10);
                }

                .header-fixed h1 {
                    color: var(--clr-light-a0);
                }

                /* user chat message background */
                .stChatMessage:has([data-testid="stChatMessageAvatarUser"]) {
                    background-color: var(--clr-surface-tonal-a10);
                }

                /* user avatar background */
                div[data-testid="stChatMessageAvatarUser"] {
                    background-color: var(--clr-surface-tonal-a60);
                }

                /* chatbot avatar background */
                div[data-testid="stChatMessageAvatarAssistant"] {
                    background-color: var(--clr-primary-a20);
                }

                /* message input bar background div[data-testid="stChatInput"]:first-child */
                .st-emotion-cache-x1bvup.exaa2ht1 {
                    background-color: var(--clr-surface-tonal-a20);
                    border: 1px solid var(--clr-primary-a0);
                }
                textarea[data-testid="stChatInputTextArea"] {
                    background-color: var(--clr-surface-tonal-a20);
                    color: var(--clr-light-a0);
                    border: none;
                }
                textarea[data-testid="stChatInputTextArea"]::placeholder {
                    color: var(--clr-surface-tonal-a60);
                }
            }
            
            /* Override system preference when light mode is explicitly set */
            [data-theme="light"] .header-fixed,
            .stApp[data-theme="light"] .header-fixed {
                background-color: var(--clr-light-a0) !important;
                border-bottom-color: var(--clr-surface-tonal-a60) !important;
            }
            
            [data-theme="light"] .header-fixed h1,
            .stApp[data-theme="light"] .header-fixed h1 {
                color: var(--clr-dark-a0) !important;
            }
        </style>
        <div class="header-fixed">
            <h1>Travel Itinerary Generator 🌎</h1>
        </div>
        <div style="margin-top: 8rem;"></div>
    """, unsafe_allow_html=True)

# Configuration from environment variables (no sidebar)
endpoint = "https://hai5014-aa.openai.azure.com/"
api_key = os.getenv("AZURE_AI_SECRET")
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
        {"role": "system", "content": """You're a helpful travel assistant that converses in the user's language (English OR Korean). You format responses the same regardless of language. You help users create personalized travel itineraries for a 3-day holiday weekend trip by asking the questions below one-by-one without explicitly numbering the steps. You always stay on task if the user provides irrelevant input.
1. Choose a destination you haven't been to before: Filandia, Colombia; Southern Tunisia; Côn Đảo, Vietnam; Prince Edward Island, Canada; Sibiu, Romania
2. Assume the user has no knowledge of the destination. Introduce what the destination is known for and provide a quick overview of the types of activities available. If you were to travel to this destination, what do you imagine would be your main purpose? (visiting must-see attractions, cultural immersion, culinary exploration, relaxation, etc)
3. Who do you imagine yourself going with?
4. What is your travel style?
5. Suggest 3 first-day itineraries for the user to choose from, considering their answers to the previous questions. Each day should have different activities; highlight how the activities fit the user's preferences. Which day are you most interested in starting your trip with?
6. Are there any adjustments you'd like to make to this day?
7. Guide the user in building the itinerary day by day, while building knowledge on their preferences. Provide 1-day itineraries as options, and ask the user if they want to make any adjustments before moving on to the next day. When the user makes adjustments, provide rational suggestions for subsequent changes based on locations and timing, as well as the user's preferences. Display the full itinerary when presenting the user with new options.
8. When the itinerary is complete, inform the user to return to Google Forms to continue the experiment."""}
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
if prompt := st.chat_input("Message Travel Itinerary Assistant"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
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
                break  # Success, exit retry loop
                
            except Exception as e:
                error_message = str(e)
                
                # Check if it's a content filtering error
                if "content management policy" in error_message.lower() or "filtered" in error_message.lower():
                    retry_count += 1
                    
                    if retry_count < max_retries:
                        # Try to rephrase the last user message for better compatibility
                        if len(st.session_state.messages) > 1:
                            # Add a system instruction to be more careful with language
                            modified_messages = st.session_state.messages.copy()
                            modified_messages.append({
                                "role": "system", 
                                "content": "Please respond in a simple, clear manner focusing only on travel planning topics. Avoid any potentially ambiguous language."
                            })
                            
                            # Retry with modified context
                            try:
                                for response in client.chat.completions.create(
                                    messages=modified_messages,
                                    max_tokens=1024,
                                    temperature=0.7,  # Lower temperature for more conservative responses
                                    model=deployment_name,
                                    stream=True
                                ):
                                    try:
                                        content = response.choices[0].delta.content
                                        if content is not None:
                                            full_response += content
                                            placeholder.markdown(full_response + "▌")
                                    except Exception:
                                        try:
                                            content = response.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                            if content:
                                                full_response += content
                                                placeholder.markdown(full_response + "▌")
                                        except Exception:
                                            continue
                                
                                placeholder.markdown(full_response)
                                st.session_state.messages.append({"role": "assistant", "content": full_response})
                                break
                                
                            except Exception:
                                continue  # Try again with different approach
                        else:
                            continue
                    else:
                        # Final fallback response
                        fallback_response = """I apologize, but I'm having trouble processing your request right now. Let me help you with your travel planning in a different way. 

Could you please tell me which destination you'd like to explore from these options:
- Filandia, Colombia
- Southern Tunisia  
- Côn Đảo, Vietnam
- Prince Edward Island, Canada
- Sibiu, Romania

Please choose one and I'll provide information about what makes it special!
죄송합니다만, 현재 귀하의 요청을 처리하는 데 어려움을 겪고 있습니다. 다른 방법으로 여행 계획을 도와드리겠습니다.

다음 옵션 중 탐험하고 싶은 목적지를 알려주시겠어요?
- 콜롬비아 필란디아
- 튀니지 남부
- 베트남 콘다오
- 캐나다 프린스에드워드아일랜드
- 루마니아 시비우

하나를 선택해 주시면 그곳의 특별한 매력에 대한 정보를 제공해 드리겠습니다!"""
                        
                        placeholder.markdown(fallback_response)
                        st.session_state.messages.append({"role": "assistant", "content": fallback_response})
                        break
                else:
                    # For non-content-filtering errors, show the original error handling
                    st.error(f"Error during API call: {e}")
                    try:
                        if hasattr(e, "args") and e.args:
                            st.error(f"Detailed error: {e.args[0]}")
                    except Exception:
                        pass
                    break