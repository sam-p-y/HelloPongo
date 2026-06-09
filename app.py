import streamlit as st
import json
from google import genai
from google.genai import types

# 1. Setup the App Interface
st.set_page_config(page_title="Our Kitchen", page_icon="🍳", layout="centered")
st.title("Our Kitchen")

# 2. Securely connect the Gemini VIP Pass
API_KEY = st.secrets.get("GEMINI_API_KEY")
if not API_KEY:
    st.error("API Key missing! Please add it to your Streamlit secrets.")
    st.stop()

client = genai.Client(api_key=API_KEY)

# 3. The Input Section (What you type on Sunday)
with st.expander("📝 Plan This Week", expanded=True):
    meals_needed = st.number_input("Meals Needed", min_value=1, max_value=7, value=4)
    schedule_notes = st.text_area("Schedule Notes", placeholder="e.g., Tuesday 20 mins to cook...")
    inventory = st.text_area("Inventory to Use", placeholder="e.g., Half a bag of rice, cheddar cheese...")
    cravings = st.text_area("Cravings & Goals", placeholder="e.g., Healthy, Tex-Mex, under $100...")
    
    generate_button = st.button("Generate Meals", type="primary", use_container_width=True)

# 4. The Brain (Talking to Gemini)
if generate_button:
    with st.spinner("Chef Gemini is doing the puzzle math..."):
        prompt = f"""
        You are an expert meal planner for a couple in British Columbia. The user needs {meals_needed} meals.
        Schedule Notes: {schedule_notes}
        Inventory: {inventory}
        Cravings: {cravings}
        
        Rules:
        1. Use the Capsule Grocery Strategy to cross-utilize ingredients and minimize waste.
        2. Keep recipes simple (20-50 mins).
        3. Provide direct, high-quality image URLs of the food from real websites (unsplash or recipes).
        
        You MUST output valid JSON matching this exact structure:
        {{
          "meals": [
            {{
              "day": "Monday",
              "name": "Meal Name",
              "time": "30 mins",
              "image_url": "https://example.com/image.jpg",
              "instructions": "1. Step one 2. Step two"
            }}
          ],
          "groceries": [
            {{
              "aisle": "Produce",
              "items": ["2 Yellow Onions", "1 Lime"]
            }}
          ]
        }}
        """
        
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.7
                )
            )
            st.session_state.data = json.loads(response.text)
        except Exception as e:
            st.error(f"There was an error: {e}")

# 5. The Output (The App Screen)
if "data" in st.session_state:
    data = st.session_state.data
    
    st.divider()
    st.header("🍽️ Your Weekly Gallery")
    
    # Builds the visual gallery and instructions
    for meal in data.get("meals", []):
        st.subheader(f"{meal['day']}: {meal['name']}")
        st.caption(f"Prep time: {meal['time']}")
        st.image(meal["image_url"], use_container_width=True)
        with st.expander("View Instructions"):
            st.write(meal["instructions"])
            
    st.divider()
    st.header("🛒 Tap-to-Check Grocery List")
    
    # Builds the tappable checkboxes for the store
    for aisle in data.get("groceries", []):
        st.subheader(aisle["aisle"])
        for item in aisle["items"]:
            # Creates a unique, clickable checkbox for every item
            st.checkbox(item, key=f"{aisle['aisle']}_{item}")
